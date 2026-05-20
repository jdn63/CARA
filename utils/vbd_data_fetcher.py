import csv
import io
import json
import logging
import os
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import defaultdict

logger = logging.getLogger(__name__)

DHS_LYME_COUNTY_CSV_URL = "https://www.dhs.wisconsin.gov/epht/lyme-county.csv"
DHS_LYME_STATE_CSV_URL = "https://www.dhs.wisconsin.gov/epht/lyme-state.csv"
DHS_WNV_COUNTY_CSV_URL = "https://www.dhs.wisconsin.gov/epht/west-nile-data-county.csv"
DHS_WNV_STATE_CSV_URL = "https://www.dhs.wisconsin.gov/epht/west-nile-data-state.csv"

DHS_LYME_DATA_URL = "https://www.dhs.wisconsin.gov/tick/lyme-data.htm"
DHS_WNV_DATA_URL = "https://www.dhs.wisconsin.gov/mosquito/wnv-data.htm"

RECENT_YEARS_WINDOW = 6

_real_data_cache = None


def load_real_vbd_data() -> Dict[str, Any]:
    global _real_data_cache
    if _real_data_cache is not None:
        return _real_data_cache

    try:
        path = 'data/disease/wisconsin_vbd_real_data.json'
        if os.path.exists(path):
            with open(path) as f:
                _real_data_cache = json.load(f)
            logger.info("Loaded real VBD data file with %d counties",
                       len(_real_data_cache.get('county_data', {})))
            return _real_data_cache
    except Exception as e:
        logger.warning(f"Error loading real VBD data: {e}")

    _real_data_cache = {}
    return _real_data_cache


def invalidate_cache():
    global _real_data_cache
    _real_data_cache = None


def get_county_real_data(county_name: str) -> Optional[Dict[str, Any]]:
    real_data = load_real_vbd_data()
    county_data = real_data.get('county_data', {}).get(county_name)

    if county_data:
        return county_data

    cached = _get_cached_county_data(county_name)
    if cached:
        return cached

    return county_data


def _get_cached_county_data(county_name: str) -> Optional[Dict[str, Any]]:
    try:
        from utils.data_cache_manager import get_cached_data
        cache_entry = get_cached_data(
            source_type='dhs_vbd_surveillance',
            county_name=county_name
        )
        if cache_entry and cache_entry.get('data'):
            return cache_entry['data']
    except Exception as e:
        logger.debug(f"No cached VBD data for {county_name}: {e}")
    return None


def get_statewide_summary() -> Dict[str, Any]:
    real_data = load_real_vbd_data()
    summary = real_data.get('statewide_summary', {})

    cached = _get_cached_statewide_data()
    if cached:
        summary.update(cached)

    return summary


def _get_cached_statewide_data() -> Optional[Dict[str, Any]]:
    try:
        from utils.data_cache_manager import get_cached_data
        cache_entry = get_cached_data(
            source_type='dhs_vbd_surveillance',
            county_name='_statewide'
        )
        if cache_entry and cache_entry.get('data'):
            return cache_entry['data']
    except Exception as e:
        logger.debug(f"VBD cache lookup failed: {e}")
    return None


def classify_lyme_rate(rate: float) -> str:
    if rate >= 100:
        return 'very_high'
    elif rate >= 50:
        return 'high'
    elif rate >= 20:
        return 'moderate'
    elif rate >= 5:
        return 'low'
    else:
        return 'minimal'


def classify_wnv_rate(rate: float, total_5yr: int = 0) -> str:
    if rate >= 5 or total_5yr >= 3:
        return 'high'
    elif rate >= 2.5:
        return 'moderate'
    elif rate >= 0.5:
        return 'low'
    else:
        return 'minimal'


