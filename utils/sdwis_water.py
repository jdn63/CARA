"""
EPA SDWIS public water system data module.

DATA SOURCE
-----------
EPA Envirofacts SDWIS REST API (free, no key):

    https://data.epa.gov/efservice/WATER_SYSTEM/...
    https://data.epa.gov/efservice/GEOGRAPHIC_AREA/...

WATER_SYSTEM provides per-system attributes for Wisconsin (population
served, system type CWS/NTNCWS/TNCWS, activity code, primary source
GW/SW). GEOGRAPHIC_AREA provides the county served per system. The two
tables are joined on pwsid.

AGGREGATION
-----------
Per county: active system counts by type, population served by
community water systems (CWS), groundwater share, and a private-well
reliance estimate:

    private_well_reliance = 1 - min(1, cws_population_served /
                                        county_population)

County population comes from utils.census_data_loader. Systems serving
multiple counties are counted in each county they serve; their
population served is attributed to the primary (first-listed) county
only, to avoid double counting in the reliance estimate.

KNOWN COVERAGE GAP
------------------
Menominee County is coterminous with the Menominee Indian Reservation.
Its public water systems are regulated under EPA Region 5 direct tribal
primacy, not Wisconsin state primacy, so the STATE_SERVED=WI query
returns no rows for it. Menominee therefore has no SDWIS cache entry
and callers fall back to the disclosed rule-based proxy for that county
(coverage: 71 of 72 counties).

CACHE-ONLY INVARIANT
--------------------
fetch_bulk_sdwis_data() performs live HTTP and is called only by the
scheduler job refresh_all_epa_sdwis. It short-circuits under
is_cache_only_mode(). get_water_system_metrics() reads only the
persistent cache and never fetches.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

EF_BASE = "https://data.epa.gov/efservice"
SDWIS_CACHE_PREFIX = "epa_sdwis_"
SDWIS_CACHE_EXPIRY_DAYS = 400  # annual refresh cadence
PAGE_SIZE = 1000
REQUEST_TIMEOUT = 90


def _fetch_pages(table_filter: str) -> list:
    """Paginate an Envirofacts table query, returning all rows."""
    rows = []
    start = 0
    while True:
        url = (f"{EF_BASE}/{table_filter}/ROWS/"
               f"{start}:{start + PAGE_SIZE - 1}/JSON")
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        page = resp.json()
        if not isinstance(page, list) or not page:
            break
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        start += PAGE_SIZE
        time.sleep(0.5)
    return rows


def fetch_bulk_sdwis_data() -> Dict[str, Dict[str, Any]]:
    """
    Fetch and join SDWIS WATER_SYSTEM and GEOGRAPHIC_AREA for Wisconsin,
    aggregated to a per-county table keyed by lowercase county name.
    Returns an empty dict on failure or in cache-only mode.
    """
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("epa_sdwis_bulk")
        return {}

    try:
        systems = _fetch_pages(
            "WATER_SYSTEM/STATE_CODE/=/WI/PWS_ACTIVITY_CODE/=/A")
        geo = _fetch_pages("GEOGRAPHIC_AREA/STATE_SERVED/=/WI")
    except Exception as exc:
        logger.error("SDWIS bulk fetch failed: %s", exc)
        return {}

    return aggregate_sdwis_tables(systems, geo)


def aggregate_sdwis_tables(systems: list, geo: list) -> Dict[str, Dict[str, Any]]:
    """
    Join WATER_SYSTEM and GEOGRAPHIC_AREA rows on pwsid and aggregate to
    a per-county table keyed by lowercase county name.
    """
    by_pwsid: Dict[str, Dict[str, Any]] = {}
    for s in systems:
        pwsid = s.get("pwsid")
        if pwsid:
            by_pwsid[pwsid] = s

    counties_by_pwsid: Dict[str, list] = {}
    for g in geo:
        pwsid = g.get("pwsid")
        county = (g.get("county_served") or "").strip()
        if pwsid and county and pwsid in by_pwsid:
            counties_by_pwsid.setdefault(pwsid, [])
            if county not in counties_by_pwsid[pwsid]:
                counties_by_pwsid[pwsid].append(county)

    from utils.census_data_loader import wisconsin_census

    table: Dict[str, Dict[str, Any]] = {}

    def _bucket(county: str) -> Dict[str, Any]:
        key = county.lower()
        if key not in table:
            table[key] = {
                "county": county,
                "active_systems_total": 0,
                "cws_count": 0,
                "ntncws_count": 0,
                "tncws_count": 0,
                "cws_population_served": 0,
                "groundwater_systems": 0,
                "surface_water_systems": 0,
            }
        return table[key]

    for pwsid, counties in counties_by_pwsid.items():
        sys_row = by_pwsid[pwsid]
        stype = (sys_row.get("pws_type_code") or "").upper()
        source = (sys_row.get("primary_source_code") or "").upper()
        pop = int(sys_row.get("population_served_count") or 0)
        for idx, county in enumerate(counties):
            b = _bucket(county)
            b["active_systems_total"] += 1
            if stype == "CWS":
                b["cws_count"] += 1
                if idx == 0:
                    b["cws_population_served"] += pop
            elif stype == "NTNCWS":
                b["ntncws_count"] += 1
            elif stype == "TNCWS":
                b["tncws_count"] += 1
            if source.startswith("GW"):
                b["groundwater_systems"] += 1
            elif source.startswith("SW"):
                b["surface_water_systems"] += 1

    for key, b in table.items():
        county_pop = wisconsin_census.get_county_population(b["county"])
        if county_pop:
            reliance = 1.0 - min(1.0, b["cws_population_served"] / county_pop)
            b["private_well_reliance"] = round(reliance, 3)
            b["county_population"] = county_pop
        else:
            b["private_well_reliance"] = None
            b["county_population"] = None
        b["retrieved_at"] = datetime.utcnow().isoformat()

    logger.info("SDWIS bulk fetch: %d systems, %d counties",
                len(by_pwsid), len(table))
    return table


def write_snapshot(table: Dict[str, Dict[str, Any]]) -> None:
    """Write a human-readable JSON snapshot for transparency."""
    import os
    snapshot_dir = "data/water"
    os.makedirs(snapshot_dir, exist_ok=True)
    path = os.path.join(snapshot_dir, "wisconsin_county_sdwis.json")
    with open(path, "w") as f:
        json.dump({
            "source": "EPA Envirofacts SDWIS (WATER_SYSTEM + GEOGRAPHIC_AREA)",
            "generated_at": datetime.utcnow().isoformat(),
            "county_count": len(table),
            "counties": table,
        }, f, indent=2, sort_keys=True)


def populate_cache_from_bulk(table: Dict[str, Dict[str, Any]]) -> int:
    written = 0
    for key, payload in table.items():
        try:
            set_in_persistent_cache(
                SDWIS_CACHE_PREFIX + key, payload,
                expiry_days=SDWIS_CACHE_EXPIRY_DAYS)
            written += 1
        except Exception as exc:
            logger.error("SDWIS cache write failed for %s: %s", key, exc)
    return written


def get_water_system_metrics(county_name: str) -> Optional[Dict[str, Any]]:
    """
    Cache-only accessor for per-county SDWIS metrics. Never fetches.
    Returns None when the cache has no entry (caller falls back to its
    disclosed proxy and labels it as such).
    """
    key = SDWIS_CACHE_PREFIX + (county_name or "").strip().lower()
    try:
        return get_from_persistent_cache(
            key, max_age_days=SDWIS_CACHE_EXPIRY_DAYS)
    except Exception as exc:
        logger.warning("SDWIS cache read failed for %s: %s",
                       county_name, exc)
        return None
