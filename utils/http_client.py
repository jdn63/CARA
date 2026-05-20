"""
Shared resilient HTTP wrapper for CARA external-source fetchers.

Closes review finding M2 (2026-05-20). The three CDC Socrata fetchers
(utils/nssp_respiratory, utils/nhsn_hospital, utils/nndss_communicable)
previously each made a single-shot `requests.get(...)` call with no
retry, no backoff, and no protection against a flapping upstream. A
brief CDC 5xx burst would empty the cache and surface a fallback
payload on the next scheduler tick.

This module provides:

  fetch_json(source_id, url, params=None, headers=None, timeout=20,
             max_retries=3, base_backoff_seconds=0.5)
      Bounded exponential backoff with full jitter on transient errors
      (429, 502, 503, 504, ConnectionError, Timeout). Respects a
      Retry-After header when present on 429/503. Honors a per-source
      circuit breaker so a sick upstream is not hammered.

Circuit breaker (per source_id):
  - CLOSED: normal traffic; transient failures are retried in-place.
  - OPEN: after N consecutive top-level failures, the breaker opens
    for COOLDOWN_SECONDS. Subsequent calls short-circuit with
    CircuitOpenError without touching the network.
  - HALF_OPEN: after the cooldown, the next call is allowed through
    as a probe. Success closes the breaker; failure re-opens it for
    another cooldown.

Cache-only mode (utils.request_context.is_cache_only_mode) is NOT
checked here; callers must check it before invoking fetch_json so the
cache-only architectural guarantee is preserved at the call site (see
replit.md, Cache-only request path).
"""

import logging
import random
import threading
import time
from typing import Any, Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "CARA-WI-PublicHealth/1.0 (contact: github.com/jdn63)"

_RETRYABLE_STATUS = frozenset({429, 502, 503, 504})

BREAKER_FAILURE_THRESHOLD = 4
BREAKER_COOLDOWN_SECONDS = 300

_BREAKER_LOCK = threading.Lock()
_BREAKER_STATE: Dict[str, Dict[str, Any]] = {}


class CircuitOpenError(RuntimeError):
    """Raised when a per-source circuit breaker is OPEN and refusing traffic."""

    def __init__(self, source_id: str, retry_after_seconds: float):
        super().__init__(
            f"Circuit breaker OPEN for source '{source_id}'; "
            f"refusing traffic for another {retry_after_seconds:.0f}s"
        )
        self.source_id = source_id
        self.retry_after_seconds = retry_after_seconds


def _breaker_state(source_id: str) -> Dict[str, Any]:
    state = _BREAKER_STATE.get(source_id)
    if state is None:
        state = {
            'state': 'CLOSED',
            'consecutive_failures': 0,
            'opened_at': 0.0,
            'probe_in_flight': False,
        }
        _BREAKER_STATE[source_id] = state
    return state


def _breaker_check(source_id: str) -> None:
    """Reserve permission to call the upstream for source_id.

    State machine (per source):
      - CLOSED: always allowed through.
      - OPEN:
          - if the cooldown has NOT elapsed, raise CircuitOpenError.
          - if the cooldown HAS elapsed, transition to HALF_OPEN and
            mark `probe_in_flight=True` for THIS caller. The very
            first caller after cooldown gets the single probe slot.
      - HALF_OPEN:
          - if a probe is already in flight (another caller already
            took the slot), raise CircuitOpenError so concurrent
            callers do not pile onto a still-sick upstream.
          - if no probe is in flight (e.g. the probing thread was
            killed), grant a fresh probe slot.

    The probe slot is released by `_breaker_record_success` or
    `_breaker_record_failure`, which together cover every code path
    out of `fetch_json`.
    """
    with _BREAKER_LOCK:
        st = _breaker_state(source_id)
        cur = st['state']
        if cur == 'CLOSED':
            return
        if cur == 'OPEN':
            elapsed = time.monotonic() - st['opened_at']
            remaining = BREAKER_COOLDOWN_SECONDS - elapsed
            if remaining > 0:
                raise CircuitOpenError(source_id, remaining)
            st['state'] = 'HALF_OPEN'
            st['probe_in_flight'] = True
            logger.info(
                f"HTTP breaker [{source_id}] HALF_OPEN after "
                f"{BREAKER_COOLDOWN_SECONDS}s cooldown; granting "
                f"single-flight probe"
            )
            return
        # HALF_OPEN
        if st['probe_in_flight']:
            raise CircuitOpenError(source_id, BREAKER_COOLDOWN_SECONDS)
        st['probe_in_flight'] = True
        return


def _breaker_record_success(source_id: str) -> None:
    with _BREAKER_LOCK:
        st = _breaker_state(source_id)
        if st['state'] != 'CLOSED' or st['consecutive_failures'] > 0:
            logger.info(
                f"HTTP breaker [{source_id}] CLOSED after success "
                f"(was {st['state']}, prior failures="
                f"{st['consecutive_failures']})"
            )
        st['state'] = 'CLOSED'
        st['consecutive_failures'] = 0
        st['opened_at'] = 0.0
        st['probe_in_flight'] = False