# --- Empirical-Bayes shrinkage and reliability gates (review finding H9) ---
#
# Crude county-level VBD rates per 100,000 are unstable in low-population
# counties: one extra confirmed Lyme case in a county of 4,500 (Florence,
# Menominee, Iron) moves the per-100k rate by ~20 points, which is enough to
# bounce the county across tier boundaries. Per H9 the fix is two-fold:
#
# 1. Shrink the county rate toward the statewide rate using a Buhlmann
#    credibility weight w = c / (c + k), which is equivalent to a
#    Poisson-Gamma empirical-Bayes posterior mean when the prior is Gamma
#    with mean = state_rate and shape = k (k acts as a "prior strength"
#    expressed in annual-case-equivalents). c is the county's average
#    annual case count over the lookback window.
#
# 2. Tag each county with a reliability tier (low / medium / high) so that
#    downstream code can refuse to apply climate trend boosts (or any other
#    multiplicative amplification) on top of statistically unreliable
#    baselines, and so the UI can show a confidence band rather than a
#    point estimate that pretends to be precise.
#
# Statewide background rates are derived from data/disease/
# wisconsin_vbd_real_data.json statewide_summary divided by the Wisconsin
# resident population (2023 Census estimate, kept as a module constant
# rather than fetched at runtime to keep this helper deterministic).

WI_POPULATION_2023 = 5_896_000  # WI resident population, U.S. Census 2023 estimate

# Prior strength in annual-case-equivalents. Lower k => weaker prior =>
# observed county data dominates faster. k for Lyme is higher because Lyme
# is endemic statewide and the prior is more informative; WNV is sparse
# enough that a strong prior would over-shrink the rare counties that
# actually do see local transmission.
LYME_PRIOR_STRENGTH_K = 3.0
WNV_PRIOR_STRENGTH_K = 1.5

# Reliability bands keyed off observed annual case count. The thresholds
# mirror common small-area-estimation cutoffs and align with the prior
# strengths above (a county whose case count is below the prior strength
# is being driven by the prior, not by its own data).
RELIABILITY_LOW_MAX = 2.0     # 0-2 annual cases: too few to drive the score
RELIABILITY_HIGH_MIN = 10.0   # >= 10 annual cases: observed rate is credible

# Order used to combine per-disease reliability into an overall VBD
# reliability (the weakest disease pulls the combined tier down).
RELIABILITY_ORDER = {'low': 0, 'medium': 1, 'high': 2}
RELIABILITY_LABEL = {0: 'low', 1: 'medium', 2: 'high'}


def get_statewide_background_rates() -> Dict[str, float]:
    """Statewide annual incidence rate per 100,000 used as the prior mean.

    Reads the statewide_summary block from the real-data file and divides
    average annual case counts by the Wisconsin population. Falls back to
    epidemiologically reasonable defaults if the file is missing or has
    malformed entries (Lyme ~88/100k, WNV ~0.30/100k).
    """
    try:
        summary = load_real_vbd_data().get('statewide_summary', {}) or {}
        lyme_state_avg = float(summary.get('lyme', {}).get('avg_annual_recent') or 5223.0)
        wnv_state_avg = float(summary.get('wnv', {}).get('avg_annual') or 18.0)
    except Exception as e:
        logger.debug(f"Could not derive statewide VBD rates from summary: {e}")
        lyme_state_avg, wnv_state_avg = 5223.0, 18.0
    return {
        'lyme': lyme_state_avg * 100_000.0 / WI_POPULATION_2023,
        'wnv': wnv_state_avg * 100_000.0 / WI_POPULATION_2023,
    }


def apply_credibility_shrinkage(
    observed_rate: float,
    observed_cases: float,
    state_rate: float,
    prior_strength_k: float,
) -> Dict[str, float]:
    """Buhlmann credibility shrinkage of a county rate toward a state prior.

    weight = cases / (cases + k); shrunk = w * observed + (1-w) * state.
    Returns the shrunk rate and the credibility weight for transparency.
    A county with zero observed cases is fully shrunk to the state rate
    (weight = 0) and a county with case counts much larger than k is
    barely shrunk at all (weight -> 1).

    This is the standard Buhlmann linear credibility estimator and is a
    close empirical-Bayes approximation to the posterior mean of a
    Poisson-Gamma model when k is interpreted as a prior strength in
    annual-case-equivalents. A strict posterior-mean form would require
    explicit person-time exposure (population x years) and a fitted
    Gamma(alpha, beta) prior; we use the credibility approximation
    because the input data is reported as average annual rates rather
    than as case counts over a known person-time denominator.
    """
    if observed_cases is None or observed_cases < 0:
        observed_cases = 0.0
    if prior_strength_k <= 0:
        return {'rate': float(observed_rate or 0.0), 'weight': 1.0}
    w = observed_cases / (observed_cases + prior_strength_k)
    shrunk = w * float(observed_rate or 0.0) + (1.0 - w) * float(state_rate or 0.0)
    return {'rate': shrunk, 'weight': w}


