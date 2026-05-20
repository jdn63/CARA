"""County Health Metrics Data Module

Provides county-level communicable disease vulnerability and resilience metrics
from two publicly accessible, keyless data sources:

  1. County Health Rankings (CHR) annual CSV
     URL: https://www.countyhealthrankings.org/
     Metrics: flu vaccination rate, primary care physician access,
              poor mental health days, mental health providers per 100k
     Frequency: Annual (March release)

  2. CDC PLACES Local Data for Better Health (Socrata API)
     URL: https://data.cdc.gov/resource/swc5-untb.json
     Metrics: COPD prevalence, frequent mental distress prevalence (MHLTH)
     Frequency: Annual

Both sources are cached for 30 days (data refreshes annually).
"""

import io
import logging
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
import requests

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

# --- County Health Rankings ---
CHR_CSV_URL = (
    "https://www.countyhealthrankings.org/sites/default/files/media/document/"
    "analytic_data2025_v3.csv"
)
CHR_CACHE_KEY = "health_metrics_chr_wi_2025"
CHR_CACHE_EXPIRY = 30

# --- CDC PLACES ---
PLACES_API_URL = "https://data.cdc.gov/resource/swc5-untb.json"
PLACES_COPD_CACHE_KEY = "health_metrics_places_copd_wi"
PLACES_MHLTH_CACHE_KEY = "health_metrics_places_mhlth_wi"
PLACES_CACHE_EXPIRY = 30

# Wisconsin statewide fallback values (used when county data is unavailable)
WI_DEFAULTS = {
    "flu_vaccination_rate": 45.6,       # CHR 2025 WI mean
    "primary_care_per_100k": 65.0,      # Approximate WI average
    "copd_prevalence": 7.0,             # Approximate WI average
    "mental_health_days": 4.2,          # CHR WI mean (avg mentally unhealthy days/month)
    "mental_health_providers": 100.0,   # Approximate WI average per 100k
    "mental_distress_prevalence": 14.5, # CDC PLACES WI mean (% adults >= 14 poor mental health days)
}


# ---------------------------------------------------------------------------
# County Health Rankings helpers
# ---------------------------------------------------------------------------

def _fetch_chr_wi_data() -> Dict[str, Dict]:
    """
    Download and cache County Health Rankings 2025 CSV, returning a dict of
    county-level metrics keyed by county name (no 'County' suffix).

    Returns:
        {
          "Adams": {"flu_vax": 24.0, "pc_per_100k": 9.6},
          "Ashland": {...},
          ...
        }
        Returns empty dict on failure.
    """
    cached = get_from_persistent_cache(CHR_CACHE_KEY, max_age_days=CHR_CACHE_EXPIRY)
    if cached:
        logger.info("Using cached County Health Rankings data")
        return cached

    # Cache-only enforcement: live HTTP is forbidden in the user dashboard
    # request path. The scheduler must warm this cache. See
    # utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("county_health_rankings")
        return {}

    try:
        logger.info(f"Downloading County Health Rankings data from {CHR_CSV_URL}")
        resp = requests.get(CHR_CSV_URL, timeout=30)
        resp.raise_for_status()

        df = pd.read_csv(io.StringIO(resp.text), low_memory=False)

        # Filter to Wisconsin county rows (not the statewide summary row)
        wi = df[
            (df["State Abbreviation"] == "WI") &
            (df["Name"].str.endswith(" County", na=False))
        ].copy()

        # Strip " County" suffix to match CARA's county name convention
        wi["county"] = wi["Name"].str.replace(" County", "", regex=False).str.strip()

        result: Dict[str, Dict] = {}
        for _, row in wi.iterrows():
            county = row["county"]
            try:
                flu_raw = float(row.get("Flu Vaccinations raw value", float("nan")))
                flu_pct = round(flu_raw * 100.0, 1) if not pd.isna(flu_raw) else None
            except (ValueError, TypeError):
                flu_pct = None

            try:
                pc_raw = float(row.get("Primary Care Physicians raw value", float("nan")))
                pc_per_100k = round(pc_raw * 100000.0, 1) if not pd.isna(pc_raw) else None
            except (ValueError, TypeError):
                pc_per_100k = None

            # Poor Mental Health Days — average number of mentally unhealthy days/month
            # CHR raw value column stores the value in days (not a ratio), so no scaling needed
            try:
                mhd_raw = float(row.get("Poor Mental Health Days raw value", float("nan")))
                mental_health_days = round(mhd_raw, 2) if not pd.isna(mhd_raw) else None
            except (ValueError, TypeError):
                mental_health_days = None

            # Mental Health Providers — raw value is providers per person; scale to per-100k
            try:
                mhp_raw = float(row.get("Mental Health Providers raw value", float("nan")))
                mhp_per_100k = round(mhp_raw * 100000.0, 1) if not pd.isna(mhp_raw) else None
            except (ValueError, TypeError):
                mhp_per_100k = None

            result[county] = {
                "flu_vax": flu_pct,
                "pc_per_100k": pc_per_100k,
                "mental_health_days": mental_health_days,
                "mhp_per_100k": mhp_per_100k,
            }

        logger.info(
            f"Loaded County Health Rankings data for {len(result)} WI counties (CHR 2025)"
        )
        set_in_persistent_cache(CHR_CACHE_KEY, result, expiry_days=CHR_CACHE_EXPIRY)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch County Health Rankings data: {e}")
        return {}


