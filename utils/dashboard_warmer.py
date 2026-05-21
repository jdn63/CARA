"""Dashboard cache warmer.

Background daemon that pre-builds the per-jurisdiction dashboard
context cache (`dashboard_full_v6_<discipline>_<jid>`) so the first
user click on /dashboard/<jid> or /em-dashboard/<slug> hits a warm
cache instead of paying the 1-15 second cold-compute cost.

Why: process_risk_data() + the 7 TemporalRiskComponent calculations
+ predictive analysis cost varies by jurisdiction size. Milwaukee
County (id 41) takes ~14s cold; smaller counties take ~1-3s cold.
After warm, both the PH and EM variants serve in ~12ms because the
fully-rendered context is in the v6 persistent cache.

The persistent cache has a 1-day TTL (max_age_days=1 in
routes/dashboard.py). After a gunicorn auto-reload, code stays the
same but the in-process Python caches reset; persistent-cache files
on disk survive. So the warmer is mostly important on first deploy
after a v6 bump (which invalidated v5 entries) and on the first
boot of a long-lived deployment.

The warmer runs only on the primary gunicorn worker (same guard as
the data-refresh scheduler) so we never run 84+72 dashboard
computations N times in parallel across workers.

Cache-only invariant: each warm call goes through routes.dashboard
which already wraps fetchers in cache_only_context() once
process_risk_data() returns. The warmer does not introduce any new
request-path live HTTP. If a source's underlying cache is cold, the
warmer's dashboard render just embeds the fetcher's existing
fallback payload, exactly as a real user hit would.
"""

import logging
import threading
import time
from typing import List, Tuple

from utils.persistent_cache import get_from_persistent_cache


logger = logging.getLogger(__name__)


# Largest counties first so the user's most likely click lands on a
# warm cache the fastest. Order is by 2020 Census population.
_PRIORITY_COUNTIES = [
    'Milwaukee', 'Dane', 'Waukesha', 'Brown', 'Racine', 'Outagamie',
    'Winnebago', 'Kenosha', 'Rock', 'Marathon', 'Washington',
    'La Crosse', 'Eau Claire', 'Sheboygan', 'Walworth', 'Fond du Lac',
    'Dodge', 'Ozaukee', 'St. Croix', 'Jefferson',
]


def _prioritized_county_order(counties: List[dict]) -> List[dict]:
    by_name = {c['name']: c for c in counties}
    priority_first: List[dict] = []
    for name in _PRIORITY_COUNTIES:
        if name in by_name:
            priority_first.append(by_name.pop(name))
    rest = sorted(by_name.values(), key=lambda c: c['name'])
    return priority_first + rest


def _is_already_warm(jurisdiction_id: str, discipline: str) -> bool:
    """Mirror the dashboard view's cache lookup so we skip work that
    a previous warmer pass (or a real user hit) already did."""
    key = f"dashboard_full_v6_{discipline}_{jurisdiction_id}"
    try:
        return get_from_persistent_cache(key, max_age_days=1) is not None
    except Exception:
        return False


def _warm_one(client, url: str, label: str) -> Tuple[bool, float]:
    """Issue a GET against the test client and return (ok, seconds)."""
    started = time.monotonic()
    try:
        resp = client.get(url)
        duration = time.monotonic() - started
        if resp.status_code == 200:
            return True, duration
        logger.warning(
            f"Dashboard warmer: {label} returned HTTP {resp.status_code} "
            f"after {duration:.1f}s"
        )
        return False, duration
    except Exception as e:
        duration = time.monotonic() - started
        logger.warning(
            f"Dashboard warmer: {label} failed after {duration:.1f}s: {e}"
        )
        return False, duration


def _warm_all(app, delay_seconds: int) -> None:
    """Body of the daemon thread. Warms PH (84 LHDs) then EM (72
    counties), in priority order, skipping anything that already has
    a v6 cache entry."""
    try:
        time.sleep(delay_seconds)
    except Exception:
        pass

    try:
        from utils.data_processor import get_wi_jurisdictions
        from utils.em_counties import get_wi_counties_for_em
    except Exception as e:
        logger.error(f"Dashboard warmer: import failed, aborting: {e}")
        return

    try:
        ph_jurisdictions = get_wi_jurisdictions() or []
    except Exception as e:
        logger.error(f"Dashboard warmer: could not load PH jurisdictions: {e}")
        ph_jurisdictions = []

    try:
        em_counties = _prioritized_county_order(get_wi_counties_for_em() or [])
    except Exception as e:
        logger.error(f"Dashboard warmer: could not load EM counties: {e}")
        em_counties = []

    client = app.test_client()
    started_all = time.monotonic()
    ph_warmed = ph_skipped = ph_failed = 0
    em_warmed = em_skipped = em_failed = 0

    logger.info(
        f"Dashboard warmer starting: {len(ph_jurisdictions)} PH "
        f"jurisdictions + {len(em_counties)} EM counties"
    )

    for j in ph_jurisdictions:
        jid = str(j.get('id', ''))
        if not jid or jid.startswith('T'):
            ph_skipped += 1
            continue
        if _is_already_warm(jid, 'public_health'):
            ph_skipped += 1
            continue
        ok, dur = _warm_one(
            client,
            f"/dashboard/{jid}?discipline=public_health",
            f"PH /dashboard/{jid}",
        )
        if ok:
            ph_warmed += 1
            logger.debug(f"Dashboard warmer: PH {jid} warmed in {dur:.1f}s")
        else:
            ph_failed += 1

    for c in em_counties:
        slug = c.get('id', '')
        jid = str(c.get('jurisdiction_id', ''))
        if not slug or not jid:
            em_skipped += 1
            continue
        if _is_already_warm(jid, 'em'):
            em_skipped += 1
            continue
        ok, dur = _warm_one(
            client,
            f"/em-dashboard/{slug}",
            f"EM /em-dashboard/{slug}",
        )
        if ok:
            em_warmed += 1
            logger.debug(f"Dashboard warmer: EM {slug} warmed in {dur:.1f}s")
        else:
            em_failed += 1

    elapsed = time.monotonic() - started_all
    logger.info(
        f"Dashboard warmer complete in {elapsed:.0f}s: "
        f"PH warmed={ph_warmed} skipped={ph_skipped} failed={ph_failed}; "
        f"EM warmed={em_warmed} skipped={em_skipped} failed={em_failed}"
    )


def start_dashboard_warmer(app, delay_seconds: int = 25) -> None:
    """Start the dashboard cache warmer in a daemon thread. Safe to
    call from create_app() on the primary gunicorn worker. The delay
    lets the app finish booting (scheduler also starts at +10s) before
    we begin issuing internal requests."""
    t = threading.Thread(
        target=_warm_all,
        args=(app, delay_seconds),
        name='dashboard-warmer',
        daemon=True,
    )
    t.start()
    logger.info(
        f"Dashboard warmer scheduled to start in {delay_seconds}s "
        f"(primary worker only)"
    )