def compute_reliability(annual_cases: float) -> str:
    """Classify a county-disease pair into low / medium / high reliability.

    Banding mirrors the prior-strength constants: counties below the prior
    strength are 'low' (their rate is being driven by the prior, not the
    data), counties at typical small-area-estimation reliable thresholds
    (>=10 events) are 'high', and the middle band is 'medium'.
    """
    cases = float(annual_cases or 0.0)
    if cases <= RELIABILITY_LOW_MAX:
        return 'low'
    if cases < RELIABILITY_HIGH_MIN:
        return 'medium'
    return 'high'


def combine_reliability(*tiers: str) -> str:
    """Combined reliability is the weakest input tier (precautionary)."""
    valid = [t for t in tiers if t in RELIABILITY_ORDER]
    if not valid:
        return 'low'
    return RELIABILITY_LABEL[min(RELIABILITY_ORDER[t] for t in valid)]


def poisson_rate_ci(
    annual_cases: float,
    annual_rate: float,
    confidence: float = 0.95,
) -> Dict[str, float]:
    """Approximate 95% CI for a Poisson incidence rate per 100,000.

    Uses the normal approximation rate_se = rate / sqrt(cases) for
    cases >= 1. For cases == 0 we apply the conventional Poisson(0)
    one-sided 95% upper bound of 3 expected events (the "rule of three"):
    if rate > 0 this translates to 3 * rate / cases on the rate scale,
    but since cases == 0 we instead back-derive person-years from the
    statewide WNV rate as a worst-case denominator and report the
    upper bound at that scale. When both rate and cases are zero we
    return a small but nonzero upper bound (the statewide WNV mean,
    ~0.31/100k) so the UI does not display a misleading 0-0 CI for
    counties that have simply not reported any cases yet. Lower bound
    is clamped at 0. The CI is intentionally coarse -- it is shown to
    users as a "this rate is uncertain" cue, not as a statistical
    inference for publication.
    """
    cases = float(annual_cases or 0.0)
    rate = float(annual_rate or 0.0)
    if cases <= 0:
        # Poisson rule of three: with 0 observed events, the 95% upper
        # bound on the true count is ~3. Translate to a rate bound by
        # using whichever denominator is informative.
        if rate > 0:
            # Should not happen (rate>0 implies cases>0) but handle defensively.
            return {'low': 0.0, 'high': rate * 3.0}
        # No cases AND no rate -- use the statewide WNV rate as a coarse
        # ceiling so the UI does not show 0-0 for zero-case counties.
        try:
            state = get_statewide_background_rates()
            ceiling = max(state.get('wnv', 0.3), 0.1)
        except Exception:
            ceiling = 0.3
        return {'low': 0.0, 'high': ceiling}
    if confidence != 0.95:
        # Only 95% supported; fall through to default rather than fail.
        pass
    se = rate / (cases ** 0.5) if cases > 0 else 0.0
    low = max(0.0, rate - 1.96 * se)
    high = rate + 1.96 * se
    return {'low': low, 'high': high}


def rate_to_score(rate: float, disease: str = 'lyme') -> float:
    if disease == 'lyme':
        if rate >= 200:
            return 0.95
        elif rate >= 100:
            return 0.75 + (rate - 100) * 0.002
        elif rate >= 50:
            return 0.55 + (rate - 50) * 0.004
        elif rate >= 20:
            return 0.35 + (rate - 20) * 0.0067
        elif rate >= 5:
            return 0.15 + (rate - 5) * 0.0133
        else:
            return max(0.05, rate * 0.03)
    else:
        if rate >= 10:
            return 0.90
        elif rate >= 5:
            return 0.60 + (rate - 5) * 0.06
        elif rate >= 2.5:
            return 0.40 + (rate - 2.5) * 0.08
        elif rate >= 0.5:
            return 0.15 + (rate - 0.5) * 0.125
        else:
            return max(0.05, rate * 0.30)


