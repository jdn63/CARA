"""
CDC Environmental Public Health Tracking (EPHT) heat exposure metrics
for Wisconsin counties.

Purpose
-------
Provides the first real, county-resolved, observed source for the
"annual heat days" exposure metric that drives the Extreme Heat
domain's exposure sub-formula in utils/climate_adjusted_risk.py.

Before this module the pipeline carried two synthetic layers:
  1. utils/wisconsin_climate_data.get_wisconsin_heat_days() returned a
     constant 12 statewide.
  2. utils/extreme_heat_metrics.get_annual_heat_days() pulled monthly
     maximums from the NCEI Climate-at-a-Glance API and used a
     "if monthly max >= 85 F add 3 days" heuristic to fabricate a
     daily count, then cached the fabricated value as if it were real.

Both layers are retained as last-resort fallbacks (the constant for
elderly/ED-visit paths that have no real replacement; the NCEI
heuristic as a redundancy under EPHT) but the canonical source for the
exposure score is now this module.

Endpoints (no API key required)
-------------------------------
- Measure 421: Annual count of days with maximum temperature >= 90 F,
  per county, per year. Source dataset is NCEI nClimGrid daily series
  aggregated to county.
- Measure 1064: Annual crude rate of emergency-department visits for
  heat-related illness per 100,000 population, per county, per year.

URL pattern:
  https://ephtracking.cdc.gov/apigateway/api/v1/getCoreHolder/
    {measure_id}/1/55/ALL/0/0/0/JSON

The "55" is Wisconsin's state FIPS. "ALL" requests every county in
the state. The last three "0"s defeat optional stratification.

Cadence and known data lag
--------------------------
EPHT publishes annually and lags real time by roughly 12 to 24 months.
In calendar year 2026 the most recent measure-421 year is typically
2023 or 2024. The scheduler refresh interval is set to annual
(8760 h) and the freshness window to 500 days so the dashboard
freshness panel does not flag an inherently lagged source as stale.

Cache-only request-path invariant
---------------------------------
The request-path getters in this module read from the persistent
cache only. If the cache is empty and the calling thread is inside
`utils.request_context.is_cache_only_mode()`, the getter records a
blocked fetch and returns None. The caller is expected to fall back
to the NCEI heuristic (also cache-only) and finally to None per the
v28.7 explicit-failure-mode contract documented in ARCHITECTURE.md.

Scheduler entry point is `warm_all_wi_counties()`, called via
`utils.data_source_refresher.refresh_all_cdc_epht_heat`.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from utils.persistent_cache import (
    get_from_persistent_cache,
    set_in_persistent_cache,
)

logger = logging.getLogger(__name__)


EPHT_BASE_URL = "https://ephtracking.cdc.gov/apigateway/api/v1/getCoreHolder"
MEASURE_HEAT_DAYS_90F = 421
MEASURE_HEAT_ED_VISITS = 1064

WI_STATE_FIPS = "55"

_SOURCE_ID = "cdc_epht_heat"
_PERSISTENT_KEY_PREFIX = "cdc_epht_heat"
_FETCH_TIMEOUT_SECONDS = 30
_PERSISTENT_CACHE_DAYS = 400


_WI_COUNTY_FIPS: Dict[str, str] = {
    'Adams': '001', 'Ashland': '003', 'Barron': '005', 'Bayfield': '007',
    'Brown': '009', 'Buffalo': '011', 'Burnett': '013', 'Calumet': '015',
    'Chippewa': '017', 'Clark': '019', 'Columbia': '021', 'Crawford': '023',
    'Dane': '025', 'Dodge': '027', 'Door': '029', 'Douglas': '031',
    'Dunn': '033', 'Eau Claire': '035', 'Florence': '037', 'Fond du Lac': '039',
    'Forest': '041', 'Grant': '043', 'Green': '045', 'Green Lake': '047',
    'Iowa': '049', 'Iron': '051', 'Jackson': '053', 'Jefferson': '055',
    'Juneau': '057', 'Kenosha': '059', 'Kewaunee': '061', 'La Crosse': '063',
    'Lafayette': '065', 'Langlade': '067', 'Lincoln': '069', 'Manitowoc': '071',
    'Marathon': '073', 'Marinette': '075', 'Marquette': '077', 'Menominee': '078',
    'Milwaukee': '079', 'Monroe': '081', 'Oconto': '083', 'Oneida': '085',
    'Outagamie': '087', 'Ozaukee': '089', 'Pepin': '091', 'Pierce': '093',
    'Polk': '095', 'Portage': '097', 'Price': '099', 'Racine': '101',
    'Richland': '103', 'Rock': '105', 'Rusk': '107', 'St. Croix': '109',
    'Sauk': '111', 'Sawyer': '113', 'Shawano': '115', 'Sheboygan': '117',
    'Taylor': '119', 'Trempealeau': '121', 'Vernon': '123', 'Vilas': '125',
    'Walworth': '127', 'Washburn': '129', 'Washington': '131', 'Waukesha': '133',
    'Waupaca': '135', 'Waushara': '137', 'Winnebago': '139', 'Wood': '141',
}

_FIPS_TO_COUNTY: Dict[str, str] = {fips: name for name, fips in _WI_COUNTY_FIPS.items()}


def _measure_url(measure_id: int) -> str:
    """Build the EPHT API URL for a Wisconsin all-county batch fetch.

    The CDC EPHT path segments are:
      measureId / geographicTypeId (1=state-county) / parentGeographicId
      (state FIPS) / childGeographicId (ALL=every county) / temporalId
      and 3 stratification fields (we want the unstratified series, so
      all zero) / response format.

    A single call returns every available year for every county in the
    state. We pick the latest non-null value per county at parse time.
    """
    return (
        f"{EPHT_BASE_URL}/{measure_id}/1/{WI_STATE_FIPS}/ALL/0/0/0/JSON"
    )


def _safe_float(value: Any) -> Optional[float]:
    """Best-effort numeric coercion. None/blank/non-numeric returns None."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _county_fips_from_geo_id(geo_id: Any) -> Optional[str]:
    """Extract the 3-digit Wisconsin county FIPS from an EPHT geoId.

    EPHT typically returns a 5-digit string (state + county FIPS) like
    "55079" for Milwaukee. Some historical responses use integer types
    or pad inconsistently. Returns the 3-digit suffix only when the
    geoId belongs to Wisconsin.
    """
    if geo_id is None:
        return None
    s = str(geo_id).strip()
    if not s.isdigit():
        return None
    s = s.zfill(5)
    if not s.startswith(WI_STATE_FIPS):
        return None
    suffix = s[2:]
    if suffix in _FIPS_TO_COUNTY:
        return suffix
    return None


