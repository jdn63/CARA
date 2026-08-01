"""
Weather Alerts Module

This module handles retrieval and processing of weather alerts from the National Weather Service (NWS) API.
It supports the temporal risk analysis by providing information on active weather events.
"""

import os
import json
import logging
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Get module logger (centralized config in core.py)
logger = logging.getLogger(__name__)

# Cache weather alerts to reduce API calls
_weather_alerts_cache = {}
_cache_expiry = {}  # Timestamp when cached data expires

# Cache county FIPS codes
_county_fips_cache = {}


def get_active_alerts(jurisdiction_id: str) -> List[Dict]:
    """
    Get active weather alerts for a specific jurisdiction.
    
    Args:
        jurisdiction_id: The ID of the jurisdiction to get alerts for
        
    Returns:
        List of active weather alerts with event type, severity, and expiration
    """
    global _weather_alerts_cache, _cache_expiry
    
    # Check if we have a non-expired cached result
    cache_key = f"alerts_{jurisdiction_id}"
    current_time = datetime.now()
    
    if (cache_key in _weather_alerts_cache and 
        cache_key in _cache_expiry and 
        current_time < _cache_expiry[cache_key]):
        return _weather_alerts_cache[cache_key]
    
    # Get county name from jurisdiction ID
    county_name = _get_county_from_jurisdiction(jurisdiction_id)
    if not county_name:
        logger.warning(f"Could not determine county for jurisdiction ID {jurisdiction_id}")
        return []
    
    # Get FIPS code for county
    county_fips = _get_county_fips(county_name)
    if not county_fips:
        logger.warning(f"Could not determine FIPS code for county {county_name}")
        return []
    
    # Call NWS API to get active alerts for the county
    try:
        # Always try to get real alert data instead of using load management
        logger.info(f"Fetching real weather alerts for {jurisdiction_id}")
        # We previously returned empty data some of the time, but now we'll always
        # try to get real alert data for accuracy and reliability
        
        # NWS API URL for alerts (filtered by area/zone)
        url = f"https://api.weather.gov/alerts/active?zone={county_fips}"
        
        # Make API request
        headers = {
            "User-Agent": "WI-Health-Risk-Assessment-Tool/1.0 (Wisconsin-DHS)"
        }
        
        # Add defensive error handling with retries
        max_retries = 2
        retry_count = 0
        response = None  # Initialize response variable to avoid unbound reference
        
        while retry_count <= max_retries:
            try:
                # Use a shorter timeout to avoid blocking the server
                response = requests.get(url, headers=headers, timeout=3)
                # Check for success immediately to avoid processing invalid response
                if response.status_code == 200:
                    break
                else:
                    logger.warning(f"Weather alerts API returned status code {response.status_code}")
                    retry_count += 1
                    if retry_count <= max_retries:
                        time.sleep(0.5)  # Short delay between retries
                    else:
                        logger.error(f"Weather alerts API failed with status code {response.status_code} after {max_retries} retries")
                        return []  # Return empty alerts list
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                retry_count += 1
                if retry_count <= max_retries:
                    logger.warning(f"Weather alerts API request failed (attempt {retry_count}): {str(e)}. Retrying...")
                    time.sleep(0.5)  # Short delay between retries
                else:
                    logger.error(f"Weather alerts API request failed after {max_retries} retries: {str(e)}")
                    return []  # Return empty alerts list
        
        # This code block is unreachable since we already check the status code above,
        # but we'll keep it for extra safety
        if response is None:
            logger.error("Error fetching weather alerts: No response received")
            return []
        elif response.status_code != 200:
            logger.error(f"Error fetching weather alerts: status code {response.status_code}")
            return []
            
        # Parse response with safe error handling
        try:
            alerts_data = response.json()
        except Exception as json_err:
            logger.error(f"Error parsing weather alerts JSON: {str(json_err)}")
            return []  # Return empty list if JSON parsing fails
        
        # Extract relevant alert information
        processed_alerts = []
        for feature in alerts_data.get('features', []):
            properties = feature.get('properties', {})
            
            # Check if this alert affects our county
            affected_zones = properties.get('affectedZones', [])
            if not any(county_fips in zone for zone in affected_zones):
                continue
                
            # Extract alert details
            processed_alert = {
                'event': properties.get('event', 'Unknown'),
                'headline': properties.get('headline', ''),
                'description': properties.get('description', ''),
                'severity': properties.get('severity', 'Unknown'),
                'expires': properties.get('expires', ''),
                'response_type': properties.get('responseType', ''),
                'urgency': properties.get('urgency', '')
            }
            
            processed_alerts.append(processed_alert)
            
        # Cache the result for 15 minutes
        _weather_alerts_cache[cache_key] = processed_alerts
        _cache_expiry[cache_key] = current_time + timedelta(minutes=15)
        
        return processed_alerts
        
    except Exception as e:
        logger.error(f"Error retrieving weather alerts: {str(e)}")
        return []

