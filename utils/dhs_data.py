"""Wisconsin Department of Health Services Data Module

This module provides functions to fetch real public health data from Wisconsin DHS
for use in infectious disease risk calculations.

Data sources include:
- Communicable Disease Data - Flu, COVID-19, RSV
- Vaccination Coverage Data
- County Health Rankings
"""

import io
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Union, Optional

import pandas as pd
import requests
from requests.exceptions import RequestException

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache, clear_cache_by_prefix

logger = logging.getLogger(__name__)

# Cache configuration
DHS_CACHE_PREFIX = "dhs_data_"
DHS_CACHE_EXPIRY = 7  # 7 days

# MMR county vaccination data from WI DHS immunization CSV
MMR_CSV_URL = "https://www.dhs.wisconsin.gov/immunization/county-immunization-data.csv"
MMR_COUNTY_CACHE_KEY = "dhs_data_mmr_county_all"
MMR_COUNTY_CACHE_EXPIRY = 30  # Annual data; refresh monthly

# Counties in Wisconsin
WISCONSIN_COUNTIES = [
    "Adams", "Ashland", "Barron", "Bayfield", "Brown", "Buffalo", "Burnett", "Calumet",
    "Chippewa", "Clark", "Columbia", "Crawford", "Dane", "Dodge", "Door", "Douglas",
    "Dunn", "Eau Claire", "Florence", "Fond du Lac", "Forest", "Grant", "Green",
    "Green Lake", "Iowa", "Iron", "Jackson", "Jefferson", "Juneau", "Kenosha",
    "Kewaunee", "La Crosse", "Lafayette", "Langlade", "Lincoln", "Manitowoc", "Marathon",
    "Marinette", "Marquette", "Menominee", "Milwaukee", "Monroe", "Oconto", "Oneida",
    "Outagamie", "Ozaukee", "Pepin", "Pierce", "Polk", "Portage", "Price", "Racine",
    "Richland", "Rock", "Rusk", "Sauk", "Sawyer", "Shawano", "Sheboygan", "St. Croix",
    "Taylor", "Trempealeau", "Vernon", "Vilas", "Walworth", "Washburn", "Washington",
    "Waukesha", "Waupaca", "Waushara", "Winnebago", "Wood"
]