def _parse_epht_payload(payload: Any) -> Dict[str, Tuple[float, int]]:
    """Parse a CDC EPHT JSON response into {county_fips: (value, year)}.

    Defensive: the EPHT API returns its payload under one of several
    shapes ("tableResult", "table_result", a top-level list of rows,
    etc.) depending on the measure. This function walks every plausible
    container and pulls rows with a recognizable geoId, year, and
    dataValue. Per county only the row with the highest year and a
    non-null value is retained.
    """
    rows: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        rows = [r for r in payload if isinstance(r, dict)]
    elif isinstance(payload, dict):
        for key in ('tableResult', 'table_result', 'results', 'data', 'rows'):
            container = payload.get(key)
            if isinstance(container, list):
                rows.extend(r for r in container if isinstance(r, dict))

    if not rows:
        logger.warning(
            "EPHT parse: no recognizable rows in payload "
            "(top-level keys=%s)",
            list(payload.keys()) if isinstance(payload, dict) else 'non-dict',
        )
        return {}

    best: Dict[str, Tuple[float, int]] = {}
    for row in rows:
        county_fips = _county_fips_from_geo_id(
            row.get('geoId') or row.get('geo_id') or row.get('geoid')
        )
        if county_fips is None:
            continue
        year_raw = row.get('year') or row.get('temporal') or row.get('Year')
        try:
            year = int(str(year_raw))
        except (TypeError, ValueError):
            continue
        value = _safe_float(
            row.get('dataValue')
            or row.get('data_value')
            or row.get('value')
        )
        if value is None:
            continue
        prior = best.get(county_fips)
        if prior is None or year > prior[1]:
            best[county_fips] = (value, year)

    return best


