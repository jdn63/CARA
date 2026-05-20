"""
Mpox Surveillance (Shape A outbreak flag)

Lightweight tiered outbreak flag for mpox (formerly monkeypox) that
nudges the infectious_disease Acute signal. See
utils/disease_surveillance.py for the dispatch and stacking rule.

Tiers (configurable in config/risk_weights.yaml ->
disease_alert_thresholds.mpox):
    baseline  - no elevated activity in WI
    elevated  - WI 4-week case count above elevated_threshold_cases
    cluster   - WI cluster_threshold_cases or more in 4 weeks,
                OR clade I detection reported in WI

Data source (best-effort; verify endpoint when deployed):
    - CDC Mpox cases by State of Residence (Socrata)
      https://data.cdc.gov/resource/usqr-pmk5.json
      (If this dataset ID changes, update CDC_MPOX_ENDPOINT below;
      the fetcher degrades to "baseline" on HTTP error.)

Granularity: statewide Wisconsin per design decision (#2).

Cache-only invariant: request-path callers must never trigger live HTTP.
Live fetches occur exclusively in the scheduler job refresh_all_mpox.
"""

from __future__ import annotations

import logging
import requests
from datetime import datetime, timezone
from typing import Any, Dict, List

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

CACHE_KEY = "mpox_surveillance_v1"
CACHE_DAYS = 7
HTTP_TIMEOUT = 20
_UA = "CARA-WI-PublicHealth/1.0 (contact: github.com/jdn63)"

CDC_MPOX_ENDPOINT = "https://data.cdc.gov/resource/usqr-pmk5.json"

_DEFAULT_THRESHOLDS = {
    "elevated_threshold_4wk_cases": 3,
    "cluster_threshold_4wk_cases": 5,
    "tier_boosts": {"baseline": 0.0, "elevated": 0.15, "cluster": 0.30},
}


def _thresholds() -> Dict[str, Any]:
    out = {
        "elevated_threshold_4wk_cases": _DEFAULT_THRESHOLDS["elevated_threshold_4wk_cases"],
        "cluster_threshold_4wk_cases": _DEFAULT_THRESHOLDS["cluster_threshold_4wk_cases"],
        "tier_boosts": dict(_DEFAULT_THRESHOLDS["tier_boosts"]),
    }
    try:
        from utils.config_manager import get_config_manager
        cfg = get_config_manager().config or {}
        block = (cfg.get("disease_alert_thresholds") or {}).get("mpox") or {}
        for k in ("elevated_threshold_4wk_cases", "cluster_threshold_4wk_cases"):
            v = block.get(k)
            if isinstance(v, (int, float)) and v >= 0:
                out[k] = int(v)
        boosts = block.get("tier_boosts") or {}
        for k in out["tier_boosts"]:
            v = boosts.get(k)
            if isinstance(v, (int, float)) and 0.0 <= float(v) <= 0.40:
                out["tier_boosts"][k] = float(v)
    except Exception as exc:
        logger.warning(f"mpox thresholds: config unavailable, using defaults ({exc})")
    return out