def get_flu_vaccination_rate(county_name: str) -> Optional[float]:
    """
    Get county-level flu vaccination rate (%) from County Health Rankings.

    Source: BRFSS phone survey, CHR 2025. Range in Wisconsin: 22% to 69%.
    Represents all-ages seasonal flu coverage, not registry-based.

    Args:
        county_name: Wisconsin county name (e.g., 'Adams', 'St. Croix').

    Returns:
        Flu vaccination rate as a percentage (0-100), or None if unavailable.
    """
    county_name = county_name.strip().title()
    chr_data = _fetch_chr_wi_data()
    row = chr_data.get(county_name)
    if row and row.get("flu_vax") is not None:
        rate = row["flu_vax"]
        logger.debug(f"CHR flu vaccination rate for {county_name}: {rate:.1f}%")
        return rate
    logger.warning(
        f"CHR flu vaccination rate not available for {county_name}; "
        f"using WI default {WI_DEFAULTS['flu_vaccination_rate']}%"
    )
    return None


def get_primary_care_access(county_name: str) -> Optional[float]:
    """
    Get county-level primary care physician density from County Health Rankings.

    Source: CHR 2025. Range in Wisconsin: 9.6/100k (Adams) to 173.8/100k (Ashland).
    Low access indicates reduced resilience for managing outbreak surge.

    Args:
        county_name: Wisconsin county name (e.g., 'Adams', 'St. Croix').

    Returns:
        Primary care physicians per 100,000 population, or None if unavailable.
    """
    county_name = county_name.strip().title()
    chr_data = _fetch_chr_wi_data()
    row = chr_data.get(county_name)
    if row and row.get("pc_per_100k") is not None:
        rate = row["pc_per_100k"]
        logger.debug(f"CHR primary care access for {county_name}: {rate:.1f} per 100k")
        return rate
    logger.warning(
        f"CHR primary care access not available for {county_name}; "
        f"using WI default {WI_DEFAULTS['primary_care_per_100k']}/100k"
    )
    return None


def get_mental_health_days(county_name: str) -> Optional[float]:
    """
    Get county-level average mentally unhealthy days per month from County Health Rankings.

    Source: CHR 2025, derived from BRFSS survey question on number of days
    mental health was "not good" in the past 30 days. WI range roughly 3.0-5.5.

    Args:
        county_name: Wisconsin county name (e.g., 'Adams', 'St. Croix').

    Returns:
        Average mentally unhealthy days per month, or None if unavailable.
    """
    county_name = county_name.strip().title()
    chr_data = _fetch_chr_wi_data()
    row = chr_data.get(county_name)
    if row and row.get("mental_health_days") is not None:
        days = row["mental_health_days"]
        logger.debug(f"CHR mentally unhealthy days for {county_name}: {days:.2f}/month")
        return days
    logger.warning(
        f"CHR mental health days not available for {county_name}; "
        f"using WI default {WI_DEFAULTS['mental_health_days']} days/month"
    )
    return None


def get_mental_health_providers_per_100k(county_name: str) -> Optional[float]:
    """
    Get county-level mental health provider density from County Health Rankings.

    Source: CHR 2025. Covers psychiatrists, psychologists, licensed clinical
    social workers, counselors, and marriage and family therapists.
    Low access (fewer providers per 100k) indicates higher shortage risk.

    Args:
        county_name: Wisconsin county name (e.g., 'Adams', 'St. Croix').

    Returns:
        Mental health providers per 100,000 population, or None if unavailable.
    """
    county_name = county_name.strip().title()
    chr_data = _fetch_chr_wi_data()
    row = chr_data.get(county_name)
    if row and row.get("mhp_per_100k") is not None:
        rate = row["mhp_per_100k"]
        logger.debug(f"CHR mental health providers for {county_name}: {rate:.1f}/100k")
        return rate
    logger.warning(
        f"CHR mental health providers not available for {county_name}; "
        f"using WI default {WI_DEFAULTS['mental_health_providers']}/100k"
    )
    return None


# ---------------------------------------------------------------------------
# CDC PLACES COPD helper
# ---------------------------------------------------------------------------