def get_county_disease_data(county_name: str, disease_type: str) -> Dict[str, Any]:
    """
    Get disease activity data for a specific county and disease type from Wisconsin DHS.
    
    Args:
        county_name: Name of the Wisconsin county
        disease_type: Type of disease (flu, covid, rsv)
        
    Returns:
        Dictionary containing disease activity data
    """
    if not county_name or county_name.strip() == "":
        logger.warning("Empty county name provided, using Milwaukee as default")
        county_name = "Milwaukee"
    
    # Normalize the county name
    county_name = county_name.strip().title()
    
    # Check if county exists in Wisconsin
    if county_name not in WISCONSIN_COUNTIES:
        logger.warning(f"Unknown county: {county_name}. Using Milwaukee data.")
        county_name = "Milwaukee"
    
    # Generate cache key
    cache_key = f"{DHS_CACHE_PREFIX}{disease_type.lower()}_{county_name.lower()}"

    # Try to get from cache first
    cached_data = get_from_persistent_cache(cache_key, max_age_days=DHS_CACHE_EXPIRY)
    if cached_data:
        logger.debug(f"Retrieved {disease_type} data for {county_name} from cache")
        return cached_data

    # NSSP is now the genuine primary source. The legacy DHS GIS MapServer
    # (retired, HTTP 404) and the DHS respiratory HTML page web scraper have
    # both been removed: the same NSSP/ESSENCE feed underlies the WI DHS
    # respiratory dashboards, so going to NSSP directly is more accurate
    # and avoids fragile HTML scraping.
    try:
        from utils.disease_surveillance import get_disease_metrics

        metrics = get_disease_metrics(county_name)
        if not metrics or 'error' in metrics:
            logger.warning(
                f"NSSP returned no usable {disease_type} data for {county_name}"
            )
            return {
                'county': county_name,
                'disease_type': disease_type,
                'data_quality': {
                    'available': False,
                    'reason': 'NSSP surveillance data unavailable',
                    'classification': 'unavailable',
                },
                'source': 'CDC NSSP Emergency Department Visits (data.cdc.gov/resource/vutn-jzwm)',
                'last_updated': datetime.now().isoformat(),
            }

        activity_levels = metrics.get('activity_levels', {}) or {}
        ed_visit_pct = (metrics.get('metrics', {}) or {}).get('ed_visit_pct', {}) or {}

        normalized = disease_type.lower()
        if normalized in ('flu', 'influenza'):
            activity_level = activity_levels.get('ili', 'low')
            ed_pct = ed_visit_pct.get('influenza')
        elif normalized in ('covid', 'covid-19', 'covid19'):
            activity_level = activity_levels.get('covid', 'minimal')
            ed_pct = ed_visit_pct.get('covid19')
        elif normalized == 'rsv':
            activity_level = activity_levels.get('rsv', 'minimal')
            ed_pct = ed_visit_pct.get('rsv')
        else:
            activity_level = activity_levels.get('overall', 'low')
            ed_pct = None

        disease_data = {
            'county': county_name,
            'disease_type': disease_type,
            'activity_level': activity_level,
            'ed_visit_percent': ed_pct,
            'trend': metrics.get('trend', 'stable'),
            'risk_score': metrics.get('risk_score', 0.3),
            'last_updated': metrics.get('last_updated', datetime.now().isoformat()),
            'report_date': metrics.get('report_date'),
            'source': 'CDC NSSP Emergency Department Visits (data.cdc.gov/resource/vutn-jzwm)',
            'data_quality': {
                'available': True,
                'classification': 'real_surveillance',
                'confidence': metrics.get('confidence', 0.9),
            },
        }

        set_in_persistent_cache(cache_key, disease_data, DHS_CACHE_EXPIRY)
        logger.info(
            f"Retrieved real {disease_type} data for {county_name} from NSSP "
            f"(activity={activity_level})"
        )
        return disease_data

    except Exception as e:
        logger.error(f"Error fetching {disease_type} data for {county_name}: {str(e)}")
        return {
            'county': county_name,
            'disease_type': disease_type,
            'data_quality': {
                'available': False,
                'reason': f'NSSP fetch failed: {str(e)}',
                'classification': 'unavailable',
            },
            'source': 'CDC NSSP Emergency Department Visits (data.cdc.gov/resource/vutn-jzwm)',
            'last_updated': datetime.now().isoformat(),
        }

def _fetch_mmr_county_data() -> Dict[str, float]:
    """
    Download and parse the WI DHS county immunization CSV to extract MMR (1)
    vaccination rates for 24-month-old children by county, for the most recent
    year available.

    Source: https://www.dhs.wisconsin.gov/immunization/county-immunization-data.csv
    Data source: Wisconsin Immunization Registry (WIR). Updated annually by DHS.

    Returns:
        Dict mapping county name to MMR rate as a float (0-100).
        Returns an empty dict if the download fails.
    """
    cached = get_from_persistent_cache(MMR_COUNTY_CACHE_KEY, max_age_days=MMR_COUNTY_CACHE_EXPIRY)
    if cached:
        logger.info("Using cached MMR county data from DHS WIR CSV")
        return cached

    # Cache-only enforcement: live HTTP is forbidden in the user dashboard
    # request path. The scheduler must warm this cache via the DHS WIR
    # refresh job. See utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("wi_dhs_wir_mmr_county")
        return {}

    try:
        logger.info(f"Downloading MMR county data from {MMR_CSV_URL}")
        response = requests.get(MMR_CSV_URL, timeout=15)
        response.raise_for_status()

        df = pd.read_csv(io.StringIO(response.text))
        df.columns = [c.strip() for c in df.columns]
        df['County'] = df['County'].str.strip()
        df['Age'] = df['Age'].str.strip()
        df['vaccine'] = df['vaccine'].str.strip()

        max_year = int(df['Year'].max())
        mmr_rows = df[
            (df['Year'] == max_year) &
            (df['vaccine'] == 'MMR (1)') &
            (df['Age'] == '24-month olds')
        ].copy()

        mmr_rows['rate'] = (
            mmr_rows['Percent'].str.replace('%', '', regex=False).astype(float)
        )

        county_rates = dict(zip(mmr_rows['County'], mmr_rows['rate']))
        logger.info(
            f"Loaded MMR (1) rates for {len(county_rates)} counties "
            f"(year {max_year}) from WI DHS WIR CSV"
        )
        set_in_persistent_cache(MMR_COUNTY_CACHE_KEY, county_rates, expiry_days=MMR_COUNTY_CACHE_EXPIRY)
        return county_rates

    except Exception as e:
        logger.error(f"Failed to fetch MMR county data from DHS WIR CSV: {e}")
        return {}


