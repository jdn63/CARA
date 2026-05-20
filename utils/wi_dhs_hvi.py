"""
Wisconsin DHS Heat Vulnerability Index (HVI) data module.

Replaces the prior 404-prone HTTP fetcher in utils/heat_vulnerability.py.

DATA SOURCE
-----------
Wisconsin Department of Health Services Heat Vulnerability Index, served as
a public ArcGIS MapServer layer at:

    https://dhsgis.wi.gov/server/rest/services/DHS_HVI/Heat_Vulnerability_Index/MapServer/0

The layer publishes 4,472 Census block groups covering Wisconsin
(state FIPS 55) with the following per-block-group fields used here:

    CNTY_FIPS10, CNTY_NAME10         block-group county identifiers
    EnviroIndex_Value_WI             z-score, environmental sub-index
    HealthIndex_Value_WI             z-score, health sub-index
    PopIndex_Value_WI                z-score, population sub-index
    SocioIndex_Value_WI              z-score, socioeconomic sub-index
    HVI_Value_WI                     composite z-score (sum of 4 sub-indices)

All z-scores are statewide-normalized by DHS.

AGGREGATION CHOICE
------------------
Block-group z-scores are aggregated to county level using an UNWEIGHTED
arithmetic mean.  Census block groups are designed by the Census Bureau
to contain roughly 600-3,000 people each, so an unweighted mean across
the block groups of a county is a defensible first-cut population proxy.
A future improvement could fetch ACS block-group populations and apply a
true population-weighted mean.

VULNERABILITY SCORE 0-1
-----------------------
After per-county z-score means are computed, they are min-max normalized
across the 72 Wisconsin counties to produce a 0-1 vulnerability_score.
A quintile-bin categorical label (Low, Moderate Low, Moderate, Moderate
High, High) is also derived, matching DHS's own published bucketing.

CACHING
-------
Results are written to the persistent cache (utils.persistent_cache) keyed
by county name, with a 90-day TTL appropriate for an index that DHS
updates on a multi-year cadence.  A human-readable JSON snapshot of the
full 72-county table is also written to
data/wi_dhs_hvi/wisconsin_county_hvi.json for transparency and version
control.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)


WI_DHS_HVI_QUERY_URL = (
    "https://dhsgis.wi.gov/server/rest/services/DHS_HVI/"
    "Heat_Vulnerability_Index/MapServer/0/query"
)
WI_DHS_HVI_CACHE_PREFIX = "wi_dhs_hvi_"
WI_DHS_HVI_CACHE_EXPIRY_DAYS = 90
WI_DHS_HVI_PAGE_SIZE = 2000
WI_DHS_HVI_REQUEST_TIMEOUT = 60

SNAPSHOT_DIR = "data/wi_dhs_hvi"
SNAPSHOT_PATH = os.path.join(SNAPSHOT_DIR, "wisconsin_county_hvi.json")


_HVI_FIELDS = [
    "CNTY_FIPS10",
    "CNTY_NAME10",
    "BLKGRP_GEOID10",
    "HVI_Value_WI",
    "EnviroIndex_Value_WI",
    "HealthIndex_Value_WI",
    "PopIndex_Value_WI",
    "SocioIndex_Value_WI",
]


def _normalize_county_key(name: str) -> str:
    return (name or "").strip().lower().replace(" county", "")


def _quintile_label(rank: int, total: int) -> str:
    if total <= 1:
        return "Moderate"
    pct = rank / (total - 1)
    if pct < 0.20:
        return "Low"
    if pct < 0.40:
        return "Moderate Low"
    if pct < 0.60:
        return "Moderate"
    if pct < 0.80:
        return "Moderate High"
    return "High"


def fetch_bulk_hvi_data() -> Dict[str, Dict[str, Any]]:
    """
    Paginate the DHS HVI MapServer endpoint and aggregate all block groups
    to a 72-county table.  Returns a dict keyed by lowercase county name.

    On failure returns an empty dict.
    """
    # Cache-only enforcement: bulk HVI is a multi-page paginated fetch
    # warmed by the scheduler quarterly job. See utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("wi_dhs_hvi_bulk")
        return {}

    features: List[Dict[str, Any]] = []
    offset = 0
    pages = 0
    started = time.time()

    while True:
        params = {
            "where": "1=1",
            "outFields": ",".join(_HVI_FIELDS),
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": WI_DHS_HVI_PAGE_SIZE,
        }
        try:
            r = requests.get(
                WI_DHS_HVI_QUERY_URL,
                params=params,
                timeout=WI_DHS_HVI_REQUEST_TIMEOUT,
                headers={"User-Agent": "CARA-Wisconsin-Risk-Assessment/1.0"},
            )
            r.raise_for_status()
            payload = r.json()
        except Exception as e:
            logger.error("DHS HVI page fetch failed at offset %d: %s", offset, e)
            return {}

        page_features = payload.get("features", []) or []
        if not page_features:
            break
        features.extend(page_features)
        pages += 1
        if not payload.get("exceededTransferLimit"):
            break
        offset += len(page_features)
        if pages > 20:
            # Hard fail rather than persist a partial county table.
            # ArcGIS at the time of writing returns the full 4,472 WI
            # block groups in 3 pages of 2,000; > 20 pages means the
            # endpoint contract has shifted and the result is untrustworthy.
            logger.error(
                "DHS HVI pagination guard tripped after %d pages — aborting "
                "to avoid persisting an incomplete county table", pages,
            )
            return {}

    duration = time.time() - started
    logger.info(
        "DHS HVI bulk fetch: %d block groups across %d page(s) in %.1fs",
        len(features), pages, duration,
    )
    if not features:
        return {}

    grouped: Dict[str, Dict[str, Any]] = {}
    for feat in features:
        attrs = feat.get("attributes", {}) or {}
        county_raw = attrs.get("CNTY_NAME10") or ""
        county_key = _normalize_county_key(county_raw)
        if not county_key:
            continue
        bucket = grouped.setdefault(county_key, {
            "county": county_raw.strip().title(),
            "fips": "55" + (attrs.get("CNTY_FIPS10") or "").zfill(3),
            "block_group_count": 0,
            "_hvi_sum": 0.0,
            "_env_sum": 0.0,
            "_health_sum": 0.0,
            "_pop_sum": 0.0,
            "_socio_sum": 0.0,
        })
        bucket["block_group_count"] += 1
        bucket["_hvi_sum"] += attrs.get("HVI_Value_WI") or 0.0
        bucket["_env_sum"] += attrs.get("EnviroIndex_Value_WI") or 0.0
        bucket["_health_sum"] += attrs.get("HealthIndex_Value_WI") or 0.0
        bucket["_pop_sum"] += attrs.get("PopIndex_Value_WI") or 0.0
        bucket["_socio_sum"] += attrs.get("SocioIndex_Value_WI") or 0.0

    county_means: List[Dict[str, Any]] = []
    for key, b in grouped.items():
        n = max(1, b["block_group_count"])
        county_means.append({
            "key": key,
            "county": b["county"],
            "fips": b["fips"],
            "block_group_count": b["block_group_count"],
            "hvi_zscore_mean": b["_hvi_sum"] / n,
            "enviro_zscore_mean": b["_env_sum"] / n,
            "health_zscore_mean": b["_health_sum"] / n,
            "pop_zscore_mean": b["_pop_sum"] / n,
            "socio_zscore_mean": b["_socio_sum"] / n,
        })

    z_values = [c["hvi_zscore_mean"] for c in county_means]
    z_min = min(z_values)
    z_max = max(z_values)
    z_span = (z_max - z_min) or 1.0

    sorted_by_z = sorted(county_means, key=lambda c: c["hvi_zscore_mean"])
    rank_by_key = {c["key"]: idx for idx, c in enumerate(sorted_by_z)}

    timestamp = datetime.utcnow().isoformat()
    result: Dict[str, Dict[str, Any]] = {}
    for c in county_means:
        rank = rank_by_key[c["key"]]
        vulnerability_score = round((c["hvi_zscore_mean"] - z_min) / z_span, 4)
        label = _quintile_label(rank, len(county_means))
        result[c["key"]] = {
            "county": c["county"],
            "fips": c["fips"],
            "block_group_count": c["block_group_count"],
            "hvi_zscore_mean": round(c["hvi_zscore_mean"], 4),
            "enviro_zscore_mean": round(c["enviro_zscore_mean"], 4),
            "health_zscore_mean": round(c["health_zscore_mean"], 4),
            "pop_zscore_mean": round(c["pop_zscore_mean"], 4),
            "socio_zscore_mean": round(c["socio_zscore_mean"], 4),
            "vulnerability_score": vulnerability_score,
            "category": label,
            "statewide_rank": rank + 1,
            "statewide_county_count": len(county_means),
            "data_source": "Wisconsin DHS Heat Vulnerability Index (ArcGIS MapServer)",
            "endpoint": WI_DHS_HVI_QUERY_URL,
            "last_updated": timestamp,
        }

    # Sanity check: Wisconsin has 72 counties.  If the aggregated table
    # is missing more than a couple of them, the upstream feature payload
    # is incomplete and we should not overwrite the on-disk snapshot.
    EXPECTED_WI_COUNTIES = 72
    if len(result) < EXPECTED_WI_COUNTIES - 2:
        logger.error(
            "DHS HVI county aggregation produced %d counties (expected %d) — "
            "refusing to write snapshot or cache", len(result), EXPECTED_WI_COUNTIES,
        )
        return {}

    _write_snapshot(result, timestamp)
    return result


def _write_snapshot(table: Dict[str, Dict[str, Any]], timestamp: str) -> None:
    try:
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        payload = {
            "generated_at": timestamp,
            "endpoint": WI_DHS_HVI_QUERY_URL,
            "county_count": len(table),
            "aggregation": "unweighted mean of block-group z-scores per county",
            "vulnerability_score": "min-max normalized across the 72 WI counties",
            "category": "quintile of statewide rank (Low, Moderate Low, Moderate, Moderate High, High)",
            "counties": table,
        }
        with open(SNAPSHOT_PATH, "w") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
        logger.info("Wrote DHS HVI snapshot to %s", SNAPSHOT_PATH)
    except Exception as e:
        logger.warning("Failed to write DHS HVI snapshot: %s", e)


_in_memory_cache: Dict[str, Dict[str, Any]] = {}


def _load_snapshot() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(SNAPSHOT_PATH):
        return {}
    try:
        with open(SNAPSHOT_PATH) as f:
            payload = json.load(f)
        return payload.get("counties", {}) or {}
    except Exception as e:
        logger.warning("Failed to read DHS HVI snapshot: %s", e)
        return {}


def get_hvi_data(county_name: str) -> Optional[Dict[str, Any]]:
    """
    Return the HVI record for a Wisconsin county.

    Resolution order: in-memory cache, persistent cache, on-disk snapshot
    written by the most recent scheduler refresh.  Returns None if no
    cached data is available (cache-only mode; no live API calls during
    user requests).
    """
    key = _normalize_county_key(county_name)
    if not key:
        return None

    if key in _in_memory_cache:
        return _in_memory_cache[key]

    cached = get_from_persistent_cache(
        f"{WI_DHS_HVI_CACHE_PREFIX}{key}",
        max_age_days=WI_DHS_HVI_CACHE_EXPIRY_DAYS,
    )
    if cached:
        _in_memory_cache[key] = cached
        return cached

    snapshot = _load_snapshot()
    if key in snapshot:
        _in_memory_cache[key] = snapshot[key]
        return snapshot[key]

    logger.debug("No cached DHS HVI data for %s", county_name)
    return None


def populate_cache_from_bulk(table: Dict[str, Dict[str, Any]]) -> int:
    """
    Write a bulk-fetched table into the persistent cache, one entry per
    county.  Returns the number of records written.  Intended for use by
    the scheduler refresh job.
    """
    written = 0
    for key, record in table.items():
        try:
            set_in_persistent_cache(
                f"{WI_DHS_HVI_CACHE_PREFIX}{key}",
                record,
                expiry_days=WI_DHS_HVI_CACHE_EXPIRY_DAYS,
            )
            _in_memory_cache[key] = record
            written += 1
        except Exception as e:
            logger.warning("Failed to persist DHS HVI for %s: %s", key, e)
    return written