def fetch_mpox_surveillance() -> Dict[str, Any]:
    """Live fetch of mpox state-level case counts. Called only by scheduler."""
    cached = get_from_persistent_cache(CACHE_KEY, max_age_days=CACHE_DAYS)
    if cached:
        logger.info(f"Mpox surveillance loaded from cache (tier={cached.get('tier')})")
        return cached

    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("mpox")
        return _fallback()

    thr = _thresholds()
    wi_recent_4wk = 0
    us_recent_4wk = 0
    fetch_errors: List[str] = []

    try:
        r = requests.get(
            CDC_MPOX_ENDPOINT,
            params={"$limit": 50000},
            timeout=HTTP_TIMEOUT,
            headers={"User-Agent": _UA, "Accept": "application/json"},
        )
        if r.status_code != 200:
            fetch_errors.append(f"HTTP {r.status_code}")
        else:
            rows = r.json() if r.content else []
            if not isinstance(rows, list):
                fetch_errors.append("unexpected response shape")
                rows = []
            # Heuristic: locate the most recent 4 weekly rows for WI.
            # CDC mpox dataset column names have changed over time; check
            # several common spellings before giving up.
            state_keys = ("state", "state_of_residence", "jurisdiction", "us_jurisdiction")
            case_keys = ("cases", "weekly_cases", "case_count", "new_cases", "n_cases")
            wi_rows: List[Dict[str, Any]] = []
            for row in rows:
                state_val = ""
                for sk in state_keys:
                    if sk in row and row[sk]:
                        state_val = str(row[sk]).strip().lower()
                        break
                if state_val in ("wi", "wisconsin"):
                    wi_rows.append(row)
            # Sort by any date-like field descending, take last 4
            def _date_key(row: Dict[str, Any]) -> str:
                for dk in ("week_ending", "report_date", "date", "mmwr_week"):
                    if dk in row and row[dk]:
                        return str(row[dk])
                return ""
            wi_rows.sort(key=_date_key, reverse=True)
            for row in wi_rows[:4]:
                for ck in case_keys:
                    if ck in row and row[ck] is not None:
                        try:
                            wi_recent_4wk += int(float(row[ck]))
                        except (TypeError, ValueError):
                            pass
                        break
            us_recent_4wk = sum(
                int(float(r2.get(ck, 0) or 0))
                for r2 in rows[:200]
                for ck in case_keys if ck in r2
            ) if rows else 0
    except Exception as exc:
        fetch_errors.append(str(exc))
        logger.warning(f"Mpox fetch failed: {exc}")

    # Tier determination - clade I detection is a forward-looking placeholder;
    # CDC does not yet publish a structured WI clade I flag, so v1 sets it
    # to False and relies on the count thresholds.
    clade_i_detected = False
    if wi_recent_4wk >= thr["cluster_threshold_4wk_cases"] or clade_i_detected:
        tier = "cluster"
    elif wi_recent_4wk >= thr["elevated_threshold_4wk_cases"]:
        tier = "elevated"
    else:
        tier = "baseline"

    boosts = thr["tier_boosts"]
    detail = (
        f"WI 4-week mpox cases: {wi_recent_4wk} "
        f"(elevated threshold {thr['elevated_threshold_4wk_cases']}, "
        f"cluster threshold {thr['cluster_threshold_4wk_cases']})"
    )
    if fetch_errors:
        detail += f"; fetch issues: {'; '.join(fetch_errors)}"

    result = {
        "tier": tier,
        "boost": boosts.get(tier, 0.0),
        "wi_recent_4wk_cases": wi_recent_4wk,
        "us_recent_4wk_cases_sample": us_recent_4wk,
        "elevated_threshold": thr["elevated_threshold_4wk_cases"],
        "cluster_threshold": thr["cluster_threshold_4wk_cases"],
        "clade_i_detected": clade_i_detected,
        "source": "cdc_mpox",
        "source_label": "CDC Mpox cases by State of Residence",
        "source_url": "https://www.cdc.gov/mpox/situation-summary/index.html",
        "detail": detail,
        "signal_scope": "statewide_wisconsin",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "fetch_errors": fetch_errors,
    }
    set_in_persistent_cache(CACHE_KEY, result, expiry_days=CACHE_DAYS)
    logger.info(f"Mpox fetched: tier={tier}, wi_4wk={wi_recent_4wk}")
    return result


def _fallback() -> Dict[str, Any]:
    thr = _thresholds()
    return {
        "tier": "baseline",
        "boost": 0.0,
        "wi_recent_4wk_cases": 0,
        "us_recent_4wk_cases_sample": 0,
        "elevated_threshold": thr["elevated_threshold_4wk_cases"],
        "cluster_threshold": thr["cluster_threshold_4wk_cases"],
        "clade_i_detected": False,
        "source": "unavailable",
        "source_label": "CDC Mpox (cache unavailable)",
        "source_url": "https://www.cdc.gov/mpox/situation-summary/index.html",
        "detail": "Data unavailable - awaiting scheduler refresh",
        "signal_scope": "statewide_wisconsin",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "fetch_errors": [],
    }


def get_mpox_outbreak_flags() -> Dict[str, Any]:
    """Stable accessor for the dispatch in utils/disease_surveillance.py."""
    try:
        return fetch_mpox_surveillance()
    except Exception as exc:
        logger.error(f"get_mpox_outbreak_flags failed: {exc}")
        return _fallback()