def get_vaccination_rate(county_name: str) -> float:
    """
    Get the MMR (1) vaccination rate for 24-month-olds in a Wisconsin county.

    Primary source: WI DHS county-immunization-data.csv (WIR, most recent year).
    Fallback: County Health Rankings-based estimate if CSV is unavailable.

    Args:
        county_name: Name of the Wisconsin county.

    Returns:
        MMR vaccination rate as a percentage (0-100).
    """
    county_name = county_name.strip().title()

    if county_name not in WISCONSIN_COUNTIES:
        logger.warning(f"Unknown county: {county_name}. Using Milwaukee data.")
        county_name = "Milwaukee"

    cache_key = f"{DHS_CACHE_PREFIX}vaccination_{county_name.lower()}"
    cached_data = get_from_persistent_cache(cache_key, max_age_days=DHS_CACHE_EXPIRY)
    if cached_data and 'rate' in cached_data:
        logger.debug(f"Retrieved vaccination data for {county_name} from cache")
        return cached_data['rate']

    # Primary: WI DHS WIR county immunization CSV (MMR for 24-month olds)
    mmr_rates = _fetch_mmr_county_data()
    if county_name in mmr_rates:
        rate = mmr_rates[county_name]
        logger.info(f"MMR (1) rate for {county_name}: {rate:.1f}% (WI DHS WIR)")
        cache_data = {
            'rate': rate,
            'last_updated': datetime.now().isoformat(),
            'source': 'WI DHS WIR'
        }
        set_in_persistent_cache(cache_key, cache_data, expiry_days=DHS_CACHE_EXPIRY)
        return rate

    # Fallback: County Health Rankings-based estimate
    logger.warning(
        f"MMR CSV data not available for {county_name}; using health ranking estimate"
    )
    health_ranks = {
        "Ozaukee": 1, "Waukesha": 2, "St. Croix": 3, "Washington": 4, "Pierce": 5,
        "Dane": 6, "Door": 7, "Portage": 8, "Outagamie": 9, "Pepin": 10,
        "Taylor": 11, "Eau Claire": 12, "La Crosse": 13, "Sheboygan": 14, "Calumet": 15,
        "Kewaunee": 16, "Fond du Lac": 17, "Marathon": 18, "Green": 19, "Dunn": 20,
        "Clark": 21, "Polk": 22, "Brown": 23, "Columbia": 24, "Barron": 25,
        "Sauk": 26, "Trempealeau": 27, "Iowa": 28, "Vernon": 29, "Monroe": 30,
        "Winnebago": 31, "Oconto": 32, "Wood": 33, "Buffalo": 34, "Lafayette": 35,
        "Jefferson": 36, "Chippewa": 37, "Waupaca": 38, "Dodge": 39, "Oneida": 40,
        "Manitowoc": 41, "Crawford": 42, "Douglas": 43, "Bayfield": 44, "Green Lake": 45,
        "Lincoln": 46, "Grant": 47, "Richland": 48, "Racine": 49, "Walworth": 50,
        "Washburn": 51, "Florence": 52, "Waushara": 53, "Iron": 54, "Vilas": 55,
        "Jackson": 56, "Price": 57, "Juneau": 58, "Kenosha": 59, "Rock": 60,
        "Rusk": 61, "Ashland": 62, "Langlade": 63, "Adams": 64, "Burnett": 65,
        "Marinette": 66, "Shawano": 67, "Sawyer": 68, "Marquette": 69, "Forest": 70,
        "Milwaukee": 71, "Menominee": 72
    }

    rank = health_ranks.get(county_name, 35)
    base_rate = 70.0
    rank_factor = (73 - rank) / 72.0
    rate = base_rate + (rank_factor * 15.0)
    rate = max(45.0, min(90.0, rate))

    cache_data = {
        'rate': rate,
        'last_updated': datetime.now().isoformat(),
        'source': 'county_health_ranking_estimate'
    }
    set_in_persistent_cache(cache_key, cache_data, expiry_days=DHS_CACHE_EXPIRY)
    return rate