def _get_county_from_jurisdiction(jurisdiction_id: str) -> Optional[str]:
    """Get county name from jurisdiction ID"""
    try:
        # Import the jurisdiction mapping
        from utils.jurisdiction_mapping_code import jurisdiction_mapping
        county = jurisdiction_mapping.get(jurisdiction_id)
        return county
    except ImportError:
        # Fallback mapping for testing
        fallback_mapping = {
            '41': 'Milwaukee',
            '42': 'Milwaukee',
            '43': 'Waukesha',
            '44': 'Dane',
            '45': 'Brown',
            '46': 'Bayfield',
            '47': 'Pierce'
        }
        return fallback_mapping.get(jurisdiction_id)

def _get_county_fips(county_name: str) -> Optional[str]:
    """Get FIPS code for a Wisconsin county"""
    global _county_fips_cache
    
    # Return cached value if available
    if county_name in _county_fips_cache:
        return _county_fips_cache[county_name]
    
    # Wisconsin FIPS codes for counties - the first two digits (55) are the state code
    wi_fips_codes = {
        'Adams': '55001',
        'Ashland': '55003',
        'Barron': '55005',
        'Bayfield': '55007',
        'Brown': '55009',
        'Buffalo': '55011',
        'Burnett': '55013',
        'Calumet': '55015',
        'Chippewa': '55017',
        'Clark': '55019',
        'Columbia': '55021',
        'Crawford': '55023',
        'Dane': '55025',
        'Dodge': '55027',
        'Door': '55029',
        'Douglas': '55031',
        'Dunn': '55033',
        'Eau Claire': '55035',
        'Florence': '55037',
        'Fond du Lac': '55039',
        'Forest': '55041',
        'Grant': '55043',
        'Green': '55045',
        'Green Lake': '55047',
        'Iowa': '55049',
        'Iron': '55051',
        'Jackson': '55053',
        'Jefferson': '55055',
        'Juneau': '55057',
        'Kenosha': '55059',
        'Kewaunee': '55061',
        'La Crosse': '55063',
        'Lafayette': '55065',
        'Langlade': '55067',
        'Lincoln': '55069',
        'Manitowoc': '55071',
        'Marathon': '55073',
        'Marinette': '55075',
        'Marquette': '55077',
        'Menominee': '55078',
        'Milwaukee': '55079',
        'Monroe': '55081',
        'Oconto': '55083',
        'Oneida': '55085',
        'Outagamie': '55087',
        'Ozaukee': '55089',
        'Pepin': '55091',
        'Pierce': '55093',
        'Polk': '55095',
        'Portage': '55097',
        'Price': '55099',
        'Racine': '55101',
        'Richland': '55103',
        'Rock': '55105',
        'Rusk': '55107',
        'Sauk': '55111',
        'Sawyer': '55113',
        'Shawano': '55115',
        'Sheboygan': '55117',
        'St. Croix': '55109',
        'Taylor': '55119',
        'Trempealeau': '55121',
        'Vernon': '55123',
        'Vilas': '55125',
        'Walworth': '55127',
        'Washburn': '55129',
        'Washington': '55131',
        'Waukesha': '55133',
        'Waupaca': '55135',
        'Waushara': '55137',
        'Winnebago': '55139',
        'Wood': '55141'
    }
    
    # Get FIPS code for county
    fips = wi_fips_codes.get(county_name)
    
    # Cache for future use
    if fips:
        _county_fips_cache[county_name] = fips
        
    return fips

def clear_weather_cache() -> int:
    """
    Clear weather alerts and conditions cache.
    
    Returns:
        Number of cache entries cleared
    """
    global _weather_alerts_cache, _cache_expiry
    
    entries_cleared = len(_weather_alerts_cache) + len(_cache_expiry)
    
    _weather_alerts_cache.clear()
    _cache_expiry.clear()
    
    logger.info(f"Weather cache cleared: {entries_cleared} entries removed")
    return entries_cleared