def _breaker_record_failure(source_id: str) -> None:
    with _BREAKER_LOCK:
        st = _breaker_state(source_id)
        st['consecutive_failures'] += 1
        was_half_open = st['state'] == 'HALF_OPEN'
        st['probe_in_flight'] = False
        if (was_half_open
                or st['consecutive_failures'] >= BREAKER_FAILURE_THRESHOLD):
            st['state'] = 'OPEN'
            st['opened_at'] = time.monotonic()
            logger.warning(
                f"HTTP breaker [{source_id}] OPEN for "
                f"{BREAKER_COOLDOWN_SECONDS}s after "
                f"{st['consecutive_failures']} consecutive failures"
                f"{' (failed HALF_OPEN probe)' if was_half_open else ''}"
            )


def reset_breaker(source_id: str) -> None:
    """Test/admin hook to clear a breaker's state."""
    with _BREAKER_LOCK:
        _BREAKER_STATE.pop(source_id, None)


def get_breaker_snapshot() -> Dict[str, Dict[str, Any]]:
    """Return a copy of all breaker state for diagnostics."""
    with _BREAKER_LOCK:
        return {k: dict(v) for k, v in _BREAKER_STATE.items()}


def _compute_backoff(attempt: int,
                     base: float,
                     retry_after_header: Optional[str]) -> float:
    """Bounded exponential backoff with full jitter.

    attempt is 0-indexed. If the server sent Retry-After (seconds), honor
    it (capped at 60s) instead of the computed backoff.
    """
    if retry_after_header:
        try:
            ra = float(retry_after_header)
            if ra > 0:
                return min(ra, 60.0)
        except (TypeError, ValueError):
            pass
    cap = min(base * (2 ** attempt), 30.0)
    return random.uniform(0.0, cap)


def fetch_json(source_id: str,
               url: str,
               params: Optional[Dict[str, Any]] = None,
               headers: Optional[Dict[str, str]] = None,
               timeout: int = 20,
               max_retries: int = 3,
               base_backoff_seconds: float = 0.5) -> Any:
    """Fetch JSON from `url` with bounded retry + jitter + circuit breaker.

    Args:
        source_id: stable identifier used for breaker state and logs
            (e.g. 'cdc_nssp', 'cdc_nhsn', 'cdc_nndss').
        url: absolute URL.
        params: query params dict.
        headers: extra headers (merged on top of the default User-Agent).
        timeout: per-attempt timeout in seconds.
        max_retries: number of retry attempts after the first try. The
            total number of network calls is `1 + max_retries`.
        base_backoff_seconds: initial backoff before full-jitter.

    Returns:
        Parsed JSON (dict or list) from the upstream response.

    Raises:
        CircuitOpenError if the breaker for source_id is OPEN.
        requests.HTTPError on non-retryable HTTP failure or after
            retries are exhausted.
        requests.RequestException on a transport-level failure after
            retries are exhausted.
    """
    _breaker_check(source_id)

    merged_headers = {'User-Agent': DEFAULT_USER_AGENT}
    if headers:
        merged_headers.update(headers)

    last_exc: Optional[BaseException] = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(
                url,
                params=params,
                headers=merged_headers,
                timeout=timeout,
            )
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            sleep_for = _compute_backoff(attempt, base_backoff_seconds, None)
            logger.warning(
                f"HTTP [{source_id}] transport error "
                f"({type(exc).__name__}) attempt {attempt + 1}/"
                f"{max_retries + 1}; retrying in {sleep_for:.2f}s"
            )
            time.sleep(sleep_for)
            continue

        status = resp.status_code
        if status in _RETRYABLE_STATUS and attempt < max_retries:
            sleep_for = _compute_backoff(
                attempt, base_backoff_seconds,
                resp.headers.get('Retry-After'),
            )
            logger.warning(
                f"HTTP [{source_id}] status {status} "
                f"attempt {attempt + 1}/{max_retries + 1}; "
                f"retrying in {sleep_for:.2f}s"
            )
            time.sleep(sleep_for)
            continue

        # Either a 2xx, a non-retryable 4xx, or a retryable 5xx with
        # no retries left: let raise_for_status decide.
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            _breaker_record_failure(source_id)
            raise
        try:
            payload = resp.json()
        except ValueError as exc:
            _breaker_record_failure(source_id)
            raise requests.RequestException(
                f"HTTP [{source_id}] non-JSON response from {url}: {exc}"
            ) from exc

        _breaker_record_success(source_id)
        return payload

    _breaker_record_failure(source_id)
    assert last_exc is not None
    raise last_exc
