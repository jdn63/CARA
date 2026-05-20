"""
Request-context flags for the user-facing assessment path.

Purpose
-------
CARA's architectural guarantee is that no external HTTP call occurs
during a user dashboard request. All external data is pre-fetched by
scheduled background jobs (utils/data_source_refresher.py) and stored
in the persistent cache or PostgreSQL. The dashboard render must read
exclusively from cache.

A code review on 2026-05-19 found that several fetchers reachable
from routes/dashboard.py would fall back to a live `requests.get` if
the persistent cache was empty (cold deploy, expired cache, scheduler
outage). This module provides the enforcement mechanism that prevents
that fallback.

Mechanism
---------
A thread-local boolean `cache_only` is set to True by the
`cache_only_context()` context manager. Request-path entry points
(currently process_risk_data) wrap their body in this context.
Every fetcher that performs external HTTP must, after its cache
lookup and BEFORE its `requests.get` call, check
`is_cache_only_mode()` and short-circuit to its existing fallback
payload if True.

Scheduler jobs never enter this context, so they continue to fetch
live data normally.

Telemetry
---------
Each blocked fetch is counted on the thread-local `blocked_fetches`
list so callers can log or surface "N live fetches were prevented
during this request" diagnostics. This list is reset on each context
entry.
"""

from __future__ import annotations

import logging
import threading
from contextlib import contextmanager
from typing import Iterator, List

logger = logging.getLogger(__name__)

_state = threading.local()


def is_cache_only_mode() -> bool:
    """Return True iff the current thread is inside a cache_only_context()."""
    return bool(getattr(_state, "cache_only", False))


def record_blocked_fetch(source_label: str) -> None:
    """
    Record that a fetcher short-circuited a live fetch because the
    thread is in cache-only mode. Safe to call when not in context
    (no-op outside cache_only_context).

    The `source_label` is canonicalized through utils.source_registry
    so that telemetry labels converge on the canonical IDs even when
    the calling fetcher still passes a legacy name. Labels may include
    a `:param` suffix (e.g. 'airnow:dane') to identify a specific
    instance; only the prefix before the colon is canonicalized.
    """
    bucket: List[str] = getattr(_state, "blocked_fetches", None)  # type: ignore[assignment]
    if bucket is None:
        return

    # Local import to avoid a hard cycle at import time: source_registry
    # is loaded lazily so that request_context stays usable even if the
    # registry itself fails to import for some reason.
    try:
        from utils.source_registry import canonicalize as _canonicalize
        base, _, suffix = source_label.partition(":")
        canonical_base = _canonicalize(base)
        if canonical_base is not None and canonical_base != base:
            source_label = (
                f"{canonical_base}:{suffix}" if suffix else canonical_base
            )
    except ImportError:
        pass

    bucket.append(source_label)
    logger.warning(
        f"[cache_only_mode] Blocked live fetch for '{source_label}' in "
        "request path - persistent cache was empty. The scheduler must "
        "warm this cache; the dashboard will use a fallback payload."
    )


def get_blocked_fetches() -> List[str]:
    """Return a copy of the blocked-fetch labels recorded so far."""
    bucket: List[str] = getattr(_state, "blocked_fetches", None) or []  # type: ignore[assignment]
    return list(bucket)


@contextmanager
def cache_only_context(label: str = "request") -> Iterator[List[str]]:
    """
    Enter cache-only mode for the duration of the block.

    While inside, any fetcher that calls `is_cache_only_mode()` will
    see True and is expected to skip its `requests.get` and return a
    fallback payload instead.

    Yields the (initially empty) blocked-fetches list so the caller
    can inspect it after the block to log telemetry or attach it to
    response provenance.

    Nested entries are safe: the previous cache_only state and the
    previous blocked_fetches bucket are restored on exit.
    """
    prev_flag = getattr(_state, "cache_only", False)
    prev_bucket = getattr(_state, "blocked_fetches", None)
    new_bucket: List[str] = []
    _state.cache_only = True
    _state.blocked_fetches = new_bucket
    logger.debug(
        f"[cache_only_mode] ENTER ({label}); live HTTP from request "
        "path is now blocked."
    )
    try:
        yield new_bucket
    finally:
        _state.cache_only = prev_flag
        _state.blocked_fetches = prev_bucket
        if new_bucket:
            logger.info(
                f"[cache_only_mode] EXIT ({label}); blocked "
                f"{len(new_bucket)} live fetch(es): {new_bucket}"
            )
        else:
            logger.debug(f"[cache_only_mode] EXIT ({label}); no live fetches blocked.")
