"""
Census County Business Patterns (CBP) gasoline station data module.

DATA SOURCE
-----------
Census Bureau CBP API (requires CENSUS_API_KEY, already configured):

    https://api.census.gov/data/2023/cbp
        ?get=ESTAB,NAME&for=county:*&in=state:55&NAICS2017=447

NAICS 447 (Gasoline Stations) establishment counts per Wisconsin
county. The 2023 vintage still uses the NAICS2017 predicate name.
Counties with too few establishments to disclose are suppressed by
Census and simply absent from the response; those counties fall back
to the disclosed rule-based proxy.

DERIVED METRIC
--------------
stations_per_10k = establishments / county_population * 10000

fuel_access_exposure = 1 - percentile rank of stations_per_10k across
counties with data (fewer stations per capita = higher exposure),
scaled to the 0.15-0.95 band used by the EAGLE-I electrical exposure
score for consistency.

CACHE-ONLY INVARIANT
--------------------
fetch_bulk_cbp_fuel() performs live HTTP and is called only by the
scheduler job refresh_all_census_cbp_fuel. It short-circuits under
is_cache_only_mode(). get_fuel_station_metrics() reads only the
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

CBP_YEAR = 2023
CBP_URL = f"https://api.census.gov/data/{CBP_YEAR}/cbp"
CBP_CACHE_PREFIX = "census_cbp_fuel_"
CBP_CACHE_EXPIRY_DAYS = 400
REQUEST_TIMEOUT = 60


def fetch_bulk_cbp_fuel() -> Dict[str, Dict[str, Any]]:
    """
    Fetch NAICS 447 establishment counts for all Wisconsin counties and
    derive per-capita metrics and an exposure score. Returns a dict
    keyed by lowercase county name; empty dict on failure or in
    cache-only mode.
    """
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("census_cbp_fuel_bulk")
        return {}

    api_key = os.environ.get("CENSUS_API_KEY")
    if not api_key:
        logger.error("CBP fuel fetch skipped: CENSUS_API_KEY not set")
        return {}

    try:
        resp = requests.get(CBP_URL, params={
            "get": "ESTAB,NAME",
            "for": "county:*",
            "in": "state:55",
            "NAICS2017": "447",
            "key": api_key,
        }, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        rows = resp.json()
    except Exception as exc:
        logger.error("CBP fuel fetch failed: %s", exc)
        return {}

    if not rows or len(rows) < 2:
        logger.error("CBP fuel fetch returned no data rows")
        return {}

    header = rows[0]
    idx = {name: header.index(name) for name in header}

    from utils.census_data_loader import wisconsin_census

    table: Dict[str, Dict[str, Any]] = {}
    for row in rows[1:]:
        name = row[idx["NAME"]]
        county = name.replace(" County, Wisconsin", "").strip()
        estab = int(row[idx["ESTAB"]] or 0)
        pop = wisconsin_census.get_county_population(county)
        per_10k = round(estab / pop * 10000, 3) if pop else None
        table[county.lower()] = {
            "county": county,
            "gas_stations": estab,
            "county_population": pop,
            "stations_per_10k": per_10k,
            "cbp_year": CBP_YEAR,
        }

    ranked = sorted(
        [k for k, v in table.items() if v["stations_per_10k"] is not None],
        key=lambda k: table[k]["stations_per_10k"])
    n = len(ranked)
    for rank, key in enumerate(ranked):
        pct = rank / (n - 1) if n > 1 else 0.5
        table[key]["fuel_access_exposure"] = round(0.95 - 0.80 * pct, 3)
    for v in table.values():
        v.setdefault("fuel_access_exposure", None)
        v["retrieved_at"] = datetime.utcnow().isoformat()

    logger.info("CBP fuel fetch: %d counties", len(table))
    return table


def write_snapshot(table: Dict[str, Dict[str, Any]]) -> None:
    """Write a human-readable JSON snapshot for transparency."""
    snapshot_dir = "data/fuel"
    os.makedirs(snapshot_dir, exist_ok=True)
    path = os.path.join(snapshot_dir, "wisconsin_county_cbp_fuel.json")
    with open(path, "w") as f:
        json.dump({
            "source": f"Census County Business Patterns {CBP_YEAR}, NAICS 447",
            "generated_at": datetime.utcnow().isoformat(),
            "county_count": len(table),
            "counties": table,
        }, f, indent=2, sort_keys=True)


def populate_cache_from_bulk(table: Dict[str, Dict[str, Any]]) -> int:
    written = 0
    for key, payload in table.items():
        try:
            set_in_persistent_cache(
                CBP_CACHE_PREFIX + key, payload,
                expiry_days=CBP_CACHE_EXPIRY_DAYS)
            written += 1
        except Exception as exc:
            logger.error("CBP fuel cache write failed for %s: %s", key, exc)
    return written


def get_fuel_station_metrics(county_name: str) -> Optional[Dict[str, Any]]:
    """
    Cache-only accessor for per-county CBP fuel metrics. Never fetches.
    """
    key = CBP_CACHE_PREFIX + (county_name or "").strip().lower()
    try:
        return get_from_persistent_cache(
            key, max_age_days=CBP_CACHE_EXPIRY_DAYS)
    except Exception as exc:
        logger.warning("CBP fuel cache read failed for %s: %s",
                       county_name, exc)
        return None