def _fetch_csv(url: str, timeout: int = 30) -> Optional[List[Dict[str, str]]]:
    # Cache-only enforcement: WI DHS EPHT vector-borne CSVs are warmed
    # weekly by the scheduler. See utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch(f"wi_dhs_epht_csv:{url.rsplit('/', 1)[-1]}")
        return None
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; CARA/1.0; Wisconsin Public Health Assessment)',
            'Accept': 'text/csv, application/csv, */*'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'csv' not in content_type and 'text' not in content_type:
            logger.warning(f"Unexpected content-type from {url}: {content_type}")

        text = response.text
        if len(text) < 100:
            logger.warning(f"CSV response too short from {url}: {len(text)} bytes")
            return None

        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            logger.warning(f"No rows parsed from CSV at {url}")
            return None

        logger.info(f"Fetched {len(rows)} rows from {url}")
        return rows

    except requests.RequestException as e:
        logger.error(f"HTTP error fetching CSV from {url}: {e}")
        return None
    except csv.Error as e:
        logger.error(f"CSV parsing error from {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching CSV from {url}: {e}")
        return None


def _parse_lyme_county_csv(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    county_data = {}

    count_rows = [r for r in rows if r.get('Sub-topic') == 'Counts']
    rate_rows = [r for r in rows if r.get('Sub-topic') == 'Crude Rates per 100,000']

    all_years = set()
    for r in count_rows:
        try:
            yr = int(r['Year'])
            all_years.add(yr)
        except (ValueError, KeyError):
            pass

    if not all_years:
        logger.warning("No valid years found in Lyme county CSV")
        return county_data

    max_year = max(all_years)
    min_recent_year = max_year - RECENT_YEARS_WINDOW + 1
    recent_years = [y for y in all_years if y >= min_recent_year]

    county_counts = defaultdict(lambda: defaultdict(dict))
    for r in count_rows:
        try:
            county = r['County']
            year = int(r['Year'])
            confirmed = int(r['Number Confirmed']) if r.get('Number Confirmed') else 0
            probable = int(r['Number Probable']) if r.get('Number Probable') else 0
            total = int(r['Number Total']) if r.get('Number Total') else confirmed + probable
            county_counts[county][year] = {
                'confirmed': confirmed,
                'probable': probable,
                'total': total,
            }
        except (ValueError, KeyError):
            continue

    county_rates = defaultdict(dict)
    for r in rate_rows:
        try:
            county = r['County']
            year = int(r['Year'])
            rate = float(r['Crude Rate']) if r.get('Crude Rate') else None
            if rate is not None:
                county_rates[county][year] = rate
        except (ValueError, KeyError):
            continue

    for county in county_counts:
        recent_count_data = {y: d for y, d in county_counts[county].items() if y in recent_years}
        if not recent_count_data:
            continue

        recent_totals = [d['total'] for d in recent_count_data.values()]
        recent_confirmed = [d['confirmed'] for d in recent_count_data.values()]
        avg_annual_cases = round(sum(recent_totals) / len(recent_totals), 1)
        avg_annual_confirmed = round(sum(recent_confirmed) / len(recent_confirmed), 1)

        recent_rate_data = {y: r for y, r in county_rates.get(county, {}).items() if y in recent_years}
        if recent_rate_data:
            avg_rate = round(sum(recent_rate_data.values()) / len(recent_rate_data), 1)
        else:
            avg_rate = None

        latest_year_total = county_counts[county].get(max_year, {}).get('total')
        latest_year_rate = county_rates.get(county, {}).get(max_year)

        year_by_year = {}
        for y in sorted(recent_count_data.keys()):
            entry = {'total': recent_count_data[y]['total']}
            if y in county_rates.get(county, {}):
                entry['rate'] = county_rates[county][y]
            year_by_year[str(y)] = entry

        county_data[county] = {
            'lyme_avg_annual_rate': avg_rate,
            'lyme_avg_annual_cases': avg_annual_cases,
            'lyme_avg_annual_confirmed': avg_annual_confirmed,
            'lyme_latest_year': max_year,
            'lyme_latest_cases': latest_year_total,
            'lyme_latest_rate': latest_year_rate,
            'lyme_data_years': sorted(recent_count_data.keys()),
            'lyme_year_by_year': year_by_year,
        }

    logger.info(f"Parsed Lyme data for {len(county_data)} counties, years {min_recent_year}-{max_year}")
    return county_data


def _parse_wnv_county_csv(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    county_data = {}

    single_year_all = [
        r for r in rows
        if r.get('range') == 'Single Year'
        and r.get('disease') == 'All'
        and r.get('SUB_TOPIC') == 'Counts'
        and r.get('COUNTY', '') != 'All'
    ]

    all_years = set()
    for r in single_year_all:
        try:
            yr = int(r['Year'])
            all_years.add(yr)
        except (ValueError, KeyError):
            pass

    if not all_years:
        logger.warning("No valid years found in WNV county CSV")
        return county_data

    max_year = max(all_years)
    min_recent_year = max_year - RECENT_YEARS_WINDOW + 1
    recent_years = [y for y in all_years if y >= min_recent_year]

    five_yr_min = max_year - 4
    five_yr_range = [y for y in all_years if y >= five_yr_min]

    county_yearly = defaultdict(lambda: defaultdict(int))
    for r in single_year_all:
        try:
            county = r['COUNTY']
            year = int(r['Year'])
            total = int(r['COUNT_TOTAL']) if r.get('COUNT_TOTAL') else 0
            county_yearly[county][year] = total
        except (ValueError, KeyError):
            continue

    rate_rows = [
        r for r in rows
        if r.get('range') == 'Single Year'
        and r.get('disease') == 'All'
        and r.get('SUB_TOPIC') == 'Crude Rates per 100,000'
        and r.get('COUNTY', '') != 'All'
    ]
    county_rates = defaultdict(dict)
    for r in rate_rows:
        try:
            county = r['COUNTY']
            year = int(r['Year'])
            rate = float(r['CRUDERATE']) if r.get('CRUDERATE') else None
            if rate is not None:
                county_rates[county][year] = rate
        except (ValueError, KeyError):
            continue

    for county in county_yearly:
        five_yr_totals = [county_yearly[county].get(y, 0) for y in five_yr_range]
        total_5yr = sum(five_yr_totals)

        recent_totals = [county_yearly[county].get(y, 0) for y in recent_years]
        avg_annual = round(sum(recent_totals) / len(recent_totals), 2) if recent_totals else 0

        recent_rate_vals = [county_rates.get(county, {}).get(y) for y in recent_years]
        recent_rate_vals = [r for r in recent_rate_vals if r is not None]
        avg_rate = round(sum(recent_rate_vals) / len(recent_rate_vals), 1) if recent_rate_vals else 0

        county_data[county] = {
            'wnv_total_cases_5yr': total_5yr,
            'wnv_avg_annual_cases': avg_annual,
            'wnv_avg_annual_rate': avg_rate,
            'wnv_latest_year': max_year,
            'wnv_latest_cases': county_yearly[county].get(max_year, 0),
        }

    logger.info(f"Parsed WNV data for {len(county_data)} counties, years {min_recent_year}-{max_year}")
    return county_data


def _parse_lyme_state_csv(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    statewide = {}

    count_rows = [r for r in rows if r.get('Sub Topic') == 'Counts (All)']
    for r in count_rows:
        try:
            year = int(r.get('Select a year', ''))
            total = int(r.get('Number Total', '') or r.get('Number Confirmed', '') or 0)
            if total > 0:
                statewide[f'cases_{year}'] = total
        except (ValueError, KeyError):
            continue

    if statewide:
        years = sorted([int(k.replace('cases_', '')) for k in statewide if k.startswith('cases_')])
        if years:
            latest = years[-1]
            statewide['latest_year'] = latest
            statewide['latest_cases'] = statewide.get(f'cases_{latest}', 0)
            recent_5 = years[-5:]
            avg = sum(statewide.get(f'cases_{y}', 0) for y in recent_5) / len(recent_5)
            statewide['avg_annual_cases_recent'] = round(avg, 0)

    logger.info(f"Parsed statewide Lyme data: {len(statewide)} entries")
    return statewide


def _parse_wnv_state_csv(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    statewide = {}

    count_rows = [
        r for r in rows
        if r.get('COUNTY', '') == 'All'
        and r.get('range') == 'Single Year'
        and r.get('disease') == 'All'
        and r.get('SUB_TOPIC') == 'Counts'
    ]

    for r in count_rows:
        try:
            year = int(r.get('Year', ''))
            total = int(r.get('COUNT_TOTAL', '') or 0)
            statewide[f'cases_{year}'] = total
        except (ValueError, KeyError):
            continue

    if statewide:
        years = sorted([int(k.replace('cases_', '')) for k in statewide if k.startswith('cases_')])
        if years:
            latest = years[-1]
            statewide['latest_year'] = latest
            statewide['latest_cases'] = statewide.get(f'cases_{latest}', 0)
            recent_5 = years[-5:]
            avg = sum(statewide.get(f'cases_{y}', 0) for y in recent_5) / len(recent_5)
            statewide['avg_annual_cases'] = round(avg, 1)

    logger.info(f"Parsed statewide WNV data: {len(statewide)} entries")
    return statewide


def fetch_dhs_county_data() -> Dict[str, Any]:
    result = {
        'county_data': {},
        'statewide_lyme': {},
        'statewide_wnv': {},
        'fetched_at': datetime.now().isoformat(),
        'success': False,
        'sources': [],
        'errors': []
    }

    lyme_rows = _fetch_csv(DHS_LYME_COUNTY_CSV_URL)
    if lyme_rows:
        lyme_county = _parse_lyme_county_csv(lyme_rows)
        for county, data in lyme_county.items():
            if county not in result['county_data']:
                result['county_data'][county] = {}
            result['county_data'][county].update(data)
        result['sources'].append(DHS_LYME_COUNTY_CSV_URL)
    else:
        result['errors'].append('Failed to fetch Lyme county CSV')

    wnv_rows = _fetch_csv(DHS_WNV_COUNTY_CSV_URL)
    if wnv_rows:
        wnv_county = _parse_wnv_county_csv(wnv_rows)
        for county, data in wnv_county.items():
            if county not in result['county_data']:
                result['county_data'][county] = {}
            result['county_data'][county].update(data)
        result['sources'].append(DHS_WNV_COUNTY_CSV_URL)
    else:
        result['errors'].append('Failed to fetch WNV county CSV')

    lyme_state_rows = _fetch_csv(DHS_LYME_STATE_CSV_URL)
    if lyme_state_rows:
        result['statewide_lyme'] = _parse_lyme_state_csv(lyme_state_rows)
        result['sources'].append(DHS_LYME_STATE_CSV_URL)

    wnv_state_rows = _fetch_csv(DHS_WNV_STATE_CSV_URL)
    if wnv_state_rows:
        result['statewide_wnv'] = _parse_wnv_state_csv(wnv_state_rows)
        result['sources'].append(DHS_WNV_STATE_CSV_URL)

    if result['county_data']:
        result['success'] = True

    return result


def _build_real_data_json(county_data: Dict[str, Dict[str, Any]],
                          statewide_lyme: Dict[str, Any],
                          statewide_wnv: Dict[str, Any]) -> Dict[str, Any]:
    all_lyme_years = set()
    for cd in county_data.values():
        all_lyme_years.update(cd.get('lyme_data_years', []))

    if all_lyme_years:
        data_years = f"{min(all_lyme_years)}-{max(all_lyme_years)}"
    else:
        data_years = "unknown"

    formatted_counties = {}
    for county, data in county_data.items():
        formatted_counties[county] = {
            'lyme_avg_annual_rate': data.get('lyme_avg_annual_rate', 0),
            'lyme_avg_annual_cases': data.get('lyme_avg_annual_cases', 0),
            'lyme_avg_annual_confirmed': data.get('lyme_avg_annual_confirmed', 0),
            'wnv_avg_annual_rate': data.get('wnv_avg_annual_rate', 0),
            'wnv_total_cases_5yr': data.get('wnv_total_cases_5yr', 0),
            'wnv_avg_annual_cases': data.get('wnv_avg_annual_cases', 0),
            'population_2023': None,
        }

    lyme_latest_year = statewide_lyme.get('latest_year')
    lyme_latest_cases = statewide_lyme.get('latest_cases', 0)
    wnv_latest_cases = statewide_wnv.get('latest_cases', 0)
    wnv_avg = statewide_wnv.get('avg_annual_cases', 18)

    return {
        'metadata': {
            'description': 'County-level vector-borne disease case data for Wisconsin from WI DHS EPHT CSV downloads',
            'version': '3.0.0',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'data_years': data_years,
            'sources': {
                'lyme_disease': {
                    'primary': 'Wisconsin DHS Environmental Public Health Tracking Program (EPHT)',
                    'url': DHS_LYME_COUNTY_CSV_URL,
                    'data_system': 'Wisconsin Electronic Disease Surveillance System (WEDSS)',
                    'notes': 'County-level confirmed/probable case counts and crude rates per 100,000. Case definition changed Jan 2022 (lab-based).'
                },
                'west_nile_virus': {
                    'primary': 'Wisconsin DHS Environmental Public Health Tracking Program (EPHT)',
                    'url': DHS_WNV_COUNTY_CSV_URL,
                    'data_system': 'Wisconsin Electronic Disease Surveillance System (WEDSS)',
                    'notes': 'County-level confirmed/probable case counts. Includes neuroinvasive and non-neuroinvasive. 80% of infections asymptomatic.'
                },
                'statewide_totals': {
                    'lyme_latest_year': lyme_latest_year,
                    'lyme_latest_cases': lyme_latest_cases,
                    'wnv_latest_cases': wnv_latest_cases,
                    'wnv_avg_annual': wnv_avg,
                    'source': f'WI DHS EPHT CSV downloads, fetched {datetime.now().strftime("%Y-%m-%d")}'
                }
            },
            'methodology': 'County-level incidence rates from official WI DHS EPHT CSV data downloads. Crude rates per 100,000 population. Multi-year averages computed from the most recent 6 years of available data.'
        },
        'statewide_summary': {
            'lyme': {
                'total_cases_latest': lyme_latest_cases,
                'latest_year': lyme_latest_year,
                'avg_annual_recent': statewide_lyme.get('avg_annual_cases_recent', 0),
                'trend': 'increasing',
                'trend_note': 'Incidence has increased significantly over past 20 years per WI DHS',
                'case_definition_change_2022': True,
            },
            'wnv': {
                'total_cases_latest': wnv_latest_cases,
                'latest_year': statewide_wnv.get('latest_year'),
                'avg_annual': wnv_avg,
                'underreporting_note': '80% of WNV infections are asymptomatic; reported cases represent severe illness'
            }
        },
        'county_data': formatted_counties
    }


def refresh_all_dhs_vbd_surveillance() -> Dict[str, Any]:
    app = None
    try:
        from main import app as flask_app
        app = flask_app
    except ImportError:
        logger.error("Could not import Flask app")
        return {'error': 'No Flask app available', 'success': False}

    with app.app_context():
        from utils.data_cache_manager import save_cached_data

        fetch_result = fetch_dhs_county_data()

        if fetch_result['success']:
            new_json = _build_real_data_json(
                fetch_result['county_data'],
                fetch_result.get('statewide_lyme', {}),
                fetch_result.get('statewide_wnv', {})
            )

            json_path = 'data/disease/wisconsin_vbd_real_data.json'
            try:
                with open(json_path, 'w') as f:
                    json.dump(new_json, f, indent=2)
                logger.info(f"Updated {json_path} with {len(new_json['county_data'])} counties")
            except Exception as e:
                logger.error(f"Failed to write {json_path}: {e}")

            invalidate_cache()

            save_cached_data(
                source_type='dhs_vbd_surveillance',
                data={
                    'county_count': len(fetch_result['county_data']),
                    'sources': fetch_result['sources'],
                    'fetched_at': fetch_result['fetched_at'],
                },
                county_name='_statewide',
                api_source=', '.join(fetch_result['sources']),
                used_fallback=False
            )

            for county, county_data in fetch_result['county_data'].items():
                save_cached_data(
                    source_type='dhs_vbd_surveillance',
                    data=county_data,
                    county_name=county,
                    api_source=', '.join(fetch_result['sources']),
                    used_fallback=False
                )

            logger.info(f"Saved VBD surveillance data for {len(fetch_result['county_data'])} counties to cache")

            try:
                from utils.persistent_cache import clear_cache_by_prefix
                clear_cache_by_prefix('dashboard_full_')
                logger.info("Cleared dashboard cache after VBD data refresh")
            except Exception as e:
                logger.warning(f"Could not clear dashboard cache: {e}")
        else:
            save_cached_data(
                source_type='dhs_vbd_surveillance',
                data={
                    'fetched_at': datetime.now().isoformat(),
                    'note': 'CSV fetch failed, using existing baseline',
                    'errors': fetch_result.get('errors', [])
                },
                county_name='_statewide',
                api_source=DHS_LYME_COUNTY_CSV_URL,
                used_fallback=True,
                fallback_reason='DHS EPHT CSV download failed'
            )

        return {
            'source_type': 'dhs_vbd_surveillance',
            'success': fetch_result['success'],
            'county_count': len(fetch_result.get('county_data', {})),
            'sources': fetch_result.get('sources', []),
            'errors': fetch_result.get('errors', []),
            'fetched_at': fetch_result.get('fetched_at', datetime.now().isoformat())
        }
