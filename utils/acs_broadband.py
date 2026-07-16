"""
Census ACS broadband subscription data module (communications input).

DATA SOURCE
-----------
Census Bureau ACS 5-year API, table B28002 (Presence and Types of
Internet Subscriptions in Household), using CENSUS_API_KEY:

    https://api.census.gov/data/2023/acs/acs5
        ?get=NAME,B28002_001E,B28002_004E&for=county:*&in=state:55

    B28002_001E  total households
    B28002_004E  households with a broadband subscription (any type)

The FCC Broadband Data Collection map API was evaluated first but its
public endpoints return 401/405 without a licensed account, so ACS
measured household subscription rates are used instead. This measures
adoption, not availability, and is labeled accordingly.

DERIVED METRIC
--------------
broadband_share = broadband households / total households

comms_vulnerability = 1 - percentile rank of broadband_share, scaled
to the 0.15-0.95 band used by other CARA exposure inputs (lower
subscription share = higher communications vulnerability).

CACHE-ONLY INVARIANT
--------------------
fetch_bulk_acs_broadband() performs live HTTP and is called only by
the scheduler job refresh_all_acs_broadband. It short-circuits under
is_cache_only_mode(). get_broadband_metrics() reads only the
persistent cache and never fetches.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

ACS_YEAR = 2023
ACS_URL = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"
BROADBAND_CACHE_PREFIX = "acs_broadband_"
BROADBAND_CACHE_EXPIRY_DAYS = 400
REQUEST_TIMEOUT = 60


def fetch_bulk_acs_broadband() -> Dict[str, Dict[str, Any]]:
    """
    Fetch B28002 broadband subscription counts for all Wisconsin
    counties. Returns a dict keyed by lowercase county name; empty
    dict on failure or in cache-only mode.
    """
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("acs_broadband_bulk")
        return {}

    api_key = os.environ.get("CENSUS_API_KEY")
    if not api_key:
        logger.error("ACS broadband fetch skipped: CENSUS_API_KEY not set")
        return {}

    try:
        resp = requests.get(ACS_URL, params={
            "get": "NAME,B28002_001E,B28002_004E",
            "for": "county:*",
            "in": "state:55",
            "key": api_key,
        }, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        rows = resp.json()
    except Exception as exc:
        logger.error("ACS broadband fetch failed: %s", exc)
        return {}

    if not rows or len(rows) < 2:
        logger.error("ACS broadband fetch returned no data rows")
        return {}

    table: Dict[str, Dict[str, Any]] = {}
    for row in rows[1:]:
        name, total, broadband = row[0], row[1], row[2]
        county = name.replace(" County, Wisconsin", "").strip()
        total_i = int(total or 0)
        broadband_i = int(broadband or 0)
        share = round(broadband_i / total_i, 4) if total_i else None
        table[county.lower()] = {
            "county": county,
            "total_households": total_i,
            "broadband_households": broadband_i,
            "broadband_share": share,
            "acs_year": ACS_YEAR,
        }

    ranked = sorted(
        [k for k, v in table.items() if v["broadband_share"] is not None],
        key=lambda k: table[k]["broadband_share"])
    n = len(ranked)
    for rank, key in enumerate(ranked):
        pct = rank / (n - 1) if n > 1 else 0.5
        table[key]["comms_vulnerability"] = round(0.95 - 0.80 * pct, 3)
    for v in table.values():
        v.setdefault("comms_vulnerability", None)
        v["retrieved_at"] = datetime.utcnow().isoformat()

    logger.info("ACS broadband fetch: %d counties", len(table))
    return table


def write_snapshot(table: Dict[str, Dict[str, Any]]) -> None:
    """Write a human-readable JSON snapshot for transparency."""
    snapshot_dir = "data/communications"
    os.makedirs(snapshot_dir, exist_ok=True)
    path = os.path.join(snapshot_dir, "wisconsin_county_broadband.json")
    with open(path, "w") as f:
        json.dump({
            "source": f"Census ACS {ACS_YEAR} 5-year, table B28002",
            "generated_at": datetime.utcnow().isoformat(),
            "county_count": len(table),
            "counties": table,
        }, f, indent=2, sort_keys=True)


def populate_cache_from_bulk(table: Dict[str, Dict[str, Any]]) -> int:
    written = 0
    for key, payload in table.items():
        try:
            set_in_persistent_cache(
                BROADBAND_CACHE_PREFIX + key, payload,
                expiry_days=BROADBAND_CACHE_EXPIRY_DAYS)
            written += 1
        except Exception as exc:
            logger.error("ACS broadband cache write failed for %s: %s",
                         key, exc)
    return written


def get_broadband_metrics(county_name: str) -> Optional[Dict[str, Any]]:
    """
    Cache-only accessor for per-county broadband metrics. Never fetches.
    """
    key = BROADBAND_CACHE_PREFIX + (county_name or "").strip().lower()
    try:
        return get_from_persistent_cache(
            key, max_age_days=BROADBAND_CACHE_EXPIRY_DAYS)
    except Exception as exc:
        logger.warning("ACS broadband cache read failed for %s: %s",
                       county_name, exc)
        return None