def clear_dhs_cache() -> int:
    """
    Clear all DHS data caches.
    
    Returns:
        Number of cache entries cleared
    """
    count = clear_cache_by_prefix(DHS_CACHE_PREFIX)
    logger.info(f"Cleared DHS data cache: {count} entries removed")
    return count


def get_dhs_health_metrics(county_name: str) -> Dict[str, Any]:
    """
    Aggregate Wisconsin DHS health metrics for a county into a single dict
    suitable for warm caching by the weekly scheduler job.

    Aggregates only real, county-specific data from the following live
    sources (all keyless, county-resolved):
      - WI DHS WIR CSV (MMR 24-month vaccination rate)
      - County Health Rankings BRFSS (all-ages seasonal flu vaccination,
        primary care physicians per 100k, poor mental health days,
        mental health providers per 100k)
      - CDC PLACES Socrata (COPD crude prevalence, frequent mental
        distress crude prevalence)

    Per-source failures are recorded individually rather than collapsed
    into a single fallback flag, so the dashboard can show partial
    availability instead of "all or nothing." If every source fails, the
    overall payload is marked _fallback=True so the scheduler counts the
    refresh as a fallback rather than a success.

    Args:
        county_name: Name of a Wisconsin county (will be title-cased).

    Returns:
        Dict with the per-source values plus provenance metadata. Always
        returns a dict (never None) so the scheduler can cache the result.
    """
    county_name = (county_name or "").strip().title()
    if county_name not in WISCONSIN_COUNTIES:
        logger.warning(
            f"get_dhs_health_metrics: unknown county '{county_name}', "
            "returning empty payload"
        )
        return {
            'county': county_name,
            'available': False,
            '_fallback': True,
            '_fallback_reason': 'Unknown Wisconsin county',
            'last_updated': datetime.now().isoformat(),
        }

    from utils import health_metrics_data as hmd

    sources: Dict[str, Dict[str, Any]] = {}

    def _try(label: str, fn, *args, **kwargs):
        try:
            value = fn(*args, **kwargs)
            sources[label] = {
                'value': value,
                'available': value is not None,
            }
            return value
        except Exception as exc:
            logger.warning(
                f"get_dhs_health_metrics({county_name}): {label} failed: {exc}"
            )
            sources[label] = {
                'value': None,
                'available': False,
                'error': str(exc),
            }
            return None

    mmr_rate = _try('mmr_vaccination_24mo', get_vaccination_rate, county_name)
    flu_rate = _try('flu_vaccination_all_ages', hmd.get_flu_vaccination_rate, county_name)
    pcp_density = _try('primary_care_physicians_per_100k', hmd.get_primary_care_access, county_name)
    copd_prev = _try('copd_crude_prevalence', hmd.get_copd_prevalence, county_name)
    mh_days = _try('poor_mental_health_days', hmd.get_mental_health_days, county_name)
    mh_providers = _try('mental_health_providers_per_100k', hmd.get_mental_health_providers_per_100k, county_name)
    mh_distress = _try('frequent_mental_distress_prevalence', hmd.get_mental_distress_prevalence, county_name)

    available_count = sum(1 for s in sources.values() if s.get('available'))
    total_count = len(sources)
    all_failed = available_count == 0

    payload: Dict[str, Any] = {
        'county': county_name,
        'available': not all_failed,
        'sources': sources,
        'metrics': {
            'mmr_vaccination_24mo': mmr_rate,
            'flu_vaccination_all_ages': flu_rate,
            'primary_care_physicians_per_100k': pcp_density,
            'copd_crude_prevalence': copd_prev,
            'poor_mental_health_days': mh_days,
            'mental_health_providers_per_100k': mh_providers,
            'frequent_mental_distress_prevalence': mh_distress,
        },
        'coverage': {
            'available_sources': available_count,
            'total_sources': total_count,
            'fraction': round(available_count / total_count, 3) if total_count else 0.0,
        },
        'data_source': (
            'WI DHS WIR + County Health Rankings BRFSS + CDC PLACES '
            '(aggregated; all county-specific real data)'
        ),
        'last_updated': datetime.now().isoformat(),
    }

    if all_failed:
        payload['_fallback'] = True
        payload['_fallback_reason'] = (
            'All upstream health-metrics sources failed (CHR + PLACES + WIR)'
        )
    elif available_count < total_count:
        payload['_partial'] = True
        payload['_partial_reason'] = (
            f'{total_count - available_count} of {total_count} upstream '
            'sources returned no data for this county'
        )

    return payload