def _fetch_places_copd_wi() -> Dict[str, float]:
    """
    Fetch COPD crude prevalence (%) for all Wisconsin counties via CDC PLACES API.

    Returns:
        {county_name: copd_pct, ...}  e.g. {"Adams": 10.1, "Waukesha": 4.1}
        Returns empty dict on failure.
    """
    cached = get_from_persistent_cache(PLACES_COPD_CACHE_KEY, max_age_days=PLACES_CACHE_EXPIRY)
    if cached:
        logger.info("Using cached CDC PLACES COPD data")
        return cached

    # Cache-only enforcement: see utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("cdc_places_copd")
        return {}

    try:
        logger.info("Fetching CDC PLACES COPD data for Wisconsin counties")
        params = {
            "stateabbr": "WI",
            "measureid": "COPD",
            "data_value_type": "Crude prevalence",
            "$limit": 200,
            "$select": "locationname,data_value",
        }
        resp = requests.get(PLACES_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        records = resp.json()

        result: Dict[str, float] = {}
        for rec in records:
            county = str(rec.get("locationname", "")).strip()
            try:
                val = float(rec.get("data_value", float("nan")))
                if county and not pd.isna(val):
                    result[county] = round(val, 1)
            except (ValueError, TypeError):
                pass

        logger.info(
            f"Loaded CDC PLACES COPD prevalence for {len(result)} WI counties"
        )
        set_in_persistent_cache(PLACES_COPD_CACHE_KEY, result, expiry_days=PLACES_CACHE_EXPIRY)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch CDC PLACES COPD data: {e}")
        return {}


def get_copd_prevalence(county_name: str) -> Optional[float]:
    """
    Get county-level COPD crude prevalence (%) from CDC PLACES.

    Source: CDC PLACES via Socrata API (BRFSS model-based estimates).
    Range in Wisconsin: 4.1% (Waukesha) to 10.2% (Forest). WI avg ~7%.
    High COPD burden indicates elevated respiratory disease vulnerability.

    Args:
        county_name: Wisconsin county name (e.g., 'Adams', 'St. Croix').

    Returns:
        COPD prevalence as a percentage (0-100), or None if unavailable.
    """
    county_name = county_name.strip().title()
    copd_data = _fetch_places_copd_wi()
    if county_name in copd_data:
        rate = copd_data[county_name]
        logger.debug(f"CDC PLACES COPD prevalence for {county_name}: {rate:.1f}%")
        return rate
    logger.warning(
        f"CDC PLACES COPD not available for {county_name}; "
        f"using WI default {WI_DEFAULTS['copd_prevalence']}%"
    )
    return None


def _fetch_places_mhlth_wi() -> Dict[str, float]:
    """
    Fetch frequent mental distress prevalence (%) for all Wisconsin counties via CDC PLACES API.

    Measure: MHLTH — "Mental Health Not Good for >=14 Days" (crude prevalence).
    Source: BRFSS model-based estimates, annual update.
    WI range: approximately 12-20% of adults.

    Returns:
        {county_name: prevalence_pct, ...}  e.g. {"Adams": 17.2, "Waukesha": 12.8}
        Returns empty dict on failure.
    """
    cached = get_from_persistent_cache(PLACES_MHLTH_CACHE_KEY, max_age_days=PLACES_CACHE_EXPIRY)
    if cached:
        logger.info("Using cached CDC PLACES MHLTH data")
        return cached

    # Cache-only enforcement: see utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("cdc_places_mhlth")
        return {}

    try:
        logger.info("Fetching CDC PLACES MHLTH (mental distress) data for Wisconsin counties")
        params = {
            "stateabbr": "WI",
            "measureid": "MHLTH",
            "data_value_type": "Crude prevalence",
            "$limit": 200,
            "$select": "locationname,data_value",
        }
        resp = requests.get(PLACES_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        records = resp.json()

        result: Dict[str, float] = {}
        for rec in records:
            county = str(rec.get("locationname", "")).strip()
            try:
                val = float(rec.get("data_value", float("nan")))
                if county and not pd.isna(val):
                    result[county] = round(val, 1)
            except (ValueError, TypeError):
                pass

        logger.info(
            f"Loaded CDC PLACES MHLTH prevalence for {len(result)} WI counties"
        )
        set_in_persistent_cache(PLACES_MHLTH_CACHE_KEY, result, expiry_days=PLACES_CACHE_EXPIRY)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch CDC PLACES MHLTH data: {e}")
        return {}


def get_mental_distress_prevalence(county_name: str) -> Optional[float]:
    """
    Get county-level frequent mental distress prevalence (%) from CDC PLACES.

    Source: CDC PLACES via Socrata API (BRFSS model-based estimates, measure MHLTH).
    Represents percentage of adults reporting >= 14 mentally unhealthy days per month.
    WI range: approximately 12% (Ozaukee) to 20%+ (Menominee/Forest).

    Args:
        county_name: Wisconsin county name (e.g., 'Adams', 'St. Croix').

    Returns:
        Frequent mental distress prevalence as a percentage (0-100), or None if unavailable.
    """
    county_name = county_name.strip().title()
    mhlth_data = _fetch_places_mhlth_wi()
    if county_name in mhlth_data:
        rate = mhlth_data[county_name]
        logger.debug(f"CDC PLACES MHLTH prevalence for {county_name}: {rate:.1f}%")
        return rate
    logger.warning(
        f"CDC PLACES MHLTH not available for {county_name}; "
        f"using WI default {WI_DEFAULTS['mental_distress_prevalence']}%"
    )
    return None


def clear_health_metrics_cache() -> int:
    """Clear all cached health metrics data. Returns number of entries cleared."""
    from utils.persistent_cache import clear_cache_by_prefix
    count = clear_cache_by_prefix("health_metrics_")
    logger.info(f"Cleared {count} health metrics cache entries")
    return count
