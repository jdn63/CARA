"""
H5N1 Avian Influenza Surveillance (Shape A outbreak flag)

Lightweight tiered outbreak flag for highly pathogenic avian influenza
(H5N1) that nudges the infectious_disease Acute signal. See
utils/disease_surveillance.py for the dispatch and stacking rule.

Tiers (configurable in config/risk_weights.yaml ->
disease_alert_thresholds.h5n1):
    none           - no signal
    national_only  - US detections somewhere, no WI detection in 90 days
    state          - WI livestock or poultry detection in last 90 days,
                     OR any confirmed human case in WI
    local          - placeholder for future county-level escalation;
                     v1 statewide-only per design decision

Data sources (best-effort; verify endpoints when deployed):
    - USDA APHIS HPAI Livestock Detections (public CSV/JSON)
      https://www.aphis.usda.gov/livestock-poultry-disease/avian/
        avian-influenza/hpai-detections/livestock
    - USDA APHIS HPAI Commercial Poultry Detections (public CSV)
      https://www.aphis.usda.gov/livestock-poultry-disease/avian/
        avian-influenza/hpai-detections/commercial-backyard-flocks
    - CDC H5 Bird Flu Current Situation Summary (state human-case table)
      https://www.cdc.gov/bird-flu/situation-summary/index.html

Granularity: statewide Wisconsin. Per design decision (#2), county-level
specificity is deferred until a reliable per-county data feed is wired.

Cache-only invariant: request-path callers must never trigger live HTTP.
See utils/request_context.py. Live fetches occur exclusively in the
scheduler job refresh_all_h5n1 in utils/data_source_refresher.py.
"""

from __future__ import annotations

import csv
import io
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

CACHE_KEY = "h5n1_surveillance_v1"
CACHE_DAYS = 7
HTTP_TIMEOUT = 20
_UA = "CARA-WI-PublicHealth/1.0 (contact: github.com/jdn63)"

# Best-effort source URLs. APHIS occasionally re-paths these CSVs; the
# fetcher degrades to "no_signal" if a URL 404s, and the scheduler logs
# the failure so the maintainer can update the constant.
APHIS_LIVESTOCK_CSV = (
    "https://www.aphis.usda.gov/sites/default/files/"
    "hpai-livestock-detections.csv"
)
APHIS_POULTRY_CSV = (
    "https://www.aphis.usda.gov/sites/default/files/"
    "hpai-commercial-backyard-flocks.csv"
)

_DEFAULT_TIER_BOOSTS = {
    "none": 0.0,
    "national_only": 0.05,
    "state": 0.15,
    "local": 0.30,
}


def _tier_boosts() -> Dict[str, float]:
    """Read tier->boost map from config/risk_weights.yaml, with defaults."""
    out = dict(_DEFAULT_TIER_BOOSTS)
    try:
        from utils.config_manager import get_config_manager
        cfg = get_config_manager().config or {}
        block = (cfg.get("disease_alert_thresholds") or {}).get("h5n1") or {}
        boosts = block.get("tier_boosts") or {}
        for k in out:
            v = boosts.get(k)
            if isinstance(v, (int, float)) and 0.0 <= float(v) <= 0.40:
                out[k] = float(v)
    except Exception as exc:
        logger.warning(f"H5N1 tier_boosts: config unavailable, using defaults ({exc})")
    return out


def _parse_csv_rows(text: str) -> List[Dict[str, str]]:
    try:
        return list(csv.DictReader(io.StringIO(text)))
    except Exception as exc:
        logger.warning(f"H5N1: CSV parse failed: {exc}")
        return []