def _fetch_measure(measure_id: int) -> Dict[str, Tuple[float, int]]:
    """Fetch one EPHT measure for Wisconsin and parse to a county map.

    Uses the shared utils.http_client.fetch_json wrapper so the CDC
    EPHT endpoint participates in the same retry/backoff/circuit
    breaker discipline as the other CDC fetchers. Returns an empty
    dict on any failure (caller logs and continues).
    """
    from utils.http_client import fetch_json, CircuitOpenError
    url = _measure_url(measure_id)
    try:
        payload = fetch_json(
            source_id=f"cdc_epht_{measure_id}",
            url=url,
            timeout=_FETCH_TIMEOUT_SECONDS,
        )
    except CircuitOpenError as exc:
        logger.warning("EPHT measure %s refused by breaker: %s", measure_id, exc)
        return {}
    except Exception as exc:
        logger.error(
            "EPHT measure %s fetch failed: %s: %s",
            measure_id, type(exc).__name__, exc,
        )
        return {}
    return _parse_epht_payload(payload)


def _persistent_key(county_name: str, measure_id: int) -> str:
    """Per-county persistent-cache key, normalized to lowercase county."""
    slug = county_name.strip().lower().replace(' ', '_').replace('.', '')
    return f"{_PERSISTENT_KEY_PREFIX}_{measure_id}_{slug}"


def _store_county(
    county_name: str,
    measure_id: int,
    value: float,
    data_year: int,
) -> Dict[str, Any]:
    """Persist a single county / measure entry to the file cache.

    The stored payload always includes source provenance so the
    dashboard can label the metric correctly without re-deriving the
    source name. Returns the stored dict for reuse by the scheduler
    summary.
    """
    payload = {
        'value': value,
        'data_year': data_year,
        'measure_id': measure_id,
        'source': 'CDC EPHT',
        'source_url': _measure_url(measure_id),
        'fetched_at': datetime.utcnow().isoformat(),
    }
    set_in_persistent_cache(
        _persistent_key(county_name, measure_id),
        payload,
        expiry_days=_PERSISTENT_CACHE_DAYS,
    )
    return payload


def warm_all_wi_counties() -> Dict[str, Any]:
    """Scheduler entry point: warm EPHT heat caches for all 72 WI counties.

    Performs exactly two HTTP calls (one per measure), parses the
    per-county series, and writes each county's most recent observed
    value to the persistent cache. Counties with no data in EPHT (small-
    cell suppression or no recent year) are silently skipped; their
    request-path getters will return None and the dashboard will fall
    through to the NCEI heuristic.

    Returns a summary dict in the same shape used by the other
    refresh_all_* jobs (success / failed / fallback counts plus an
    error list) so the scheduler status page can render uniformly.

    Important: this function never raises. EPHT outages must not stop
    the scheduler tick; the persistent cache from the prior successful
    run remains valid until its `expiry_days` window elapses.
    """
    results: Dict[str, Any] = {
        'source_type': _SOURCE_ID,
        'started_at': datetime.utcnow().isoformat(),
        'success': 0,
        'failed': 0,
        'fallback': 0,
        'errors': [],
        'measures': {},
    }

    for label, measure_id in (
        ('heat_days', MEASURE_HEAT_DAYS_90F),
        ('ed_visits', MEASURE_HEAT_ED_VISITS),
    ):
        parsed = _fetch_measure(measure_id)
        per_measure = {'fetched_counties': 0, 'missing_counties': 0, 'latest_year': None}
        if not parsed:
            results['failed'] += 1
            results['errors'].append({
                'measure': label,
                'error': 'EPHT returned no parseable rows',
            })
            results['measures'][label] = per_measure
            continue
        for county_name, county_fips in _WI_COUNTY_FIPS.items():
            entry = parsed.get(county_fips)
            if entry is None:
                per_measure['missing_counties'] += 1
                continue
            value, year = entry
            try:
                _store_county(county_name, measure_id, value, year)
                per_measure['fetched_counties'] += 1
                if per_measure['latest_year'] is None or year > per_measure['latest_year']:
                    per_measure['latest_year'] = year
                results['success'] += 1
            except Exception as exc:
                results['failed'] += 1
                results['errors'].append({
                    'measure': label,
                    'county': county_name,
                    'error': f"{type(exc).__name__}: {exc}",
                })
        results['measures'][label] = per_measure
        logger.info(
            "EPHT %s: %d counties stored, %d missing, latest year=%s",
            label,
            per_measure['fetched_counties'],
            per_measure['missing_counties'],
            per_measure['latest_year'],
        )

    _persist_db_summary(results)

    results['finished_at'] = datetime.utcnow().isoformat()
    return results


