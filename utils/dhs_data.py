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
from utils.web_scraper import get_wi_dhs_respiratory_data, get_county_respiratory_data

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
    
    # NOTE: The legacy DHS GIS MapServer (DHS_COVID19/COVID19_WI) was retired and
    # returns HTTP 404. It has been removed from the fallback chain. The primary
    # source is the WI DHS respiratory surveillance web scraper. If that fails,
    # the backup falls through to rank-based synthetic data generation.
    try:
        # Primary: WI DHS respiratory surveillance web scraper
        respiratory_data = get_county_respiratory_data(county_name)
        
        if respiratory_data and 'error' not in respiratory_data:
            disease_data = {
                'county': county_name,
                'disease_type': disease_type,
                'data_source': 'Wisconsin DHS (Web Scraping)',
                'last_updated': respiratory_data.get('last_updated', datetime.now().isoformat()),
                'risk_score': respiratory_data.get('risk_score', 0.3),
                'activity_levels': respiratory_data.get('activity_levels', {}),
                'trend_indicators': respiratory_data.get('trend_indicators', 'stable'),
                'key_findings': respiratory_data.get('key_findings', [])
            }
            
            activity_levels = respiratory_data.get('activity_levels', {})
            if disease_type.lower() in ['flu', 'influenza']:
                disease_data['activity_level'] = activity_levels.get('influenza', 'minimal')
            elif disease_type.lower() in ['covid', 'covid-19']:
                disease_data['activity_level'] = activity_levels.get('covid_19', 'minimal')
            elif disease_type.lower() == 'rsv':
                disease_data['activity_level'] = activity_levels.get('rsv', 'minimal')
            else:
                disease_data['activity_level'] = 'minimal'
            
            set_in_persistent_cache(cache_key, disease_data, DHS_CACHE_EXPIRY)
            logger.info(f"Successfully retrieved real {disease_type} data for {county_name}")
            return disease_data
        
        # Fallback: rank-based synthetic generation when scraper returns no data
        logger.info(f"Web scraper returned no {disease_type} data for {county_name}; using backup generation")
        data = _generate_backup_data(county_name, disease_type)
        set_in_persistent_cache(cache_key, data, expiry_days=DHS_CACHE_EXPIRY)
        return data

    except Exception as e:
        logger.error(f"Error fetching {disease_type} data for {county_name}: {str(e)}")
        return _generate_backup_data(county_name, disease_type)

def _process_flu_data(data: Dict[str, Any], county_name: str) -> Dict[str, Any]:
    """
    Process flu data from DHS API response.
    """
    # Example field mappings - adjust based on actual API response
    cases = data.get('CASES', 0)
    population = data.get('POPULATION', 100000)
    cases_per_100k = (cases / population) * 100000 if population > 0 else 0
    
    # Determine activity level based on cases per 100k
    activity_level = "low"
    if cases_per_100k >= 50:
        activity_level = "very high"
    elif cases_per_100k >= 30:
        activity_level = "high"
    elif cases_per_100k >= 10:
        activity_level = "moderate"
    
    # Determine trend based on previous data
    trend = data.get('TREND', 'stable')
    
    result = {
        'disease_type': 'flu',
        'county': county_name,
        'cases': cases,
        'cases_per_100k': cases_per_100k,
        'activity_level': activity_level,
        'trend': trend,
        'last_updated': data.get('DATEUPDATED', datetime.now().isoformat()),
        'data_quality': 'high',
        'source': 'Wisconsin DHS'
    }
    
    return result

