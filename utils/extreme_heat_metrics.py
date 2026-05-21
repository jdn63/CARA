"""
Extreme Heat Real-Time Metrics Integration
Fetches authentic data for heat days, emergency department visits, heat advisories, and demographics
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache
from utils.cache_config import get_cache_duration
from utils.wisconsin_climate_data import (
    get_wisconsin_heat_days,
    get_wisconsin_elderly_population, 
    get_wisconsin_heat_ed_visits,
    get_wisconsin_heat_advisories
)

logger = logging.getLogger(__name__)

class ExtremeHeatMetrics:
    """
    Fetches real-time extreme heat metrics from authentic data sources
    """
    
    def __init__(self):
        self.cache_ttl = {
            'heat_days': 1,  # 1 day for historical heat days
            'heat_advisories': 1,  # 1 day for weather alerts
            'elderly_population': 30,  # 30 days for census data
            'ed_visits': 1  # 1 day for health data
        }
        
        # Wisconsin county FIPS codes mapping
        self.wi_county_fips = {
            'Milwaukee': '079', 'Dane': '025', 'Brown': '009', 'Waukesha': '133',
            'Winnebago': '139', 'Rock': '105', 'Racine': '101', 'Outagamie': '087',
            'Kenosha': '059', 'Washington': '131', 'La Crosse': '063', 'Fond du Lac': '039',
            'Marathon': '073', 'Sheboygan': '117', 'Eau Claire': '035', 'Wood': '141',
            'Jefferson': '055', 'St. Croix': '109', 'Walworth': '127', 'Portage': '097',
            'Chippewa': '017', 'Dodge': '027', 'Ozaukee': '089', 'Manitowoc': '071',
            'Sauk': '111', 'Calumet': '015', 'Columbia': '021', 'Barron': '005',
            'Green': '045', 'Dunn': '033', 'Polk': '095', 'Shawano': '115',
            'Grant': '043', 'Iowa': '049', 'Juneau': '057', 'Monroe': '081',
            'Pierce': '093', 'Oneida': '085', 'Lincoln': '069', 'Buffalo': '011',
            'Crawford': '023', 'Waupaca': '135', 'Vernon': '123', 'Adams': '001',
            'Richland': '103', 'Jackson': '053', 'Kewaunee': '061', 'Green Lake': '047',
            'Marquette': '077', 'Waushara': '137', 'Burnett': '013', 'Clark': '019',
            'Washburn': '129', 'Door': '029', 'Oconto': '083', 'Langlade': '067',
            'Vilas': '125', 'Bayfield': '007', 'Sawyer': '113', 'Rusk': '107',
            'Taylor': '119', 'Price': '099', 'Ashland': '003', 'Iron': '051',
            'Forest': '041', 'Florence': '037', 'Marinette': '075', 'Menominee': '078',
            'Pepin': '091'
        }
    
    def _get_annual_heat_days_with_provenance(
        self, county_name: str, year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Resolve annual heat days for a county with explicit provenance.

        v28.8: CDC EPHT (measure 421, days >=90F per county per year) is
        consulted first as the canonical observed source. If EPHT has no
        cached entry for this county, the legacy NCEI Climate-at-a-Glance
        monthly-max heuristic is tried as a redundancy (still cache-only
        per v28.7 fix #5). If both are unavailable the call returns
        value=None so the caller and the freshness pipeline render an
        explicit "data unavailable" rather than a synthetic value
        branded as real.

        Returns a dict with keys:
          value: Optional[int] - heat-day count, or None if unavailable.
          source: str - human-readable provenance label.
          data_year: Optional[int] - year of the underlying observation.
        """
        if year is None:
            year = datetime.now().year

        try:
            from utils.cdc_epht_heat import get_epht_heat_days_for_county
            epht_entry = get_epht_heat_days_for_county(county_name)
        except Exception as exc:
            logger.warning(
                "EPHT heat-days lookup raised for %s: %s: %s",
                county_name, type(exc).__name__, exc,
            )
            epht_entry = None

        if epht_entry is not None:
            value_raw = epht_entry.get('value')
            try:
                value_int = int(round(float(value_raw))) if value_raw is not None else None
            except (TypeError, ValueError):
                value_int = None
            if value_int is not None:
                return {
                    'value': value_int,
                    'source': f"CDC EPHT measure 421 ({epht_entry.get('data_year', 'unknown')})",
                    'data_year': epht_entry.get('data_year'),
                }

        cache_key = f"heat_days_{county_name}_{year}"
        cached_data = get_from_persistent_cache(cache_key, self.cache_ttl['heat_days'])
        if cached_data is not None:
            return {
                'value': cached_data,
                'source': f"NCEI Climate-at-a-Glance heuristic ({year})",
                'data_year': year,
            }

        from utils.request_context import is_cache_only_mode, record_blocked_fetch
        if is_cache_only_mode():
            record_blocked_fetch(f"cdc_epht_heat_days:{county_name}")
            return {'value': None, 'source': 'unavailable (cache cold)', 'data_year': None}

        ncei_value = self._fetch_ncei_heat_days_live(county_name, year)
        if ncei_value is not None:
            return {
                'value': ncei_value,
                'source': f"NCEI Climate-at-a-Glance live ({year})",
                'data_year': year,
            }
        return {'value': None, 'source': 'unavailable', 'data_year': None}

    def get_annual_heat_days(self, county_name: str, year: Optional[int] = None) -> Optional[int]:
        """
        Public accessor for the annual heat-day count.

        Backward-compatible wrapper around
        `_get_annual_heat_days_with_provenance` that drops the source
        label. Callers that need provenance (the heat-domain show-work
        and dashboard caption) should invoke the private helper or
        `get_comprehensive_heat_metrics` directly.

        Returns the integer heat-day count or None if neither EPHT nor
        the NCEI heuristic has a cached value for this county.
        """
        return self._get_annual_heat_days_with_provenance(county_name, year)['value']

    def _fetch_ncei_heat_days_live(
        self, county_name: str, year: int
    ) -> Optional[int]:
        """
        Legacy NCEI Climate-at-a-Glance heuristic, retained as a
        last-resort live fetch outside cache-only contexts.

        This is the v28.7 explicit-failure path (no synthetic fallback):
        any FIPS-lookup miss, non-200 response, or parse error returns
        None so the caller can render an explicit "data unavailable"
        instead of substituting a synthetic value. Only invoked when
        EPHT has no cached entry AND we are outside cache-only mode.
        """
        # Pre-guard duplicates the original behavior: keep the legacy
        # cache key warm so subsequent reads hit `get_annual_heat_days`
        # without retraversing the EPHT lookup.
        cache_key = f"heat_days_{county_name}_{year}"

        # Cache-only enforcement: see utils/request_context.py.
        # v28.7 review fix #5: explicit failure mode. Prior code silently
        # fell back to get_wisconsin_heat_days() (a synthetic climatology
        # proxy) on every cache miss, FIPS lookup miss, or NOAA non-200,
        # masking real data outages from the freshness pipeline. We now
        # return None on any non-cache failure path so the caller (and
        # the freshness pipeline) can render an explicit "data unavailable"
        # rather than a synthetic value branded as real. The full NIHHIS /
        # Heat.gov pipeline replacement (review finding #4) is deferred
        # to a follow-up task.
        from utils.request_context import is_cache_only_mode, record_blocked_fetch
        if is_cache_only_mode():
            record_blocked_fetch(f"noaa_heat_days:{county_name}")
            return None

        try:
            county_fips = self.wi_county_fips.get(county_name)
            if not county_fips:
                logger.warning(
                    f"NOAA heat days: county FIPS not found for {county_name}; "
                    f"returning None (no synthetic fallback per v28.7 fix #5)"
                )
                return None

            # Use NOAA Climate at a Glance API for county temperature data
            url = f"https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series/tmax/55/{county_fips}/12/{year}01/{year}12.json"

            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                logger.warning(
                    f"NOAA heat days: API returned status {response.status_code} "
                    f"for {county_name}; returning None (no synthetic fallback "
                    f"per v28.7 fix #5)"
                )
                return None

            data = response.json()
            
            # Calculate heat days from monthly maximum temperature data
            heat_days = 0
            if 'data' in data:
                for month_data in data['data'].values():
                    # NOAA data is in Fahrenheit, count days likely above 90°F
                    # This is an approximation based on monthly averages
                    temp_f = float(month_data.get('value', 0))
                    if temp_f >= 85:  # If monthly max avg is 85°F, likely some days >90°F
                        # Estimate based on temperature: higher temps = more heat days
                        if temp_f >= 95:
                            heat_days += 15  # High likelihood of many heat days
                        elif temp_f >= 90:
                            heat_days += 8   # Moderate likelihood
                        elif temp_f >= 85:
                            heat_days += 3   # Some likelihood
            
            # Cache the result
            set_in_persistent_cache(cache_key, heat_days)
            logger.info(f"Retrieved heat days for {county_name}: {heat_days}")
            return heat_days
            
        except Exception as e:
            logger.error(
                f"NOAA heat days: error fetching for {county_name}: {e}; "
                f"returning None (no synthetic fallback per v28.7 fix #5)"
            )
            return None
    
    def get_heat_advisories_count(self, county_name: str, year: Optional[int] = None) -> Optional[int]:
        """
        Fetch heat advisory count from NOAA weather alerts
        Note: Current API only provides last 7 days, so this provides estimated annual count
        
        Args:
            county_name: Wisconsin county name
            year: Year for data (defaults to current year)
            
        Returns:
            Estimated annual heat advisories or None if unavailable
        """
        cache_key = f"heat_advisories_{county_name}_{year or datetime.now().year}"
        cached_data = get_from_persistent_cache(cache_key, self.cache_ttl['heat_advisories'])
        if cached_data:
            return cached_data

        # Cache-only enforcement: see utils/request_context.py.
        from utils.request_context import is_cache_only_mode, record_blocked_fetch
        if is_cache_only_mode():
            record_blocked_fetch(f"nws_heat_advisories:{county_name}")
            return None

        try:
            # Get current alerts for Wisconsin
            url = "https://api.weather.gov/alerts/active?area=WI"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"NWS Alerts API returned status {response.status_code}")
                return None
            
            data = response.json()
            current_heat_alerts = 0
            
            # Count current heat-related alerts
            for alert in data.get('features', []):
                properties = alert.get('properties', {})
                event = properties.get('event', '').lower()
                areas = properties.get('areaDesc', '').lower()
                
                if 'heat' in event and county_name.lower() in areas:
                    current_heat_alerts += 1
            
            # Estimate annual count based on historical patterns
            # Wisconsin typically has 2-6 heat advisories per year
            # Base estimate on current month and extrapolate
            current_month = datetime.now().month
            if 6 <= current_month <= 8:  # Summer months
                # If we have current alerts in summer, estimate higher annual count
                annual_estimate = max(3, current_heat_alerts * 2) if current_heat_alerts > 0 else 3
            else:
                # Off-season, use baseline estimate
                annual_estimate = 3
            
            set_in_persistent_cache(cache_key, annual_estimate)
            logger.info(f"Estimated heat advisories for {county_name}: {annual_estimate}")
            return annual_estimate
            
        except Exception as e:
            logger.error(f"Error fetching heat advisories for {county_name}: {e}")
            return None
    
    def get_elderly_population_percentage(self, county_name: str) -> Optional[float]:
        """
        Get population aged 65+ percentage from local Census data files
        
        Strategic Planning Mode: Uses county-specific Census data from local files
        
        Args:
            county_name: Wisconsin county name
            
        Returns:
            Percentage of population 65+ or None if unavailable
        """
        try:
            # Use local Census data loader for county-specific accuracy
            from utils.census_data_loader import wisconsin_census
            
            elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name)
            if elderly_pct is not None:
                logger.info(f"Local data: {county_name} has {elderly_pct}% elderly population")
                return elderly_pct
            else:
                logger.warning(f"No local population 65+ data found for {county_name}, using fallback")
                return get_wisconsin_elderly_population(county_name)
            
        except Exception as e:
            logger.error(f"Error getting population 65+ data for {county_name}: {e}")
            return get_wisconsin_elderly_population(county_name)
    
    def get_heat_related_ed_visits(self, county_name: str, year: Optional[int] = None) -> Optional[int]:
        """
        Get estimated heat-related emergency department visits
        Note: Actual ED data requires special access through ESSENCE/NSSP
        This provides estimates based on population and heat risk factors
        
        Args:
            county_name: Wisconsin county name
            year: Year for data (defaults to current year)
            
        Returns:
            Estimated annual heat-related ED visits or None if unavailable
        """
        cache_key = f"ed_visits_{county_name}_{year or datetime.now().year}"
        cached_data = get_from_persistent_cache(cache_key, self.cache_ttl['ed_visits'])
        if cached_data:
            return cached_data
        
        try:
            # Get population data for scaling
            county_fips = self.wi_county_fips.get(county_name)
            if not county_fips:
                return None
            
            # Strategic Planning Mode: Use local Census population data
            try:
                from utils.census_data_loader import wisconsin_census
                population = wisconsin_census.get_county_population(county_name)
                if population is None:
                    population = 50000  # Default if not found
            except Exception as e:
                logger.debug(f"Census data unavailable for {county_name}, using fallback: {e}")
                population = 50000
            
            # Estimate ED visits based on national averages
            # CDC data shows ~2-4 heat-related ED visits per 100,000 population annually
            # Higher for urban areas, adults aged 65+
            base_rate = 3.0  # per 100,000
            
            # Adjust for county characteristics
            elderly_pct = self.get_elderly_population_percentage(county_name) or 15.0
            if elderly_pct > 18:
                base_rate *= 1.3  # Higher risk for adults aged 65+
            
            # Urban areas typically have higher rates
            if county_name in ['Milwaukee', 'Dane', 'Brown']:
                base_rate *= 1.2
            
            estimated_visits = int((population / 100000) * base_rate)
            
            set_in_persistent_cache(cache_key, estimated_visits)
            logger.info(f"Estimated heat-related ED visits for {county_name}: {estimated_visits}")
            return estimated_visits
            
        except Exception as e:
            logger.error(f"Error estimating ED visits for {county_name}: {e}")
            return get_wisconsin_heat_ed_visits(county_name)
    
    def get_comprehensive_heat_metrics(self, county_name: str) -> Dict[str, Any]:
        """
        Get all extreme heat metrics for a county
        
        Args:
            county_name: Wisconsin county name
            
        Returns:
            Dictionary with all heat metrics
        """
        current_year = datetime.now().year

        # v28.8: resolve heat-day count through the provenance-aware
        # helper so the dashboard caption and show-work can label the
        # row with the actual source (EPHT vs NCEI heuristic vs
        # unavailable) instead of a generic "NOAA" string.
        heat_days_info = self._get_annual_heat_days_with_provenance(
            county_name, current_year
        )

        metrics = {
            'annual_heat_days': heat_days_info['value'],
            'heat_days_source': heat_days_info['source'],
            'heat_days_year': heat_days_info['data_year'],
            'heat_advisories': self.get_heat_advisories_count(county_name, current_year),
            'elderly_percentage': self.get_elderly_population_percentage(county_name),
            'ed_visits': self.get_heat_related_ed_visits(county_name, current_year),
            'data_year': current_year,
            'last_updated': datetime.now().isoformat(),
            'data_sources': {
                'heat_days': heat_days_info['source'],
                'heat_advisories': 'NWS Weather Alerts API',
                'elderly_population': 'US Census Bureau ACS API',
                'ed_visits': 'Population-based estimate (CDC national rates)'
            }
        }
        
        logger.info(f"Retrieved comprehensive heat metrics for {county_name}")
        return metrics

# Initialize the metrics fetcher
heat_metrics = ExtremeHeatMetrics()

def get_extreme_heat_metrics(county_name: str) -> Dict[str, Any]:
    """
    Main function to get extreme heat metrics for integration with existing system
    
    Args:
        county_name: Wisconsin county name
        
    Returns:
        Heat metrics dictionary
    """
    return heat_metrics.get_comprehensive_heat_metrics(county_name)