def _persist_db_summary(results: Dict[str, Any]) -> None:
    """Write a single DB cache row so the dashboard freshness panel sees us.

    The dashboard's freshness pipeline reads from data_source_cache via
    utils.data_freshness.get_all_freshness_reports. Per-county entries
    are kept in the file-based persistent cache for fast request-path
    reads; this single statewide row exists only to expose a
    fetched_at timestamp under the canonical source ID so the
    freshness badge can render.

    Failure to write the DB row is logged but does not fail the
    refresh: the file cache is still warm and the request path will
    succeed; only the freshness badge becomes stale.
    """
    try:
        from utils.data_cache_manager import save_cached_data
        save_cached_data(
            source_type=_SOURCE_ID,
            data={
                'source': 'CDC EPHT',
                'measures': {
                    'heat_days': MEASURE_HEAT_DAYS_90F,
                    'ed_visits': MEASURE_HEAT_ED_VISITS,
                },
                'summary': results.get('measures', {}),
                'success': results.get('success', 0),
                'failed': results.get('failed', 0),
            },
            api_source=EPHT_BASE_URL,
            used_fallback=results.get('failed', 0) > 0 and results.get('success', 0) == 0,
            fallback_reason=(
                'EPHT API returned no parseable rows'
                if results.get('success', 0) == 0 else None
            ),
        )
    except Exception as exc:
        logger.warning(
            "EPHT DB freshness row write failed (file cache still warm): %s: %s",
            type(exc).__name__, exc,
        )


def _read_county(
    county_name: str,
    measure_id: int,
) -> Optional[Dict[str, Any]]:
    """Request-path getter for one county / measure.

    Returns the stored payload dict if present in the persistent cache,
    or None if the cache is empty / expired. Honors the cache-only
    request-path invariant: never attempts a live fetch, never raises.
    A blocked-fetch telemetry record is added when the cache is empty
    inside an explicit cache-only context so the freshness panel can
    surface "EPHT cache cold" diagnostics.
    """
    payload = get_from_persistent_cache(
        _persistent_key(county_name, measure_id),
        max_age_days=_PERSISTENT_CACHE_DAYS,
    )
    if payload is not None:
        return payload

    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch(f"{_SOURCE_ID}:{county_name}")
    return None


def get_epht_heat_days_for_county(county_name: str) -> Optional[Dict[str, Any]]:
    """Return the most recent EPHT measure-421 entry for a WI county.

    Returns a dict with keys `value` (annual heat-day count as float),
    `data_year`, `source`, `source_url`, `fetched_at`. Returns None
    when no entry is cached for the county. Callers should treat the
    None case as "EPHT unavailable for this county" and consult the
    next fallback in the chain (NCEI heuristic, then None).
    """
    if county_name not in _WI_COUNTY_FIPS:
        return None
    return _read_county(county_name, MEASURE_HEAT_DAYS_90F)


def get_epht_ed_visits_for_county(county_name: str) -> Optional[Dict[str, Any]]:
    """Return the most recent EPHT measure-1064 entry for a WI county.

    Returns a dict with keys `value` (rate per 100,000 per year),
    `data_year`, `source`, `source_url`, `fetched_at`. Returns None
    when no entry is cached for the county. The current ED-visits
    estimator in utils.extreme_heat_metrics is population-based; this
    accessor exists so a future review can switch that estimator to
    real observed rates without further plumbing.
    """
    if county_name not in _WI_COUNTY_FIPS:
        return None
    return _read_county(county_name, MEASURE_HEAT_ED_VISITS)