def _process_covid_data(data: Dict[str, Any], county_name: str) -> Dict[str, Any]:
    """
    Process COVID-19 data from DHS API response.
    """
    # Example field mappings - adjust based on actual API response
    cases = data.get('CONFIRMED_CASES', 0)
    population = data.get('POPULATION', 100000)
    cases_per_100k = (cases / population) * 100000 if population > 0 else 0
    
    # Determine activity level based on cases per 100k
    activity_level = "low"
    if cases_per_100k >= 100:
        activity_level = "very high"
    elif cases_per_100k >= 50:
        activity_level = "high"
    elif cases_per_100k >= 20:
        activity_level = "moderate"
    
    # Determine trend based on previous data
    trend = data.get('TREND', 'stable')
    
    result = {
        'disease_type': 'covid',
        'county': county_name,
        'cases': cases,
        'cases_per_100k': cases_per_100k,
        'activity_level': activity_level,
        'trend': trend,
        'last_updated': data.get('DATE_UPDATED', datetime.now().isoformat()),
        'data_quality': 'high',
        'source': 'Wisconsin DHS'
    }
    
    return result

def _process_rsv_data(data: Dict[str, Any], county_name: str) -> Dict[str, Any]:
    """
    Process RSV data from DHS API response.
    """
    # Example field mappings - adjust based on actual API response
    cases = data.get('CASES', 0)
    population = data.get('POPULATION', 100000)
    cases_per_100k = (cases / population) * 100000 if population > 0 else 0
    
    # Determine activity level based on cases per 100k
    activity_level = "low"
    if cases_per_100k >= 30:
        activity_level = "very high"
    elif cases_per_100k >= 20:
        activity_level = "high"
    elif cases_per_100k >= 10:
        activity_level = "moderate"
    
    # Determine trend based on previous data
    trend = data.get('TREND', 'stable')
    
    result = {
        'disease_type': 'rsv',
        'county': county_name,
        'cases': cases,
        'cases_per_100k': cases_per_100k,
        'activity_level': activity_level,
        'trend': trend,
        'last_updated': data.get('LAST_UPDATED', datetime.now().isoformat()),
        'data_quality': 'high',
        'source': 'Wisconsin DHS'
    }
    
    return result

def _generate_backup_data(county_name: str, disease_type: str) -> Dict[str, Any]:
    """
    Generate backup data for a county when real API data cannot be retrieved.
    This uses realistic but not necessarily current values.
    """
    # County health rankings can influence the base rates
    # Higher health rank = lower disease risk
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
    
    # Default rank if county not found
    rank = health_ranks.get(county_name, 35)
    
    # Invert and normalize rank score (1 = best health, 72 = worst health)
    # Higher numbers mean higher risk
    health_factor = (rank / 72.0) * 0.5  # Scale to 0-0.5 range
    
    # Seasonal factors - certain diseases are more prevalent in certain seasons
    current_month = datetime.now().month
    seasonal_factors = {
        "flu": 0.8 if 10 <= current_month <= 4 else 0.2,  # Higher in winter months
        "covid": 0.6,  # Fairly consistent year-round with slight seasonal variation
        "rsv": 0.7 if 9 <= current_month <= 3 else 0.3,  # Higher in fall/winter
    }
    
    # Disease-specific base rates
    base_rates = {
        "flu": 15.0,
        "covid": 25.0,
        "rsv": 10.0
    }
    
    # Calculate cases per 100k using health ranking and seasonal factors
    seasonal_factor = seasonal_factors.get(disease_type.lower(), 0.5)
    base_rate = base_rates.get(disease_type.lower(), 15.0)
    
    # Use deterministic value instead of random variation
    random_factor = 1.0
    
    # Calculate cases per 100k
    cases_per_100k = base_rate * (1 + health_factor) * seasonal_factor * random_factor
    
    # Determine activity level
    activity_level = "low"
    if cases_per_100k >= 50:
        activity_level = "very high"
    elif cases_per_100k >= 25:
        activity_level = "high"
    elif cases_per_100k >= 10:
        activity_level = "moderate"
    
    # Use stable trend instead of randomized selection
    trend = "stable"
    
    # Format the date to match API response format
    last_updated = datetime.now().isoformat()
    
    result = {
        'disease_type': disease_type.lower(),
        'county': county_name,
        'cases_per_100k': round(cases_per_100k, 1),
        'activity_level': activity_level,
        'trend': trend,
        'last_updated': last_updated,
        'data_quality': 'estimated',
        'source': 'Estimated from County Health Rankings (not real-time DHS data)'
    }
    
    return result

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