def _filter_wi_recent(rows: List[Dict[str, str]], days: int = 90) -> List[Dict[str, str]]:
    """Filter rows for Wisconsin + recent date. Best-effort column matching."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    for row in rows:
        state = (
            row.get("State")
            or row.get("state")
            or row.get("STATE")
            or ""
        ).strip().lower()
        if state not in ("wi", "wisconsin"):
            continue
        date_str = (
            row.get("Outbreak Date")
            or row.get("Confirmed Date")
            or row.get("Date Detected")
            or row.get("Date")
            or ""
        ).strip()
        if date_str:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%b-%Y"):
                try:
                    dt = datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
                    if dt >= cutoff:
                        out.append(row)
                    break
                except ValueError:
                    continue
        else:
            # No usable date; include conservatively so the flag is not silently dropped
            out.append(row)
    return out


def fetch_h5n1_surveillance() -> Dict[str, Any]:
    """
    Live fetch of H5N1 surveillance signals. Called only by the scheduler.

    Returns the cached result if still fresh. Otherwise hits USDA APHIS
    livestock + poultry CSVs and derives the tier. Human-case counts are
    not pulled from a structured CDC feed in v1 (the CDC situation
    summary is an HTML table without a stable API endpoint); the
    wi_human_cases_ytd field is reserved for a future fetcher and
    currently reports None.
    """
    cached = get_from_persistent_cache(CACHE_KEY, max_age_days=CACHE_DAYS)
    if cached:
        logger.info(f"H5N1 surveillance loaded from cache (tier={cached.get('tier')})")
        return cached

    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("h5n1")
        return _fallback()

    wi_livestock = 0
    wi_poultry = 0
    us_livestock_total = 0
    fetch_errors: List[str] = []

    for url, kind in ((APHIS_LIVESTOCK_CSV, "livestock"), (APHIS_POULTRY_CSV, "poultry")):
        try:
            r = requests.get(url, timeout=HTTP_TIMEOUT, headers={"User-Agent": _UA})
            if r.status_code != 200:
                fetch_errors.append(f"{kind}: HTTP {r.status_code}")
                continue
            rows = _parse_csv_rows(r.text)
            wi_rows = _filter_wi_recent(rows, days=90)
            if kind == "livestock":
                wi_livestock = len(wi_rows)
                us_livestock_total = len(rows)
            else:
                wi_poultry = len(wi_rows)
        except Exception as exc:
            fetch_errors.append(f"{kind}: {exc}")
            logger.warning(f"H5N1 fetch {kind} failed: {exc}")

    # Determine tier
    if wi_livestock > 0 or wi_poultry > 0:
        tier = "state"
        detail = (
            f"WI HPAI detections in last 90 days: "
            f"{wi_livestock} livestock, {wi_poultry} poultry"
        )
    elif us_livestock_total > 0:
        tier = "national_only"
        detail = f"US livestock HPAI detections present ({us_livestock_total}); no WI detection in last 90 days"
    elif fetch_errors:
        tier = "none"
        detail = f"Data unavailable: {'; '.join(fetch_errors)}"
    else:
        tier = "none"
        detail = "No WI or US HPAI livestock/poultry detections reported in window"

    boosts = _tier_boosts()
    result = {
        "tier": tier,
        "boost": boosts.get(tier, 0.0),
        "wi_livestock_detections_90d": wi_livestock,
        "wi_poultry_detections_90d": wi_poultry,
        "us_livestock_detections_90d": us_livestock_total,
        "wi_human_cases_ytd": None,
        "us_human_cases_ytd": None,
        "source": "usda_aphis",
        "source_label": "USDA APHIS HPAI Livestock + Poultry Detections",
        "source_url": "https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections",
        "detail": detail,
        "signal_scope": "statewide_wisconsin",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "fetch_errors": fetch_errors,
    }
    set_in_persistent_cache(CACHE_KEY, result, expiry_days=CACHE_DAYS)
    logger.info(f"H5N1 fetched: tier={tier}, wi_livestock={wi_livestock}, wi_poultry={wi_poultry}")
    return result


def _fallback() -> Dict[str, Any]:
    return {
        "tier": "none",
        "boost": 0.0,
        "wi_livestock_detections_90d": 0,
        "wi_poultry_detections_90d": 0,
        "us_livestock_detections_90d": 0,
        "wi_human_cases_ytd": None,
        "us_human_cases_ytd": None,
        "source": "unavailable",
        "source_label": "USDA APHIS HPAI (cache unavailable)",
        "source_url": "https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections",
        "detail": "Data unavailable - awaiting scheduler refresh",
        "signal_scope": "statewide_wisconsin",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "fetch_errors": [],
    }


def get_h5n1_outbreak_flags() -> Dict[str, Any]:
    """Stable accessor for the dispatch in utils/disease_surveillance.py."""
    try:
        return fetch_h5n1_surveillance()
    except Exception as exc:
        logger.error(f"get_h5n1_outbreak_flags failed: {exc}")
        return _fallback()
