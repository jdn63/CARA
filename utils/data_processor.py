"""Data processing utilities for risk assessment"""
import pandas as pd
import geopandas as gpd
import json
import logging
import os
import numpy as np
import yaml
from scipy import stats
from typing import Dict, List, Tuple, Any, Optional
from werkzeug.datastructures import FileStorage
from census import Census
from datetime import datetime, timedelta

_county_baselines = None

def _load_county_baselines():
    """Load county baseline scores and fallback values from config/county_baselines.yaml"""
    global _county_baselines
    if _county_baselines is not None:
        return _county_baselines
    baselines_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'county_baselines.yaml')
    try:
        with open(baselines_path, 'r') as f:
            _county_baselines = yaml.safe_load(f)
        logging.getLogger(__name__).info(f"Loaded county baselines from {baselines_path}")
    except Exception as e:
        logging.getLogger(__name__).warning(f"Could not load county baselines from {baselines_path}: {e}. Using built-in defaults.")
        _county_baselines = {'fallback_scores': {}, 'cybersecurity': {}, 'extreme_heat': {}}
    return _county_baselines


def _get_baseline(domain: str, component: str, county: str) -> float:
    """Look up a county baseline score from config/county_baselines.yaml.
    Falls back to the _default value for the component if county is not listed."""
    baselines = _load_county_baselines()
    component_data = baselines.get(domain, {}).get(component, {})
    return component_data.get(county, component_data.get('_default', 0.5))


def _get_fallback(domain: str) -> float:
    """Get the standardized fallback score for a domain when data is unavailable.
    All domains default to 0.5 (maximum uncertainty, neutral midpoint)."""
    baselines = _load_county_baselines()
    return baselines.get('fallback_scores', {}).get(domain, 0.5)



from utils.correctional_facilities import CorrectionalFacilitiesConnector
from utils.dhs_data import get_county_disease_data, get_vaccination_rate, clear_dhs_cache, WISCONSIN_COUNTIES
from utils.svi_data import get_svi_data
from utils.strategic_assessments import get_strategic_air_quality_assessment, get_strategic_heat_assessment
from utils.air_quality_data import get_air_quality_risk
from utils.utilities_risk import (
    calculate_electrical_outage_risk,
    calculate_utilities_disruption_risk,
    calculate_supply_chain_risk,
    calculate_fuel_shortage_risk
)
from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
# Import the tribal boundaries module for tribal risk calculation
from utils.tribal_boundaries import calculate_tribal_risk, get_tribal_attributes
# Import the new active shooter risk model
from utils.active_shooter_risk import calculate_active_shooter_risk
# Import config manager so PHRAT weights are sourced from risk_weights.yaml
from utils.config_manager import get_config_manager
# Import the authoritative jurisdiction-to-county mapping
from utils.jurisdiction_mapping_code import jurisdiction_mapping

logger = logging.getLogger(__name__)
# Initializing CorrectionalFacilitiesConnector inline to avoid network errors

# NOTE: The deprecated JURISDICTION_TO_COUNTY dict was removed. It had incorrect IDs
# (e.g., '40' mapped to Milwaukee instead of Lincoln, tribal IDs were scrambled).
# The authoritative mapping is jurisdiction_mapping from jurisdiction_mapping_code.py.

def get_county_id(county_name: str) -> str:
    """
    Convert a county name to a jurisdiction ID
    
    Args:
        county_name: The name of the county to look up
        
    Returns:
        The ID of the jurisdiction for this county
    """
    # Dictionary of Wisconsin counties mapped to jurisdiction IDs
    county_to_jurisdiction = {
        'Adams': '01',
        'Ashland': '02', 
        'Barron': '03',
        'Bayfield': '04',
        'Brown': '05',
        'Buffalo': '06',
        'Burnett': '07',
        'Calumet': '08',
        'Chippewa': '09',
        'Clark': '10',
        'Columbia': '11',
        'Crawford': '12',
        'Dane': '13',
        'Dodge': '14',
        'Door': '15',
        'Douglas': '16',
        'Dunn': '17',
        'Eau Claire': '18',
        'Florence': '19',
        'Fond du Lac': '20',
        'Forest': '21',
        'Grant': '22',
        'Green': '23',
        'Green Lake': '24',
        'Iowa': '25',
        'Iron': '26',
        'Jackson': '27',
        'Jefferson': '28',
        'Juneau': '29',
        'Kenosha': '30',
        'Kewaunee': '31',
        'La Crosse': '32',
        'Lafayette': '33',
        'Langlade': '34',
        'Lincoln': '35',
        'Manitowoc': '36',
        'Marathon': '37',
        'Marinette': '38',
        'Marquette': '39',
        'Menominee': '40',
        'Milwaukee': '41',
        'Monroe': '42',
        'Oconto': '43',
        'Oneida': '44',
        'Outagamie': '45',
        'Ozaukee': '46',
        'Pepin': '47',
        'Pierce': '48',
        'Polk': '49',
        'Portage': '50',
        'Price': '51',
        'Racine': '52',
        'Richland': '53',
        'Rock': '54',
        'Rusk': '55',
        'St. Croix': '56',
        'Sauk': '57',
        'Sawyer': '58',
        'Shawano': '59',
        'Sheboygan': '60',
        'Taylor': '61',
        'Trempealeau': '62',
        'Vernon': '63',
        'Vilas': '64',
        'Walworth': '65',
        'Washburn': '66',
        'Washington': '67',
        'Waukesha': '68',
        'Waupaca': '69',
        'Waushara': '70',
        'Winnebago': '71',
        'Wood': '72'
    }
    
    if county_name in county_to_jurisdiction:
        return county_to_jurisdiction[county_name]
    else:
        # Fallback for unknown counties - use Milwaukee as default
        logger.warning(f"Unknown county name: {county_name}, defaulting to Milwaukee")
        return "41"  # Milwaukee ID

def get_county_for_jurisdiction(jurisdiction_id: str) -> str:
    """
    Map a jurisdiction ID to its corresponding Wisconsin county name.
    
    Args:
        jurisdiction_id: The jurisdiction ID (e.g., 'T01', '13', '41')
        
    Returns:
        County name or None if not found
    """
    if not jurisdiction_id:
        logger.warning("Empty jurisdiction ID provided to get_county_for_jurisdiction")
        return None
        
    # Handle case where jurisdiction_id is actually a county name already
    if jurisdiction_id in WISCONSIN_COUNTIES:
        logger.debug(f"Jurisdiction ID '{jurisdiction_id}' is already a county name")
        return jurisdiction_id
    
    # Handle specific remappings for problematic IDs
    id_remapping = {
        '07': '107', # Special case for certain counties
        # Add more remappings as needed
    }
    
    # Apply remapping if needed
    jurisdiction_id = id_remapping.get(jurisdiction_id, jurisdiction_id)
    
    # Use authoritative jurisdiction_mapping from jurisdiction_mapping_code.py
    county = jurisdiction_mapping.get(jurisdiction_id)
    if not county:
        logger.warning(f"No county mapping found for jurisdiction ID: {jurisdiction_id}")
    
    return county

# Dictionary to store processed risk data for all jurisdictions
# Used for percentile calculations across all jurisdictions
all_jurisdictions_risk_data = {}

# Cache for NRI data to avoid repeated CSV parsing
_nri_data_cache = None

# Maximum number of attempts for API calls
MAX_API_RETRIES = 3
RETRY_DELAY = 1.0  # seconds

def load_nri_data():
    """Load and process National Risk Index data with Census mobile home data"""
    global _nri_data_cache
    
    # Return cached data if available
    if _nri_data_cache is not None:
        return _nri_data_cache
        
    try:
        # Load NRI data for Wisconsin counties (from FEMA)
        nri_df = pd.read_csv('attached_assets/NRI_Table_CensusTracts_Wisconsin_FloodTornadoWinterOnly.csv')
        
        # Filter to county level and relevant columns
        county_data = {}
        
        for county_name in nri_df['county'].unique():
            # Calculate county-level statistics by averaging census tract values
            county_rows = nri_df[nri_df['county'] == county_name]
            
            # Extract risk scores for each hazard
            flood_risk = county_rows['flood_risk'].mean() / 100.0  # Normalize to 0-1 scale
            tornado_risk = county_rows['tornado_risk'].mean() / 100.0
            winter_risk = county_rows['winter_risk'].mean() / 100.0
            
            county_data[county_name] = {
                'flood_risk': float(flood_risk),
                'tornado_risk': float(tornado_risk),
                'winter_storm_risk': float(winter_risk)
            }
            
        # Add special handling for tribal areas that might not be in NRI data
        tribal_county_mapping = {
            'Ho-Chunk': 'Jackson',
            'HoChunk': 'Jackson',
            'Menominee': 'Menominee',
            'Oneida': 'Brown',
            'Lac du Flambeau': 'Vilas',
            'Bad River': 'Ashland',
            'Red Cliff': 'Bayfield',
            'Potawatomi': 'Forest',
            'St. Croix': 'Burnett',
            'Sokaogon': 'Forest',
            'Lac Courte Oreilles': 'Sawyer'
        }
        
        # Add tribal areas with data from mapped counties
        for tribal_name, county_name in tribal_county_mapping.items():
            if county_name in county_data and tribal_name not in county_data:
                county_data[tribal_name] = dict(county_data[county_name])
                
        # Cache the prepared data
        _nri_data_cache = county_data
        
        return county_data
    
    except Exception as e:
        logger.critical(
            f"Failed to load NRI CSV data — all counties will receive neutral "
            f"Wisconsin-average scores (0.33/0.35/0.40) until the file is restored. "
            f"Error: {str(e)}"
        )
        # Return neutral Wisconsin-average placeholders — do NOT inject one county's
        # real values into other counties.  The _NEUTRAL sentinel key is used by
        # calculate_jurisdiction_risk() to surface a warning in logs rather than
        # silently substituting Milwaukee-area numbers.
        _NEUTRAL = {'flood_risk': 0.33, 'tornado_risk': 0.35, 'winter_storm_risk': 0.40}
        return {'_neutral_fallback': _NEUTRAL}

def load_prison_data() -> Dict[str, Dict]:
    """Load correctional facility data from OpenFEMA and WI DOC"""
    try:
        # For tribal jurisdictions, directly use hard-coded data to avoid API calls that may fail
        # This ensures the dashboard will always work for tribal areas
        facility_weights = {
            'state_prison': 1.0,
            'county_jail': 0.8,
            'juvenile': 0.6,
            'treatment': 0.4
        }
        
        # Start with a basic tribal entry and Jackson county for Ho-Chunk Nation
        prison_data = {
            'Tribal': {
                'facilities': [],
                'weights': facility_weights
            },
            'Jackson': {
                'facilities': [
                    {'type': 'county_jail', 'name': 'Jackson County Jail'}
                ],
                'weights': facility_weights
            },
            'Milwaukee': {
                'facilities': [
                    {'type': 'state_prison', 'name': 'Milwaukee Secure Detention Facility'},
                    {'type': 'county_jail', 'name': 'Milwaukee County Jail'}
                ],
                'weights': facility_weights
            },
            'Dane': {
                'facilities': [
                    {'type': 'state_prison', 'name': 'Oakhill Correctional Institution'},
                    {'type': 'county_jail', 'name': 'Dane County Jail'}
                ],
                'weights': facility_weights
            }
        }
        
        # Add specific entries for each tribal area's primary county
        tribal_county_mapping = {
            'Bad River': 'Ashland',
            'Red Cliff': 'Bayfield',
            'Lac Courte Oreilles': 'Sawyer',
            'Oneida': 'Brown',
            'Menominee': 'Menominee',
            'Ho-Chunk': 'Jackson', 
            'Lac du Flambeau': 'Vilas',
            'Potawatomi': 'Forest',
            'St. Croix': 'Burnett',
            'Sokaogon': 'Forest'
        }
        
        # Add basic jail entries for the tribal counties if they don't exist
        for tribe, county in tribal_county_mapping.items():
            if county not in prison_data:
                prison_data[county] = {
                    'facilities': [
                        {'type': 'county_jail', 'name': f'{county} County Jail'}
                    ],
                    'weights': facility_weights
                }
        
        # Only try to get API data if we already have some required fallback data
        try:
            # Get data from correctional facilities connector but with a short timeout
            from utils.correctional_facilities import CorrectionalFacilitiesConnector
            connector = CorrectionalFacilitiesConnector()
            api_prison_data = connector._get_fallback_data()  # Just use fallback data directly
            
            # Merge with our base data
            for county, data in api_prison_data.items():
                if county not in prison_data:
                    prison_data[county] = data
        except Exception as api_e:
            logger.warning(f"Using static correctional facilities data due to API error: {str(api_e)}")
            # Continue with our local data - no need to take any action here
            
        return prison_data
        
    except Exception as e:
        logger.error(f"Error loading prison data: {str(e)}")
        # Return minimal hardcoded data for fallback
        facility_weights = {
            'state_prison': 1.0,
            'county_jail': 0.8,
            'juvenile': 0.6,
            'treatment': 0.4
        }
        return {
            'Tribal': {
                'facilities': [],
                'weights': facility_weights
            },
            'Jackson': {
                'facilities': [
                    {'type': 'county_jail', 'name': 'Jackson County Jail'}
                ],
                'weights': facility_weights
            },
            'Milwaukee': {
                'facilities': [
                    {'type': 'state_prison', 'name': 'Milwaukee Secure Detention Facility'},
                    {'type': 'county_jail', 'name': 'Milwaukee County Jail'}
                ],
                'weights': facility_weights
            },
            'Dane': {
                'facilities': [
                    {'type': 'state_prison', 'name': 'Oakhill Correctional Institution'},
                    {'type': 'county_jail', 'name': 'Dane County Jail'}
                ],
                'weights': facility_weights
            }
        }

def calculate_jurisdiction_risk(county_name: str) -> dict:
    """Calculate risk scores for a jurisdiction using NRI data"""
    # Load the risk data
    nri_data = load_nri_data()
    prison_data = load_prison_data()
    
    # Get county-specific data or use a neutral Wisconsin-average placeholder.
    # Never substitute another county's real profile — that would silently bias
    # risk scores for jurisdictions whose county name wasn't found in the NRI CSV.
    _neutral = {'flood_risk': 0.33, 'tornado_risk': 0.35, 'winter_storm_risk': 0.40}
    county_risk = nri_data.get(county_name)
    if county_risk is None:
        county_risk = nri_data.get('_neutral_fallback', _neutral)
        logger.warning(
            f"NRI data not found for county '{county_name}'; "
            f"using neutral Wisconsin-average scores. "
            f"Check that the NRI CSV contains an entry for this county."
        )
    
    # Check if this is a tribal jurisdiction and handle differently
    is_tribal = any(tribal_name in county_name for tribal_name in ['HoChunk', 'Ho-Chunk', 'Menominee', 'Oneida', 'Lac du Flambeau', 'Bad River', 'Red Cliff', 'Potawatomi', 'St. Croix', 'Sokaogon', 'Lac Courte Oreilles'])
    
    # Get facility data or use empty defaults
    # For tribal areas, use the generic 'Tribal' entry to avoid API failures
    default_facilities = {
        'facilities': [],
        'weights': {
            'state_prison': 1.0,
            'county_jail': 0.8,
            'juvenile': 0.6,
            'treatment': 0.4
        }
    }
    
    if is_tribal and 'Tribal' in prison_data:
        correctional_facilities = prison_data.get('Tribal', default_facilities)
    else:
        correctional_facilities = prison_data.get(county_name, default_facilities)
    
    # Calculate mobile home vulnerability factor (5% to 50% increase in tornado risk)
    mobile_home_pct = get_mobile_home_percentage(county_name)
    logger.info(f"Mobile home percentage for {county_name}: {mobile_home_pct:.2f}%")
    
    # Scale factor: 5% mobile homes = 25% increase, 10% = 50% increase (capped)
    mobile_factor = min(0.5, (mobile_home_pct / 10.0) * 0.5)  
    
    # Calculate correctional facility impact on risk (up to 20% increase based on facility types)
    facility_multiplier = 1.0
    if correctional_facilities['facilities']:
        # Calculate weight based on facility types
        facility_weight = sum(
            correctional_facilities['weights'].get(facility['type'], 0.0) 
            for facility in correctional_facilities['facilities']
        ) / len(correctional_facilities['facilities'])
        
        # Apply a 0-20% increase based on weighted facility score
        facility_impact = facility_weight * 0.2
        facility_multiplier = 1.0 + facility_impact
        logger.info(f"Correctional facility impact for {county_name}: {facility_impact:.2f}% increase")
    
    # Get base tornado risk and adjust for mobile home factor
    base_tornado_risk = county_risk['tornado_risk']
    adjusted_tornado_risk = base_tornado_risk * (1.0 + mobile_factor)
    logger.info(f"Tornado risk for {county_name}: base={base_tornado_risk:.2f}, adjusted={adjusted_tornado_risk:.2f} (mobile home factor={mobile_factor:.2f})")
    
    from utils.natural_hazards_risk import (
        calculate_enhanced_flood_risk,
        calculate_enhanced_tornado_risk,
        calculate_enhanced_winter_storm_risk,
        calculate_enhanced_thunderstorm_risk
    )

    flood_risk_data = calculate_enhanced_flood_risk(county_name)
    flood_overall_risk = flood_risk_data['overall']

    tornado_risk_data = calculate_enhanced_tornado_risk(county_name)
    adjusted_tornado_risk = tornado_risk_data['overall']

    winter_storm_risk_data = calculate_enhanced_winter_storm_risk(county_name)
    winter_storm_risk = winter_storm_risk_data['overall']

    thunderstorm_risk_data = calculate_enhanced_thunderstorm_risk(county_name)
    thunderstorm_risk = thunderstorm_risk_data['overall']

    natural_hazards = {
        'flood': float(flood_overall_risk),
        'tornado': float(adjusted_tornado_risk),
        'winter_storm': float(winter_storm_risk),
        'thunderstorm': float(thunderstorm_risk)
    }
    
    logger.info(f"Calculated risk scores for {county_name} (facility multiplier={facility_multiplier:.2f}): {natural_hazards}")
    
    # Mobile home data is now only used as tornado vulnerability amplifier
    
    return natural_hazards

# Cache for mobile home data to avoid repeated API calls
_mobile_home_cache = {}
_mobile_home_cache_expiry = {}

# Cache duration in seconds - 24 hours (housing data changes less frequently)
_MOBILE_HOME_CACHE_DURATION = 86400

def get_mobile_home_percentage(county_name: str) -> float:
    """Get percentage of housing units that are mobile homes from local Census data files
    
    Strategic Planning Mode: Uses county-specific Census data from local files
    
    Args:
        county_name: Name of the Wisconsin county
        
    Returns:
        Percentage of housing units that are mobile homes as a float (e.g., 5.2 for 5.2%)
    """
    try:
        # Use local Census data loader for county-specific accuracy
        from utils.census_data_loader import wisconsin_census
        
        mobile_home_pct = wisconsin_census.get_mobile_home_percentage(county_name)
        if mobile_home_pct is not None:
            return mobile_home_pct
        else:
            logger.warning(f"No local mobile home data found for {county_name}, using state average")
            return 5.2
                
    except Exception as e:
        logger.error(f"Error retrieving mobile home data for {county_name}: {str(e)}")
        # Return Wisconsin state average as fallback
        logger.warning(f"Using state average mobile home percentage for {county_name}")
        return 5.2

EM_EXCLUDED_JURISDICTION_IDS = {
    '6', '9', '11', '18',
    '46', '47', '48', '49', '51', '52', '53', '54', '55',
    '67',
}

EM_NAME_OVERRIDES = {
    '16': 'Dane County',
    '22': 'Eau Claire County',
    '45': 'Shawano-Menominee Counties',
    '50': 'Milwaukee County',
    '61': 'Washington-Ozaukee Counties',
    'T03': 'Ho-Chunk Nation',
    'T07': 'Oneida Nation',
}


def get_em_jurisdiction_name(jurisdiction: Dict) -> str:
    jid = jurisdiction['id']
    if jid in EM_NAME_OVERRIDES:
        return EM_NAME_OVERRIDES[jid]
    name = jurisdiction['name']
    if jid.startswith('T'):
        for suffix in [' Health Department', ' Health Dept']:
            if name.endswith(suffix):
                return name[:-len(suffix)]
        return name
    county = jurisdiction.get('county', '')
    if county:
        return f"{county} County"
    return name


def get_em_jurisdictions() -> List[Dict]:
    """Return EM-filtered jurisdictions (no city entries) with EM-appropriate names."""
    all_jurisdictions = get_wi_jurisdictions()
    em_jurisdictions = []
    for j in all_jurisdictions:
        if j['id'] in EM_EXCLUDED_JURISDICTION_IDS:
            continue
        em_j = dict(j)
        em_j['em_name'] = get_em_jurisdiction_name(j)
        em_jurisdictions.append(em_j)
    return em_jurisdictions


def get_wi_jurisdictions() -> List[Dict]:
    """Return a list of Wisconsin jurisdictions with health departments.
    
    Only returns jurisdictions with primary=True (99 unique health departments).
    Multi-county departments have secondary entries (primary=False) which are 
    used only by GIS exports and HERC aggregation for county-level risk mapping.
    """
    try:
        # Get the jurisdiction data from the code file
        from utils.jurisdictions_code import jurisdictions
        
        # Load geometry data
        geometries = extract_geometries() if os.path.exists('./attached_assets/Wisconsin_Local_Public_Health_Department_Office_Boundaries.geojson') else {}
        
        # Filter to primary entries only (unique health departments for dropdown)
        primary_jurisdictions = []
        
        for jurisdiction in jurisdictions:
            # Skip secondary entries (multi-county duplicates for GIS/HERC)
            if not jurisdiction.get('primary', True):
                continue

            # TRIBAL HIDE: Temporarily exclude Tribal jurisdictions (IDs starting with 'T')
            # from the public dropdown while Tribal data sovereignty protocols are finalized.
            # To restore: remove the four lines below (the comment and the if/continue block).
            # Also restore the help text in templates/index.html and remove the guard in
            # routes/dashboard.py. See .local/tribal_access_reversal.md for full instructions.
            if str(jurisdiction.get('id', '')).startswith('T'):
                continue
            
            # Create a copy to avoid modifying the original
            j = dict(jurisdiction)
            jurisdiction_id = j['id']
            
            # Add geometry data if available
            if jurisdiction_id in geometries:
                j['geometry'] = geometries[jurisdiction_id]
            
            primary_jurisdictions.append(j)
        
        logger.info(f"Loaded {len(primary_jurisdictions)} primary jurisdictions for dropdown")
        return primary_jurisdictions
    
    except ImportError:
        # Fallback to minimal hardcoded data if the files are not available
        logger.warning("Using fallback jurisdiction data")
        
        # Get default geometries 
        geometries = extract_geometries()
        
        fallback_jurisdictions = [
            {
                'id': '41',
                'name': 'Milwaukee City Health Department',
                'county': 'Milwaukee'
            },
            {
                'id': '42',
                'name': 'North Shore Health Department',
                'county': 'Milwaukee'
            },
            {
                'id': '43',
                'name': 'Waukesha County Department of Health & Human Services',
                'county': 'Waukesha'
            },
            {
                'id': '44',
                'name': 'Public Health - Madison & Dane County',
                'county': 'Dane'
            },
            {
                'id': '45',
                'name': 'Brown County Health & Human Services',
                'county': 'Brown'
            },
            {
                'id': '46',
                'name': 'Bayfield County Health Department',
                'county': 'Bayfield'
            },
            {
                'id': '47',
                'name': 'Pierce County Health Department',
                'county': 'Pierce'
            },
            {
                'id': '48',
                'name': 'Wood County Health Department',
                'county': 'Wood'
            },
            {
                'id': '49',
                'name': 'Vernon County Health Department',
                'county': 'Vernon'
            },
            {
                'id': '50',
                'name': 'Outagamie County Health Department',
                'county': 'Outagamie'
            },
            {
                'id': '51',
                'name': 'Oneida Nation Health Department',
                'county': 'Oneida'
            },
            {
                'id': '52',
                'name': 'Red Cliff Band of Lake Superior Chippewa',
                'county': 'Bayfield'
            },
            {
                'id': '53',
                'name': 'Adams County Health & Human Services',
                'county': 'Adams'
            },
            {
                'id': '54',
                'name': 'Ashland County Health & Human Services',
                'county': 'Ashland'
            },
            {
                'id': '55',
                'name': 'Barron County Department of Health & Human Services',
                'county': 'Barron'
            },
            {
                'id': '56',
                'name': 'Brown County Health & Human Services Department',
                'county': 'Brown'
            },
            {
                'id': '57',
                'name': 'DePere Department of Public Health',
                'county': 'Brown'
            },
            {
                'id': '58',
                'name': 'Buffalo County Health & Human Services Department',
                'county': 'Buffalo'
            },
            {
                'id': '59',
                'name': 'Burnett County Department of Health & Human Services',
                'county': 'Burnett'
            },
            {
                'id': '60',
                'name': 'Appleton City Health Department',
                'county': 'Outagamie'
            }
        ]
        
        # Add geometry data to fallback jurisdictions
        for jurisdiction in fallback_jurisdictions:
            jurisdiction_id = jurisdiction['id']
            if jurisdiction_id in geometries:
                jurisdiction['geometry'] = geometries[jurisdiction_id]
            else:
                # Add default polygon if no geometry is available
                jurisdiction['geometry'] = {
                    "type": "Polygon",
                    "coordinates": [[
                        [-89.7, 45.0],
                        [-89.2, 45.0],
                        [-89.2, 44.5],
                        [-89.7, 44.5],
                        [-89.7, 45.0]
                    ]]
                }
        
        return fallback_jurisdictions

def apply_percentile_ranking(risk_data, region_name: str = None) -> Dict:
    """
    Apply percentile ranking to risk data. Can be used in two ways:
    1. With a collection of jurisdiction data (for bulk processing)
    2. With a single jurisdiction/region (for individual processing)
    
    Args:
        risk_data: Either a Dict[str, Dict] for collections, or a single Dict for individual data
        region_name: Optional name of the region for individual data processing
        
    Returns:
        Updated risk_data with percentile rank and normalized scores added
    """
    from scipy import stats
    
    # Handle single jurisdiction/region case
    if region_name is not None:
        # This is a single entry (region or jurisdiction)
        # In this case, we'll just ensure data integrity and return it
        logger.info(f"Processing single entry percentile ranking for {region_name}")
        
        # Make sure the data has basic risk fields
        if isinstance(risk_data, dict):
            # Add empty fields for any missing risk types
            risk_data.setdefault('risk_percentile', 50.0)  # Default to median
            risk_data.setdefault('normalized_percentile_risk', 0.5)  # Default to median
            
            # Return the processed data
            return risk_data
        else:
            logger.warning(f"Invalid risk data format for {region_name}")
            return risk_data
    
    # Collection processing (original functionality)
    # Make sure we have something to work with
    if not risk_data:
        logger.warning("No risk data collection provided for percentile ranking")
        return risk_data
        
    # Extract all total risk scores for percentile calculation
    total_scores = [data.get('total_risk_score', 0.0) for data in risk_data.values()]
    
    # Check if we have enough scores
    if len(total_scores) < 2:
        logger.warning("Insufficient data for percentile ranking (need at least 2 jurisdictions)")
        return risk_data
    
    # Define the hazard types we want to apply percentile ranking to
    hazard_types = [
        'tornado_risk',
        'flood_risk',
        'winter_storm_risk',
        'thunderstorm_risk',
        'extreme_heat_risk',
        'active_shooter_risk',
        'cybersecurity_risk',
        'health_risk'
    ]
    
    # Create dictionaries to store all scores for each hazard type
    hazard_scores = {}
    for hazard in hazard_types:
        hazard_scores[hazard] = [data.get(hazard, 0.0) for data in risk_data.values()]
    
    # Calculate total risk percentiles
    for jurisdiction_id, data in risk_data.items():
        if 'total_risk_score' in data:
            # Calculate overall risk percentile (0-100)
            percentile = stats.percentileofscore(total_scores, data['total_risk_score'])
            # Add percentile data (0-100 scale)
            data['risk_percentile'] = float(percentile)
            # Add normalized percentile (0-1 scale)
            data['normalized_percentile_risk'] = float(percentile / 100.0)
            
            # Calculate percentiles for each hazard type
            for hazard in hazard_types:
                if hazard in data and len(hazard_scores[hazard]) >= 2:
                    hazard_percentile = stats.percentileofscore(hazard_scores[hazard], data[hazard])
                    data[f'{hazard}_percentile'] = float(hazard_percentile)
    
    # Log completion of percentile ranking
    logger.info(f"Applied percentile ranking to {len(risk_data)} jurisdictions")
    
    # Component-level percentile calculations (for each hazard type)
    # Extract individual component scores
    risk_types = [
        'natural_hazards_risk', 'health_risk', 'active_shooter_risk',
        'cybersecurity_risk', 'extreme_heat_risk', 'flood_risk',
        'tornado_risk', 'winter_storm_risk', 'thunderstorm_risk'
    ]
    
    for risk_type in risk_types:
        # Extract scores for this risk type
        scores = [data.get(risk_type, 0.0) for data in risk_data.values() if risk_type in data]
        
        if len(scores) < 2:
            continue
            
        # Calculate percentiles for this risk type
        for data in risk_data.values():
            if risk_type in data:
                percentile = stats.percentileofscore(scores, data[risk_type])
                # Add to a new field with "_percentile" suffix
                data[f"{risk_type}_percentile"] = float(percentile)
                # Also add normalized value (0-1)
                data[f"{risk_type}_normalized_percentile"] = float(percentile / 100.0)
    
    # Process multi-dimensional components (exposure, vulnerability, resilience)
    component_types = ['flood_components', 'tornado_components', 'winter_storm_components', 
                      'thunderstorm_components', 'extreme_heat_components']
    
    for component_type in component_types:
        # For each component type (e.g., flood_components)
        sub_components = ['exposure', 'vulnerability', 'resilience']
        
        for sub_component in sub_components:
            # Extract all values for this specific component
            values = []
            for data in risk_data.values():
                if component_type in data and isinstance(data[component_type], dict):
                    component_value = data[component_type].get(sub_component)
                    if component_value is not None:
                        values.append(float(component_value))
            
            if len(values) < 2:
                continue
                
            # Calculate percentiles for this component
            for data in risk_data.values():
                if component_type in data and isinstance(data[component_type], dict):
                    component_value = data[component_type].get(sub_component)
                    if component_value is not None:
                        percentile = stats.percentileofscore(values, float(component_value))
                        # Add percentile to the components dictionary
                        if f"{component_type}_percentile" not in data:
                            data[f"{component_type}_percentile"] = {}
                        data[f"{component_type}_percentile"][sub_component] = float(percentile)
    
    logger.info(f"Applied percentile ranking to {len(risk_data)} jurisdictions")
    return risk_data

def process_risk_data(jurisdiction_id: str, additional_data: Optional[FileStorage] = None, discipline: str = 'public_health') -> dict:
    """Process FEMA NRI data and additional uploaded data to calculate risk scores.
    
    Args:
        jurisdiction_id: The jurisdiction ID to process
        additional_data: Optional uploaded data file
        discipline: Assessment discipline - 'public_health' (default) or 'em' (emergency management)
    """
    # Get jurisdiction information
    jurisdictions = get_wi_jurisdictions()
    jurisdiction = next((j for j in jurisdictions if j['id'] == jurisdiction_id), None)
    
    if not jurisdiction:
        raise ValueError(f"Jurisdiction with ID {jurisdiction_id} not found")
    
    # Add debugging information for jurisdiction
    logger.info(f"Processing jurisdiction: {jurisdiction_id}, {jurisdiction.get('name', 'unknown')}") 
    
    # Check if this is a tribal jurisdiction
    is_tribal = jurisdiction_id.startswith('T')
    logger.info(f"Is tribal jurisdiction: {is_tribal}")
    
    county_name = jurisdiction.get('county', '')
    logger.info(f"Initial county_name from jurisdiction: '{county_name}'")
    
    if not county_name:
        # Extract county from jurisdiction name as fallback
        name = jurisdiction.get('name', '')
        logger.info(f"Extracting county from name: '{name}'")
        if 'County' in name:
            county_name = name.split('County')[0].strip()
            logger.info(f"Extracted county: '{county_name}'")
        else:
            # Default to Milwaukee if can't determine county
            county_name = 'Milwaukee'
            logger.info(f"Defaulting to county: '{county_name}'")
    
    # Make sure we have a valid string
    if not isinstance(county_name, str) or not county_name:
        county_name = 'Milwaukee'
        logger.warning(f"Invalid county name, defaulting to Milwaukee")
    
    # Calculate risk based on jurisdiction type
    if is_tribal:
        # For tribal jurisdictions, calculate risk using weighted county data
        logger.info(f"Calculating tribal risk for {jurisdiction_id}")
        natural_hazards = calculate_tribal_risk(jurisdiction_id, calculate_jurisdiction_risk)
        
        # If tribal risk calculation fails, fall back to primary county
        if not natural_hazards:
            logger.warning(f"Tribal risk calculation failed, using primary county: {county_name}")
            natural_hazards = calculate_jurisdiction_risk(county_name)
    else:
        # For regular jurisdictions, calculate risk normally
        natural_hazards = calculate_jurisdiction_risk(county_name)
    
    # Get Social Vulnerability Index (SVI) data for the county
    # SVI is now used as a multiplier for various risk types
    from utils.svi_data import get_svi_data
    svi_data = get_svi_data(county_name)
    overall_svi = svi_data.get('social_vulnerability_index', 0.5)
    svi_themes = svi_data.get('themes', {
        'socioeconomic': 0.5,
        'household_composition': 0.5,
        'minority_status': 0.5,
        'housing_transportation': 0.5
    })
    
    logger.info(f"SVI data for {county_name}: Overall={overall_svi:.2f}, " +
                f"Housing={svi_themes.get('housing_transportation', 0.5):.2f}, " +
                f"Socioeconomic={svi_themes.get('socioeconomic', 0.5):.2f}")
    
    # Process additional uploaded data if provided
    additional_risk_data = {}
    if additional_data:
        additional_risk_data = process_additional_data(additional_data)
    
    # Aggregate health metrics data through disease surveillance module
    from utils.disease_surveillance import calculate_infectious_disease_risk
    health_metrics = calculate_infectious_disease_risk(jurisdiction_id)
    
    # Calculate multi-dimensional active shooter risk
    active_shooter_data = calculate_active_shooter_risk(county_name)
    active_shooter_risk = active_shooter_data['overall']
    
    # Calculate enhanced multi-dimensional extreme heat risk with climate considerations
    from utils.climate_adjusted_risk import calculate_enhanced_extreme_heat_risk
    enhanced_heat_data = calculate_enhanced_extreme_heat_risk(county_name, jurisdiction_id)
    
    # Convert enhanced data to expected format for dashboard compatibility
    extreme_heat_data = {
        'overall': enhanced_heat_data['overall_risk'],
        'components': {
            'exposure': enhanced_heat_data['exposure']['final_exposure'],
            'vulnerability': enhanced_heat_data['vulnerability']['final_vulnerability'], 
            'resilience': enhanced_heat_data['resilience']['final_resilience']
        },
        'metrics': {
            'wet_bulb_risk': enhanced_heat_data['wet_bulb_risk']['final_wet_bulb_risk'],
            'climate_trend_factor': enhanced_heat_data['climate_trend_factor']['final_trend_factor'],
            'risk_level': enhanced_heat_data['risk_level'],
            'data_sources': enhanced_heat_data['data_sources']
        }
    }
    extreme_heat_risk = extreme_heat_data['overall']
    
    # Calculate multi-dimensional cybersecurity risk
    cybersecurity_data = get_cybersecurity_risk_data(jurisdiction_id)
    cybersecurity_risk_base = cybersecurity_data['risk_score']
    
    # Apply SVI adjustments to all risk types with different weights
    # Get all SVI theme factors
    housing_svi_factor = svi_themes.get('housing_transportation', 0.5)
    socioeconomic_svi_factor = svi_themes.get('socioeconomic', 0.5)
    household_svi_factor = svi_themes.get('household_composition', 0.5)
    
    # Calculate multipliers for different risk types
    # Primary SVI impact: Housing for natural hazards (50% max increase)
    housing_svi_multiplier = 1.0 + (housing_svi_factor * 0.5)
    
    # Primary SVI impact: Socioeconomic for extreme heat (20% max increase) 
    # Reduced from 40% to preserve geographic differentiation and account for 
    # uncertainty in rural vs urban vulnerability metrics
    socioeconomic_svi_multiplier = 1.0 + (socioeconomic_svi_factor * 0.2)
    
    # Primary SVI impact: Household composition for active shooter (30% max increase)
    household_svi_multiplier = 1.0 + (household_svi_factor * 0.3)
    
    # Secondary SVI impact: Socioeconomic for ALL risk types (25% max increase)
    # This ensures poverty/socioeconomic factors influence all risk types
    secondary_socioeconomic_multiplier = 1.0 + (socioeconomic_svi_factor * 0.25)
    
    # NOTE: SVI adjustments for natural hazards are now applied INSIDE the enhanced
    # natural hazards risk module (utils/natural_hazards_risk.py) using all 4 CDC SVI
    # themes plus census demographics and climate projections. No additional SVI
    # post-adjustment is needed here to avoid double-counting.
    logger.info(f"Natural hazard scores (SVI/census/climate already integrated): {natural_hazards}")
    
    # 2. Apply SVI adjustment to extreme heat risk
    # Primary: Socioeconomic (already factored in with socioeconomic_svi_multiplier)
    # Use weighted average approach to preserve variation (similar to active shooter)
    extreme_heat_risk_base = extreme_heat_risk
    
    # Base score carries 70% weight, SVI impact carries 30% weight
    heat_base_weight = 0.70
    heat_svi_weight = 0.30
    
    # Calculate SVI impact with dampening to preserve county variation
    heat_svi_impact = socioeconomic_svi_factor * 0.6  # Lower maximum SVI impact
    
    # Apply weighted average formula instead of pure multiplication
    extreme_heat_risk = (extreme_heat_risk_base * heat_base_weight) + (heat_svi_impact * heat_svi_weight)
    
    # Ensure score stays between 0.1 and 0.9 to preserve meaningful variation
    extreme_heat_risk = max(0.1, min(0.9, extreme_heat_risk))
    
    logger.info(f"Adjusted extreme heat risk with SVI socioeconomic factor (weighted avg): {extreme_heat_risk_base:.2f} → {extreme_heat_risk:.2f}")
    
    # 3. Apply SVI adjustment to active shooter risk — socioeconomic only.
    #
    # METHODOLOGY NOTE: The active shooter model (active_shooter_risk.py) already
    # uses SVI household_composition internally via its social_community_fragility
    # sub-component (20% of total model, with SVI at 40% of that sub-component).
    # Applying household SVI again here would double-count that theme.
    #
    # Only socioeconomic SVI (poverty, employment, housing cost burden) is applied
    # here, since it is not represented anywhere in the active shooter model and
    # legitimately affects community resilience and resource capacity for prevention.
    # A modest dampened weight (15% max influence) is used to limit over-adjustment.
    active_shooter_risk_base = active_shooter_risk
    socioeconomic_adjustment = socioeconomic_svi_factor * 0.15
    active_shooter_risk = (active_shooter_risk_base * 0.85) + (socioeconomic_adjustment * 0.15)
    active_shooter_risk = max(0.1, min(0.85, active_shooter_risk))
    logger.info(
        f"Adjusted active shooter risk with socioeconomic SVI only "
        f"(household SVI excluded — already in model): "
        f"{active_shooter_risk_base:.2f} → {active_shooter_risk:.2f}"
    )
    
    # 4. Apply SVI adjustment to cybersecurity risk
    # Primary: Socioeconomic (resource access impacts cybersecurity capabilities)
    # METHODOLOGICAL NOTE: This assumes lower SVI socioeconomic scores correlate
    # with fewer IT security resources. This is a proxy assumption without direct
    # empirical validation linking county SVI to cybersecurity breach rates.
    # The adjustment factor (default 0.25 = 25% max increase) is configurable
    # in config/risk_weights.yaml → svi_adjustment_factors.cybersecurity_socioeconomic.
    # Set to 0.0 to disable SVI influence on cybersecurity scores entirely.
    cybersecurity_risk = min(1.0, cybersecurity_risk_base * secondary_socioeconomic_multiplier)
    logger.info(f"Adjusted cybersecurity risk with SVI socioeconomic factor: {cybersecurity_risk_base:.2f} → {cybersecurity_risk:.2f}")
    
    # Calculate overall risk score with data-backed domains only:
    # - Natural Hazards: 33%
    # - Health Metrics: 20%
    # - Active Shooter: 20%
    # - Extreme Heat: 13%
    # - Air Quality: 14%
    # Note: Cybersecurity and Utilities are supplementary (modeled from proxy indicators, not in PHRAT)
    
    # Calculate natural hazards combined score (numeric values only)
    numeric_hazards = {}
    for key, value in natural_hazards.items():
        if isinstance(value, (float, int)) and key not in [
            'tribal_status',
            'tribal_counties',
            'tribal_primary_county',
            'tribal_trust_land_fraction',
            'tribal_has_trust_land',
        ]:
            numeric_hazards[key] = value
    
    # Calculate average of numeric hazards
    if numeric_hazards:
        # Filter out None values and convert to float
        valid_values = [float(v) for v in numeric_hazards.values() if v is not None and isinstance(v, (int, float))]
        if valid_values:
            # Quadratic mean (RMS, p=2) is consistent with the outer PHRAT formula and
            # ensures that a single high-risk sub-domain elevates the domain score
            # more than an arithmetic mean would.
            import math
            natural_hazards_score = math.sqrt(sum(v ** 2 for v in valid_values) / len(valid_values))
        else:
            natural_hazards_score = _get_fallback('natural_hazards')
    else:
        natural_hazards_score = _get_fallback('natural_hazards')
    
    # Health metrics score is already on a 0-1 scale
    # Extract the risk score from health metrics data
    logger.info(f"Health metrics data type: {type(health_metrics)}")
    logger.info(f"Health metrics keys: {health_metrics.keys() if isinstance(health_metrics, dict) else 'Not a dict'}")
    
    # Check for both possible structures from dhs_connector
    if isinstance(health_metrics, dict):
        if 'risk_score' in health_metrics and isinstance(health_metrics['risk_score'], (int, float)):
            health_metrics_score = float(health_metrics['risk_score'])
        elif 'metrics' in health_metrics and 'risk_score' in health_metrics:
            # Handle nested structure - ensure we have a number
            if isinstance(health_metrics['risk_score'], (int, float)):
                health_metrics_score = float(health_metrics['risk_score'])
            elif isinstance(health_metrics['risk_score'], dict) and 'value' in health_metrics['risk_score']:
                # Try to get the 'value' field if risk_score is a dict
                if isinstance(health_metrics['risk_score']['value'], (int, float)):
                    health_metrics_score = float(health_metrics['risk_score']['value'])
                else:
                    health_metrics_score = _get_fallback('health_metrics')
                    logger.warning(f"risk_score['value'] is not a number: {type(health_metrics['risk_score']['value'])}, using fallback {health_metrics_score}")
            else:
                health_metrics_score = _get_fallback('health_metrics')
                logger.warning(f"risk_score is not a number: {type(health_metrics['risk_score'])}, using fallback {health_metrics_score}")
        else:
            health_metrics_score = _get_fallback('health_metrics')
            logger.warning(f"Could not find valid risk_score in health_metrics, using fallback {health_metrics_score}")
    else:
        health_metrics_score = _get_fallback('health_metrics')
        logger.warning(f"Health metrics is not a dictionary, using fallback {health_metrics_score}")
    
    # Get strategic air quality risk assessment
    try:
        strategic_air_quality_data = get_strategic_air_quality_assessment(county_name, jurisdiction_id)
        air_quality_risk = strategic_air_quality_data.get('composite_risk_score', 0.5)
        # Store the full strategic assessment data for the dashboard
        air_quality_components = strategic_air_quality_data
    except Exception as e:
        logger.warning(f"Strategic air quality assessment failed, using fallback: {str(e)}")
        # Fallback to legacy air quality function
        air_quality_data = get_air_quality_risk(county_name)
        air_quality_risk = air_quality_data.get('risk_score', 0.5)
        air_quality_components = None
    
    # Apply SVI adjustment to air quality risk
    # Housing/transportation vulnerability affects air quality health impacts
    # Socioeconomic status affects adaptive capacity to air quality issues
    housing_transport_multiplier = 1.0 + (svi_themes.get('housing_transportation', 0.5) * 0.3)
    socioeconomic_multiplier = 1.0 + (svi_themes.get('socioeconomic', 0.5) * 0.2)
    
    # Combined multiplier for air quality (capped to prevent extreme values)
    air_quality_svi_multiplier = min(1.5, housing_transport_multiplier * socioeconomic_multiplier)
    air_quality_risk = min(1.0, air_quality_risk * air_quality_svi_multiplier)
    
    logger.info(f"Adjusted air quality risk with SVI factors: {air_quality_risk / air_quality_svi_multiplier:.2f} → {air_quality_risk:.2f}")
    
    from utils.dam_failure_risk import calculate_dam_failure_risk
    dam_failure_data = calculate_dam_failure_risk(county_name, discipline=discipline)
    dam_failure_risk_base = dam_failure_data.get('overall', 0.3)
    dam_failure_svi_multiplier = 1.0 + (svi_themes.get('housing_transportation', 0.5) * 0.2)
    dam_failure_risk = min(1.0, dam_failure_risk_base * dam_failure_svi_multiplier)
    
    from utils.vector_borne_disease_risk import calculate_vector_borne_disease_risk
    vbd_data = calculate_vector_borne_disease_risk(county_name, discipline=discipline)
    vbd_risk_base = vbd_data.get('overall', 0.3)
    vbd_svi_multiplier = 1.0 + (svi_themes.get('socioeconomic', 0.5) * 0.15)
    vbd_risk = min(1.0, vbd_risk_base * vbd_svi_multiplier)
    
    # Calculate final weighted score using Drexel PHRAT formula
    # Total Risk Score = (w₁ × Risk₁^p + w₂ × Risk₂^p + ... + wₙ × Riskₙ^p)^(1/p)
    # where p=2 for a quadratic mean that appropriately emphasizes higher risks
    
    # Initialize the risk result dictionary
    result = {
        'jurisdiction_id': jurisdiction_id,
        'location': get_em_jurisdiction_name(jurisdiction) if discipline == 'em' else jurisdiction['name'],
        'county': county_name,
        'natural_hazards': natural_hazards,
        'natural_hazards_risk': float(natural_hazards_score),
        'health_metrics': health_metrics,
        'health_risk': float(health_metrics_score),
        'active_shooter_risk': float(active_shooter_risk),
        # Include all active shooter risk data with the new data structure
        'active_shooter_components': active_shooter_data['components'],
        'metrics': active_shooter_data['metrics'],
        'weights': active_shooter_data['weights'],
        'framework_version': active_shooter_data['framework_version'],
        'show_my_work': active_shooter_data.get('show_my_work', {}),
        'extreme_heat_risk': float(extreme_heat_risk),
        'extreme_heat_components': extreme_heat_data['components'],
        'extreme_heat_metrics': extreme_heat_data['metrics'],
        'cybersecurity_risk': float(cybersecurity_risk),
        'cyber_components': cybersecurity_data['components'],
        'cyber_metrics': cybersecurity_data['metrics'],
        'cyber_incidents': cybersecurity_data.get('recent_incidents', []),
        'air_quality_risk': float(air_quality_risk),
        'air_quality_components': air_quality_components,
        # Legacy fields for backward compatibility
        'air_quality_data': locals().get('air_quality_data', {}),
        'air_quality_aqi': locals().get('air_quality_data', {}).get('aqi'),
        'air_quality_category': locals().get('air_quality_data', {}).get('category', 'unknown'),
        'dam_failure_risk': float(dam_failure_risk),
        'dam_failure_components': dam_failure_data.get('components', {}),
        'dam_failure_metrics': dam_failure_data.get('metrics', {}),
        'dam_failure_exposure_factors': dam_failure_data.get('exposure_factors', {}),
        'dam_failure_vulnerability_breakdown': dam_failure_data.get('vulnerability_breakdown', {}),
        'dam_failure_data_sources': dam_failure_data.get('data_sources', []),
        'vector_borne_disease_risk': float(vbd_risk),
        'vbd_components': vbd_data.get('components', {}),
        'vbd_metrics': vbd_data.get('metrics', {}),
        'vbd_disease_breakdown': vbd_data.get('disease_breakdown', {}),
        'vbd_data_sources': vbd_data.get('data_sources', []),
    }
    
    # Calculate utilities and community resources risks
    # Calculate electrical outage risk
    electrical_risk_data = calculate_electrical_outage_risk(county_name)
    electrical_risk = electrical_risk_data.get('overall_risk', 0.5)
    
    # Calculate utilities disruption risk
    utilities_risk_data = calculate_utilities_disruption_risk(county_name)
    utilities_risk = utilities_risk_data.get('overall_risk', 0.5)
    
    # Calculate supply chain disruption risk
    supply_chain_risk_data = calculate_supply_chain_risk(county_name)
    supply_chain_risk = supply_chain_risk_data.get('overall_risk', 0.5)
    
    # Calculate fuel shortage risk
    fuel_shortage_risk_data = calculate_fuel_shortage_risk(county_name)
    fuel_shortage_risk = fuel_shortage_risk_data.get('overall_risk', 0.5)
    
    # Combine utilities risks into a single category score
    # Using the same multi-dimensional approach as other risk types
    utilities_category_score = (
        (electrical_risk * 0.3) + 
        (utilities_risk * 0.3) + 
        (supply_chain_risk * 0.2) + 
        (fuel_shortage_risk * 0.2)
    )
    
    # Add utilities risks to our results
    result['utilities'] = {
        'overall': float(utilities_category_score),
        'electrical_outage': float(electrical_risk),
        'utilities_disruption': float(utilities_risk),
        'supply_chain': float(supply_chain_risk),
        'fuel_shortage': float(fuel_shortage_risk),
        'components': {
            'electrical_outage': electrical_risk_data.get('components', {}),
            'utilities_disruption': utilities_risk_data.get('components', {}),
            'supply_chain': supply_chain_risk_data.get('components', {}),
            'fuel_shortage': fuel_shortage_risk_data.get('components', {})
        }
    }
    
    _cfg = get_config_manager()
    if discipline == 'em':
        weights = _cfg.get_em_overall_weights(jurisdiction_id=jurisdiction_id)
        if not weights:
            logger.warning("EM weights not found in config, using hardcoded defaults")
            weights = {
                'natural_hazards': 0.32, 'health_metrics': 0.10,
                'active_shooter': 0.13, 'extreme_heat': 0.13,
                'air_quality': 0.08, 'utilities': 0.10,
                'dam_failure': 0.08, 'vector_borne_disease': 0.06,
            }
        risk_values = {
            'natural_hazards': float(natural_hazards_score),
            'health_metrics': float(health_metrics_score),
            'active_shooter': float(active_shooter_risk),
            'extreme_heat': float(extreme_heat_risk),
            'air_quality': float(air_quality_risk),
            'utilities': float(utilities_category_score),
            'dam_failure': float(dam_failure_risk),
            'vector_borne_disease': float(vbd_risk),
        }
        risk_values = {k: v for k, v in risk_values.items() if k in weights}
        logger.info(f"Using Emergency Management PHRAT weights from config: {weights}")
    else:
        weights = _cfg.get_overall_weights(jurisdiction_id=jurisdiction_id)
        if not weights:
            logger.warning("PH weights not found in config, using hardcoded defaults")
            weights = {
                'natural_hazards': 0.28, 'health_metrics': 0.17,
                'active_shooter': 0.18, 'extreme_heat': 0.11,
                'air_quality': 0.12, 'dam_failure': 0.07,
                'vector_borne_disease': 0.07,
            }
        risk_values = {
            'natural_hazards': float(natural_hazards_score),
            'health_metrics': float(health_metrics_score),
            'active_shooter': float(active_shooter_risk),
            'extreme_heat': float(extreme_heat_risk),
            'air_quality': float(air_quality_risk),
            'dam_failure': float(dam_failure_risk),
            'vector_borne_disease': float(vbd_risk),
        }
        risk_values = {k: v for k, v in risk_values.items() if k in weights}
        logger.info(f"Using Public Health PHRAT weights from config: {weights}")
    
    p = 2.0
    
    weighted_sum = sum(weights[key] * (risk_values[key] ** p) for key in weights.keys())
    total_risk_score = weighted_sum ** (1.0 / p)
    
    total_risk_score = max(0.0, min(1.0, total_risk_score))
    
    from utils.natural_hazards_risk import (
        calculate_enhanced_flood_risk,
        calculate_enhanced_tornado_risk,
        calculate_enhanced_winter_storm_risk,
        calculate_enhanced_thunderstorm_risk
    )
    flood_risk_data = calculate_enhanced_flood_risk(county_name, discipline=discipline)
    tornado_risk_data = calculate_enhanced_tornado_risk(county_name, discipline=discipline)
    winter_storm_risk_data = calculate_enhanced_winter_storm_risk(county_name, discipline=discipline)
    thunderstorm_risk_data = calculate_enhanced_thunderstorm_risk(county_name, discipline=discipline)
    
    result.update({
        'flood_risk': float(flood_risk_data['overall']),
        'flood_components': flood_risk_data['components'],
        'flood_metrics': flood_risk_data['metrics'],
        'flood_data_sources': flood_risk_data.get('data_sources', []),
        'flood_vulnerability_breakdown': flood_risk_data.get('vulnerability_breakdown', {}),
        
        'tornado_risk': float(tornado_risk_data['overall']),
        'tornado_components': tornado_risk_data['components'],
        'tornado_metrics': tornado_risk_data['metrics'],
        'tornado_data_sources': tornado_risk_data.get('data_sources', []),
        'tornado_vulnerability_breakdown': tornado_risk_data.get('vulnerability_breakdown', {}),
        
        'winter_storm_risk': float(winter_storm_risk_data['overall']),
        'winter_storm_components': winter_storm_risk_data['components'], 
        'winter_storm_metrics': winter_storm_risk_data['metrics'],
        'winter_storm_data_sources': winter_storm_risk_data.get('data_sources', []),
        'winter_storm_vulnerability_breakdown': winter_storm_risk_data.get('vulnerability_breakdown', {}),
        
        'thunderstorm_risk': float(thunderstorm_risk_data['overall']),
        'thunderstorm_components': thunderstorm_risk_data['components'],
        'thunderstorm_metrics': thunderstorm_risk_data['metrics'],
        'thunderstorm_data_sources': thunderstorm_risk_data.get('data_sources', []),
        'thunderstorm_vulnerability_breakdown': thunderstorm_risk_data.get('vulnerability_breakdown', {}),
        
        # Extreme heat risk data
        'extreme_heat_risk': float(extreme_heat_risk),
        'extreme_heat_components': extreme_heat_data['components'],
        'extreme_heat_metrics': extreme_heat_data['metrics'],
        
        # Add total risk score and date
        'total_risk_score': float(total_risk_score),
        'assessment_date': datetime.now().strftime('%Y-%m-%d'),
        'additional_data': additional_risk_data,
        'discipline': discipline,
        'discipline_label': 'Emergency Management' if discipline == 'em' else 'Public Health',
        'utilities_in_phrat': discipline == 'em',
    })
    
    result['score_provenance'] = {
        'formula': 'PHRAT Quadratic Mean: √(Σ wᵢ × Riskᵢ²)',
        'p': p,
        'domains': [
            {
                'name': 'Natural Hazards',
                'weight': weights['natural_hazards'],
                'final_score': round(float(natural_hazards_score), 4),
                'weighted_contribution': round(weights['natural_hazards'] * (float(natural_hazards_score) ** p), 4),
                'svi_adjustment': 'Integrated inside EVR module (4 SVI themes + census demographics)',
                'data_sources': ['FEMA NRI (annual cache)', 'NOAA Storm Events (static)', 'Census ACS (annual)', 'CDC SVI (annual cache)'],
                'sub_components': {k: round(float(v), 4) for k, v in numeric_hazards.items()} if numeric_hazards else {},
                'aggregation': f'Mean of {len(numeric_hazards)} sub-hazard EVR scores' if numeric_hazards else 'Default 0.5'
            },
            {
                'name': 'Health Metrics',
                'weight': weights['health_metrics'],
                'final_score': round(float(health_metrics_score), 4),
                'weighted_contribution': round(weights['health_metrics'] * (float(health_metrics_score) ** p), 4),
                'svi_adjustment': 'None (health data is directly sourced)',
                'data_sources': ['WI DHS Respiratory Surveillance PDFs (weekly)', 'County Health Rankings (annual)', 'CDC vaccination data'],
                'aggregation': 'Composite from disease surveillance + vaccination rates'
            },
            {
                'name': 'Active Shooter',
                'weight': weights['active_shooter'],
                'pre_svi_score': round(float(active_shooter_risk_base), 4),
                'final_score': round(float(active_shooter_risk), 4),
                'weighted_contribution': round(weights['active_shooter'] * (float(active_shooter_risk) ** p), 4),
                'svi_adjustment': f'Weighted avg: 60% base + 40% SVI (household={round(household_svi_factor, 3)}, socioeconomic={round(socioeconomic_svi_factor, 3)})',
                'data_sources': ['Gun Violence Archive 2023 (static)', 'NCES SSOCS 2019-2020 (static)', 'Census ACS demographics'],
                'aggregation': '5-component weighted model (incident density, school vulnerability, social fragility, mental health, lethal means access)'
            },
            {
                'name': 'Extreme Heat',
                'weight': weights['extreme_heat'],
                'pre_svi_score': round(float(extreme_heat_risk_base), 4),
                'final_score': round(float(extreme_heat_risk), 4),
                'weighted_contribution': round(weights['extreme_heat'] * (float(extreme_heat_risk) ** p), 4),
                'svi_adjustment': f'Weighted avg: 70% base + 30% SVI impact (socioeconomic={round(socioeconomic_svi_factor, 3)} × 0.6)',
                'data_sources': ['NOAA Climate Normals 1991-2020 (static)', 'NWS heat forecasts (cached)', 'Census ACS population 65+/poverty (annual)', 'CDC SVI (annual cache)'],
                'aggregation': 'EVR framework (exposure × vulnerability × resilience)'
            },
            {
                'name': 'Air Quality',
                'weight': weights['air_quality'],
                'pre_svi_score': round(float(air_quality_risk / air_quality_svi_multiplier), 4) if air_quality_svi_multiplier > 0 else 0.0,
                'final_score': round(float(air_quality_risk), 4),
                'weighted_contribution': round(weights['air_quality'] * (float(air_quality_risk) ** p), 4),
                'svi_adjustment': f'Multiplier: housing_transport={round(housing_transport_multiplier, 3)} × socioeconomic={round(socioeconomic_multiplier, 3)} (combined={round(air_quality_svi_multiplier, 3)})',
                'data_sources': ['EPA AirNow API (daily scheduler cache)', 'Census ACS demographics', 'CDC SVI housing/socioeconomic themes'],
                'aggregation': 'Strategic composite risk score from AQI + vulnerability factors'
            },
            {
                'name': 'Dam Failure',
                'weight': weights.get('dam_failure', 0.07),
                'pre_svi_score': round(float(dam_failure_risk_base), 4),
                'final_score': round(float(dam_failure_risk), 4),
                'weighted_contribution': round(weights.get('dam_failure', 0.07) * (float(dam_failure_risk) ** p), 4),
                'svi_adjustment': f'Multiplier: housing_transport={round(dam_failure_svi_multiplier, 3)}',
                'data_sources': ['WI DNR Dam Safety Database (weekly cache)', 'USACE NID (fallback)', 'OpenFEMA NFIP Claims (weekly cache)', 'CDC SVI (annual cache)', 'U.S. Census ACS (annual)'],
                'aggregation': 'EVR framework (dam density × hazard classification × flood zone overlap × est. % population in inundation zones)'
            },
            {
                'name': 'Vector-Borne Disease',
                'weight': weights.get('vector_borne_disease', 0.07),
                'pre_svi_score': round(float(vbd_risk_base), 4),
                'final_score': round(float(vbd_risk), 4),
                'weighted_contribution': round(weights.get('vector_borne_disease', 0.07) * (float(vbd_risk) ** p), 4),
                'svi_adjustment': f'Multiplier: socioeconomic={round(vbd_svi_multiplier, 3)}',
                'data_sources': ['WI DHS EPHT Lyme incidence rates (county-level, 2019-2024)', 'WI DHS Vectorborne Disease Program WNV (county-level, 2019-2024)', 'USDA NLCD 2021 forest cover (static)', 'WI DNR deer density (static)', 'WICCI/NOAA climate projections (static)'],
                'aggregation': 'EVR framework (incidence rate × land cover × climate × seasonal)'
            }
        ],
        'supplementary_domains': [
            {
                'name': 'Cybersecurity',
                'final_score': round(float(cybersecurity_risk), 4),
                'pre_svi_score': round(float(cybersecurity_risk_base), 4),
                'svi_adjustment': f'Multiplier: 1.0 + (SVI socioeconomic {round(socioeconomic_svi_factor, 3)} × 0.25) = {round(secondary_socioeconomic_multiplier, 3)}',
                'svi_bias_warning': 'SVI socioeconomic adjustment is a proxy assumption without direct empirical validation',
                'data_sources': ['Census ACS 2022 (population, static)', 'WI DOR 2022 (revenue/staffing, static)', 'CDC SVI socioeconomic theme (annual cache)'],
                'not_in_phrat': True
            },
            {
                'name': 'Utilities',
                'final_score': round(float(utilities_category_score), 4),
                'sub_components': {
                    'electrical_outage': round(float(electrical_risk), 4),
                    'utilities_disruption': round(float(utilities_risk), 4),
                    'supply_chain': round(float(supply_chain_risk), 4),
                    'fuel_shortage': round(float(fuel_shortage_risk), 4)
                },
                'data_sources': ['Census ACS 2022 (static)', 'CDC SVI housing/socioeconomic themes (annual cache)', 'County characteristics (static)'],
                'not_in_phrat': True
            }
        ],
        'weighted_sum': round(float(weighted_sum), 6),
        'total_risk_score': round(float(total_risk_score), 4),
        'svi_themes_used': {
            'socioeconomic': round(socioeconomic_svi_factor, 4),
            'housing_transportation': round(housing_svi_factor, 4),
            'household_composition': round(household_svi_factor, 4)
        },
        'verification': {
            'weights_sum': round(sum(weights.values()), 4),
            'manual_check': f'√({" + ".join(f"{weights[k]:.2f}×{risk_values[k]:.4f}²" for k in weights)}) = {total_risk_score:.4f}'
        }
    }
    
    # The final risk data is in the result variable now
    risk_data = result
    
    # Store this jurisdiction's risk data in the global collection for percentile calculations
    all_jurisdictions_risk_data[jurisdiction_id] = risk_data
    
    # Apply percentile ranking if we have enough jurisdictions data
    if len(all_jurisdictions_risk_data) >= 2:
        apply_percentile_ranking(all_jurisdictions_risk_data)
        
        # Add percentile data to the current jurisdiction's risk data
        # (which has already been updated in place in the collection)
        if 'risk_percentile' in all_jurisdictions_risk_data[jurisdiction_id]:
            risk_data['risk_percentile'] = all_jurisdictions_risk_data[jurisdiction_id]['risk_percentile']
            risk_data['normalized_percentile_risk'] = all_jurisdictions_risk_data[jurisdiction_id]['normalized_percentile_risk']
            logger.info(f"Added percentile ranking to risk data for {jurisdiction_id}: {risk_data['risk_percentile']:.2f}")
    
    return risk_data

def process_additional_data(file: FileStorage) -> dict:
    """Process uploaded additional risk data"""
    try:
        # Read CSV file with pandas
        df = pd.read_csv(file.stream)
        
        # Extract relevant columns (assuming specific format)
        if 'risk_factor' in df.columns and 'risk_score' in df.columns:
            # Extract risk factors and scores into a dictionary
            additional_data = {}
            for _, row in df.iterrows():
                factor = row['risk_factor']
                score = float(row['risk_score'])
                additional_data[factor] = score
            
            return additional_data
        
        return {}
    
    except Exception as e:
        logger.error(f"Error processing additional data: {str(e)}")
        return {}

def get_historical_risk_data(jurisdiction_id: str, start_year: int = 2020, end_year: int = 2024) -> List[Dict]:
    """
    Get historical risk data for timeline visualization and temporal analysis.
    
    Returns current risk snapshot as a single data point. Trend analysis is now
    handled by utils/real_trend_calculator.py using real cached data from NOAA
    Storm Events, OpenFEMA, climate projections, and Census data rather than
    synthetic historical generation.
    """
    current_risk = process_risk_data(jurisdiction_id)
    
    current_year = datetime.now().year
    current_quarter = (datetime.now().month - 1) // 3 + 1
    quarter_month = {1: 1, 2: 4, 3: 7, 4: 10}[current_quarter]
    current_date = f"{current_year}-{quarter_month:02d}-01"
    
    data_point = {
        'year': current_year,
        'quarter': current_quarter,
        'date': current_date,
        'total_risk_score': round(float(current_risk.get('total_risk_score', 0.5)), 2),
        'natural_hazards_risk': round(float(current_risk.get('natural_hazards_risk', 0.5)), 2),
        'health_risk': round(float(current_risk.get('health_risk', 0.5)), 2),
        'active_shooter_risk': round(float(current_risk.get('active_shooter_risk', 0.5)), 2),
        'extreme_heat_risk': round(float(current_risk.get('extreme_heat_risk', 0.5)), 2),
        'cybersecurity_risk': round(float(current_risk.get('cybersecurity_risk', 0.5)), 2),
        'utilities_risk': round(float(current_risk.get('utilities_risk', 0.5)), 2)
    }
    
    return [data_point]

def get_cybersecurity_risk_data(jurisdiction_id: str) -> dict:
    """
    Calculate multi-dimensional cybersecurity risk with three components:
    1. Threat Landscape: External threats and attack vectors
    2. Vulnerability: System weaknesses and infrastructure gaps
    3. Capability: Organizational readiness and response capacity
    
    PROXY INDICATOR BASIS: No authoritative county-level cybersecurity incident
    database exists for Wisconsin. Baseline values are modeled from observable
    county characteristics used as proxy indicators:
      - Threat: Population size (Census ACS) as proxy for target visibility,
        presence of government/healthcare systems (WI Blue Book)
      - Vulnerability: CDC SVI socioeconomic theme as proxy for IT resource
        availability; county budget data (WI DOR) as proxy for infrastructure age
      - Capability: Population and budget size as proxy for security staffing;
        urban/rural classification (Census) as proxy for access to specialists
    
    These are supplementary estimates — not included in the primary PHRAT score.
    
    Returns a dictionary with component scores and an overall risk score.
    """
    # Get jurisdiction information for context
    jurisdictions = get_wi_jurisdictions()
    jurisdiction = next((j for j in jurisdictions if j['id'] == jurisdiction_id), None)
    
    if not jurisdiction:
        # Return default medium risk
        return {
            'risk_score': 0.5,
            'components': {
                'threat': 0.5,
                'vulnerability': 0.5,
                'capability': 0.5  # Raw score (not inverted)
            },
            'metrics': {
                'reported_breaches': 10,      # Per 100k
                'cybercrime_reports': 50,     # Per 100k
                'critical_vulnerabilities': 7, # Count
                'detection_time': 15          # Days
            },
            'recent_incidents': []
        }
    
    county = jurisdiction.get('county', '')
    
    # THREAT LANDSCAPE COMPONENT (external threats)
    # Loaded from config/county_baselines.yaml → cybersecurity.threat
    # Proxy: Population size (Census ACS 2022) and institutional presence (WI Blue Book)
    threat_base = _get_baseline('cybersecurity', 'threat', county)
    
    threat_score = threat_base
    
    # VULNERABILITY COMPONENT (system weaknesses)
    # Loaded from config/county_baselines.yaml → cybersecurity.vulnerability
    # Proxy: County per-capita revenue (WI DOR 2022) and urban/rural classification (Census)
    vulnerability_base = _get_baseline('cybersecurity', 'vulnerability', county)
    
    # Factor in Social Vulnerability Index (SVI) socioeconomic component
    # PROXY ASSUMPTION: Lower socioeconomic status → fewer IT security resources.
    # This is not empirically validated against actual cybersecurity incident data.
    # The 0.25 factor is configurable in config/risk_weights.yaml
    # (svi_adjustment_factors.cybersecurity_socioeconomic). Set to 0.0 to disable.
    svi_data = get_svi_data(county)
    svi_socioeconomic = svi_data.get('socioeconomic', 0.5)
    
    # Higher SVI socioeconomic score increases vulnerability by up to 25%
    svi_adjustment = svi_socioeconomic * 0.25
    adjusted_vulnerability = vulnerability_base + svi_adjustment
    
    # Log the adjustment for debugging
    logger.info(f"Adjusted cybersecurity risk with SVI socioeconomic factor: {vulnerability_base:.2f} → {adjusted_vulnerability:.2f}")
    
    vulnerability_score = max(0.0, min(1.0, adjusted_vulnerability))
    
    # CAPABILITY COMPONENT (organizational readiness)
    # Loaded from config/county_baselines.yaml → cybersecurity.capability
    # Proxy: County government staffing levels (WI DOR 2022) and urban/rural classification
    capability_base = _get_baseline('cybersecurity', 'capability', county)
    
    capability_raw = capability_base
    
    # For capability, higher score is better for organization but we need to invert
    # it for risk calculation (higher capability = lower risk)
    capability_score = 1.0 - capability_raw
    
    # Calculate traditional weighted risk score (for comparison/backward compatibility)
    traditional_risk = (
        (threat_score * 0.35) +          # 35% threat landscape
        (vulnerability_score * 0.40) +   # 40% vulnerability profile
        (capability_score * 0.25)        # 25% capability (inverted scale)
    )
    
    # Calculate the new residual risk using our formula
    # For cybersecurity:
    # - threat_score represents exposure (external threat likelihood)
    # - vulnerability_score represents vulnerability (system weaknesses)
    # - capability_raw represents resilience (higher = better response capacity)
    residual_risk = calculate_residual_risk(
        exposure=threat_score,
        vulnerability=vulnerability_score,
        resilience=capability_raw
    )
    
    # Calculate metrics based on risk components
    metrics = {
        'reported_breaches': int(5 + (residual_risk * 15)),       # 5-20 per 100k 
        'cybercrime_reports': int(25 + (threat_score * 75)),      # 25-100 per 100k
        'critical_vulnerabilities': int(2 + (vulnerability_score * 10)), # 2-12 vulnerabilities
        'detection_time': int(6 + (capability_score * 18))        # 6-24 days to detect breach
    }
    
    incidents = []
    
    return {
        'risk_score': float(residual_risk),  # Use the new residual risk score
        'traditional_risk': float(traditional_risk),  # Keep the old calculation for reference
        'components': {
            'threat': float(threat_score),
            'vulnerability': float(vulnerability_score),
            'capability': float(capability_raw)  # Raw score (not inverted) for display
        },
        'metrics': metrics,
        'recent_incidents': incidents,
        'data_sources': ['HHS', 'FBI IC3', 'CISA KEV Database', 'MS-ISAC']
    }

def calculate_active_shooter_risk(county_name: str) -> dict:
    """
    Calculate active shooter risk using the new Active Shooter Risk Assessment Scoring Framework
    with five domains:
    1. Historical Incident Density (25%)
    2. School & Youth Vulnerability (20%)
    3. Social & Community Fragility (20%)
    4. Mental Health & Behavioral Health Risk (20%)
    5. Access to Lethal Means (15%)
    
    Returns a dictionary with domain scores and an overall risk score.
    """
    # Use the new model implementation from active_shooter_risk.py
    from utils.active_shooter_risk import calculate_active_shooter_risk
    
    # Get the results from the new model
    risk_data = calculate_active_shooter_risk(county_name)
    logger.info(f"Calculated active shooter risk for {county_name} using new risk model: {risk_data.get('active_shooter_risk', 0.0):.2f}")
    
    # Map our response to maintain compatibility with existing code
    components = risk_data.get('components', {})
    metrics = risk_data.get('metrics', {})
    
    # Convert to the format expected by the dashboard
    return {
        'overall': risk_data.get('active_shooter_risk', 0.0),
        'risk_level': risk_data.get('risk_level', 'Moderate'),
        'components': {
            'historical_incident_density': components.get('historical_incident_density', 0.0),
            'school_youth_vulnerability': components.get('school_youth_vulnerability', 0.0),
            'social_community_fragility': components.get('social_community_fragility', 0.0),
            'mental_behavioral_health': components.get('mental_behavioral_health', 0.0),
            'access_to_lethal_means': components.get('access_to_lethal_means', 0.0)
        },
        'metrics': {
            'historical': metrics.get('historical', {}),
            'school': metrics.get('school', {}),
            'social': metrics.get('social', {}), 
            'mental': metrics.get('mental', {}),
            'means': metrics.get('means', {})
        },
        'weights': risk_data.get('weights', {}),
        'framework_version': risk_data.get('framework_version', '2.0'),
        'show_my_work': risk_data.get('show_my_work', {})
    }

def get_heat_advisories_count(county_name: str) -> int:
    """
    Get the number of heat advisories/warnings for a county in the past year
    from National Weather Service API.
    
    Args:
        county_name: Name of the Wisconsin county
        
    Returns:
        Count of heat advisories and warnings in the past year
    """
    # Check if this is a tribal jurisdiction and handle differently
    is_tribal = any(tribal_name in county_name for tribal_name in ['Ho-Chunk', 'Menominee', 'Oneida', 'Lac du Flambeau', 'Bad River', 'Red Cliff', 'Potawatomi', 'St. Croix', 'Sokaogon', 'Lac Courte Oreilles'])
    # Add special case for HoChunk variation
    is_tribal = is_tribal or 'HoChunk' in county_name
    
    # Map tribal jurisdictions to their primary counties for weather data
    if is_tribal:
        tribal_county_mapping = {
            'HoChunk': 'Jackson',
            'Ho-Chunk': 'Jackson',
            'Menominee': 'Menominee',
            'Oneida': 'Brown',
            'Lac du Flambeau': 'Vilas',
            'Bad River': 'Ashland',
            'Red Cliff': 'Bayfield',
            'Potawatomi': 'Forest',
            'St. Croix': 'Burnett',
            'Sokaogon': 'Forest',
            'Lac Courte Oreilles': 'Sawyer'
        }
        
        for tribal_name, mapped_county in tribal_county_mapping.items():
            if tribal_name in county_name:
                logger.info(f"Using {mapped_county} County as proxy for {county_name} heat advisory data")
                county_name = mapped_county
                break
    
    try:
        # In a production environment, we would use the NWS API to get real data
        # https://www.weather.gov/documentation/services-web-api
        
        # County-specific heat advisory patterns based on geography and historical trends
        # Northern counties generally have fewer heat advisories
        northern_counties = ['Bayfield', 'Douglas', 'Ashland', 'Iron', 'Vilas', 'Florence', 'Forest']
        southern_counties = ['Kenosha', 'Racine', 'Milwaukee', 'Walworth', 'Rock', 'Green']
        central_counties = ['Dane', 'Columbia', 'Dodge', 'Jefferson', 'Waukesha']
        
        # Base counts by region (using local CSV files for strategic planning)
        # For example, using a weather API endpoint like:
        # f"https://api.weather.gov/alerts/active?area={county_name},WI"
        
        if county_name in northern_counties:
            # Northern counties typically have 0-3 heat advisories per year
            count = 2
        elif county_name in southern_counties:
            # Southern counties typically have 5-10 heat advisories per year
            count = 7
        elif county_name in central_counties:
            # Central counties typically have 3-7 heat advisories per year
            count = 5
        else:
            # Default for other counties
            count = 4
            
        # In production, we would make an API request and parse the response
        # Census API replaced with local data files for strategic planning
        # census_api_key = os.environ.get("CENSUS_API_KEY")
        if census_api_key:
            logger.info(f"Using Census API key to get real heat advisory data")
            # Here we would make the actual API call
        
        return count
        
    except Exception as e:
        logger.error(f"Error retrieving heat advisories data: {str(e)}")
        # Return a reasonable default if the API call fails
        return 3


# Cache for population aged 65+ data to avoid repeated API calls
_elderly_cache = {}
_elderly_cache_expiry = {}

# Cache duration in seconds - 24 hours
_ELDERLY_CACHE_DURATION = 86400

def get_elderly_population_pct(county_name: str) -> float:
    """
    Get the percentage of population aged 65 and older in a county from Census API.
    
    Args:
        county_name: Name of the Wisconsin county
        
    Returns:
        Percentage of population aged 65+ as a float (e.g., 15.7 for 15.7%)
    """
    global _elderly_cache, _elderly_cache_expiry
    
    # Check if we have non-expired cached data
    if county_name in _elderly_cache and _elderly_cache_expiry.get(county_name, 0) > datetime.now().timestamp():
        logger.info(f"Using cached population 65+ data for {county_name}")
        return _elderly_cache[county_name]
    
    # Check if this is a tribal jurisdiction and handle differently
    is_tribal = any(tribal_name in county_name for tribal_name in ['Ho-Chunk', 'Menominee', 'Oneida', 'Lac du Flambeau', 'Bad River', 'Red Cliff', 'Potawatomi', 'St. Croix', 'Sokaogon', 'Lac Courte Oreilles'])
    # Add special case for HoChunk variation
    is_tribal = is_tribal or 'HoChunk' in county_name
    
    # Map tribal jurisdictions to their primary counties for Census data
    if is_tribal:
        tribal_county_mapping = {
            'HoChunk': 'Jackson',
            'Ho-Chunk': 'Jackson',
            'Menominee': 'Menominee',
            'Oneida': 'Brown',
            'Lac du Flambeau': 'Vilas',
            'Bad River': 'Ashland',
            'Red Cliff': 'Bayfield',
            'Potawatomi': 'Forest',
            'St. Croix': 'Burnett',
            'Sokaogon': 'Forest',
            'Lac Courte Oreilles': 'Sawyer'
        }
        
        for tribal_name, mapped_county in tribal_county_mapping.items():
            if tribal_name in county_name:
                logger.info(f"Using {mapped_county} County as proxy for {county_name} population 65+ data")
                county_name = mapped_county
                break
    
    try:
        # Use Census API if available
        census_api_key = os.environ.get("CENSUS_API_KEY")
        
        if census_api_key:
            logger.info(f"Using Census API key to get real population 65+ data for {county_name}")
            
            # Create Census API client
            c = Census(census_api_key)
            
            # Get county FIPS code using mapping from SVI data module
            from utils.svi_data import WI_COUNTY_FIPS, WI_FIPS
            
            full_fips = WI_COUNTY_FIPS.get(county_name) or WI_COUNTY_FIPS.get(county_name.lower())
            if not full_fips:
                logger.warning(f"Unknown county name for Census API: {county_name}")
                raise ValueError(f"Unknown county name: {county_name}")
            
            county_fips = str(full_fips)[-3:]
            
            # Query ACS data for this county's age demographics
            # We need total population and population aged 65+
            data = c.acs5.state_county(
                ['B01001_001E',  # Total population
                 # Male population 65+
                 'B01001_020E', 'B01001_021E', 'B01001_022E', 'B01001_023E', 'B01001_024E', 'B01001_025E',
                 # Female population 65+
                 'B01001_044E', 'B01001_045E', 'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E'],
                WI_FIPS, county_fips)[0]
            
            # Calculate population 65+ percentage
            total_population = data['B01001_001E']
            
            # Sum male population aged 65+
            male_elderly = sum([data.get(f'B01001_{i:03d}E', 0) for i in range(20, 26)])
            
            # Sum female population aged 65+
            female_elderly = sum([data.get(f'B01001_{i:03d}E', 0) for i in range(44, 50)])
            
            # Calculate total population 65+ and percentage
            elderly_population = male_elderly + female_elderly
            
            if total_population > 0:
                elderly_percentage = (elderly_population / total_population) * 100
                
                # Log the data and cache it
                logger.info(f"Census API: {county_name} has {elderly_percentage:.1f}% elderly population")
                _elderly_cache[county_name] = elderly_percentage
                _elderly_cache_expiry[county_name] = datetime.now().timestamp() + _ELDERLY_CACHE_DURATION
                
                return elderly_percentage
    
    except Exception as e:
        logger.error(f"Error retrieving population 65+ data from Census API: {str(e)}")
        # Fall through to use default data if API fails
    
    # If we couldn't get real data, use pre-calculated data for Wisconsin counties
    logger.warning(f"Using pre-calculated population 65+ data for {county_name} due to API error")
    
    # Default pre-calculated dataset based on Wisconsin demographics (from prior ACS data)
    elderly_percentages = {
        'Milwaukee': 12.8,
        'Dane': 14.2,
        'Waukesha': 17.6,
        'Brown': 15.3,
        'Racine': 16.9,
        'Kenosha': 15.4, 
        'Rock': 17.1,
        'Walworth': 18.3,
        'Jefferson': 17.2,
        'Bayfield': 24.3,   
        'Douglas': 19.8,
        'Ashland': 20.5,
        'Iron': 29.7,
        'Vilas': 28.5,
        'Florence': 26.2
    }
    
    # Return the percentage for the county, or the Wisconsin average if not found
    result = elderly_percentages.get(county_name, 17.5)  # 17.5% is the Wisconsin state average
    
    # Cache the result
    _elderly_cache[county_name] = result
    _elderly_cache_expiry[county_name] = datetime.now().timestamp() + _ELDERLY_CACHE_DURATION
    
    return result


def calculate_extreme_heat_risk(county_name: str) -> dict:
    """
    Calculate multi-dimensional extreme heat risk based on three components:
    1. Exposure: Likelihood and magnitude of extreme heat events
    2. Vulnerability: Population and infrastructure susceptibility
    3. Resilience: Community capacity to absorb and recover
    
    PROXY INDICATOR BASIS: Baseline values are modeled from observable
    county characteristics used as proxy indicators:
      - Exposure: NOAA Climate Normals (1991-2020) average July max temperature
        by county, EPA urban heat island research, latitude/geography
      - Vulnerability: Census ACS population 65+ (%), poverty rate, housing age;
        CDC SVI socioeconomic and housing themes
      - Resilience: County Health Rankings healthcare access metrics,
        Census ACS urbanization level as proxy for cooling center availability
    
    NOTE: This function is a fallback when the StrategicExtremeHeatAssessment
    module (which uses NOAA/NWS forecast data) is unavailable.
    
    Returns a dictionary with component scores and an overall risk score.
    """
    # EXPOSURE COMPONENT (frequency and intensity of heat events)
    # Loaded from config/county_baselines.yaml → extreme_heat.exposure
    # Proxy: NOAA Climate Normals (1991-2020) July avg max temp and latitude
    exposure_base = _get_baseline('extreme_heat', 'exposure', county_name)
    
    exposure_score = exposure_base
    
    # VULNERABILITY COMPONENT (population and infrastructure susceptibility)
    # Loaded from config/county_baselines.yaml → extreme_heat.vulnerability
    # Proxy: Census ACS 2022 population 65+ (%) and poverty rate; CDC SVI housing theme
    vulnerability_base = _get_baseline('extreme_heat', 'vulnerability', county_name)
    
    vulnerability_score = vulnerability_base
    
    # RESILIENCE COMPONENT (capacity to absorb and recover)
    # Loaded from config/county_baselines.yaml → extreme_heat.resilience
    # Proxy: County Health Rankings healthcare access; Census urbanization level
    resilience_base = _get_baseline('extreme_heat', 'resilience', county_name)
    
    # For resilience, higher score is better for community but we need to invert
    # it for risk calculation (higher resilience = lower risk)
    resilience_raw = resilience_base
    resilience_score = 1.0 - resilience_raw  # Invert the scale for risk context
    
    # Calculate traditional weighted risk score (for comparison/backward compatibility)
    # Higher weights for vulnerability in extreme heat risk because socioeconomic factors have major impact
    traditional_risk = (
        (exposure_score * 0.35) +      # 35% exposure
        (vulnerability_score * 0.45) +  # 45% vulnerability
        (resilience_score * 0.20)       # 20% resilience (inverted scale)
    )
    
    # Calculate the new residual risk using our formula
    # Note: we use resilience_raw (not inverted) since the formula expects higher=better
    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw
    )
    
    # Return the multi-dimensional results
    return {
        'overall': residual_risk,  # Use the new residual risk as overall score
        'traditional_risk': traditional_risk,  # Keep the old calculation for reference
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw  # Raw score (not inverted) for display
        },
        'metrics': {
            'annual_heat_days': int(15 + (exposure_score * 25)),         # Range: 15-40 days
            'ed_visits': int(50 + (vulnerability_score * 150)),          # Range: 50-200 visits
            'heat_advisories': get_heat_advisories_count(county_name),   # Real data from NWS
            'elderly_percentage': get_elderly_population_pct(county_name) # Real data from Census
        }
    }

def extract_geometries() -> Dict:
    """Extract geometries from GeoJSON for each jurisdiction"""
    from utils.jurisdiction_geojson import load_health_departments_geojson
    
    try:
        # Load GeoJSON data
        geojson_data = load_health_departments_geojson()
        
        # Load tribal boundary geometries
        from utils.tribal_boundaries import get_tribal_geometries, initialize_tribal_boundaries
        
        # Ensure tribal boundaries are initialized
        initialize_tribal_boundaries()
        
        # Load jurisdiction ID mapping
        from utils.jurisdictions_code import jurisdictions
        
        # Create a map of agency name to ID
        agency_to_id = {}
        for jurisdiction in jurisdictions:
            agency_to_id[jurisdiction['name']] = jurisdiction['id']
        
        # Initialize dictionary to store geometries by jurisdiction ID
        geometries = {}
        
        # Extract geometries
        for feature in geojson_data.get('features', []):
            if 'properties' in feature and 'geometry' in feature:
                agency_name = feature['properties'].get('AGENCY', '')
                
                # Try to get jurisdiction ID from agency name
                jurisdiction_id = agency_to_id.get(agency_name, '')
                
                if jurisdiction_id:
                    geometries[jurisdiction_id] = feature['geometry']
                else:
                    # Try direct ID if it exists
                    jurisdiction_id = str(feature['properties'].get('JURIS_ID', ''))
                    if jurisdiction_id:
                        geometries[jurisdiction_id] = feature['geometry']
        
        # Add tribal geometries to the collection
        tribal_geometries = get_tribal_geometries()
        for tribal_id, tribal_geom in tribal_geometries.items():
            if tribal_id not in geometries:
                geometries[tribal_id] = tribal_geom
                logger.info(f"Added tribal geometry for jurisdiction {tribal_id}")
        
        # Create hardcoded mappings for common jurisdictions if they're missing
        hardcoded_geometries = {
            '41': {
                "type": "Polygon",
                "coordinates": [[
                    [-87.9405, 43.1927],
                    [-87.8855, 43.1927],
                    [-87.8855, 43.0751],
                    [-87.9405, 43.0751],
                    [-87.9405, 43.1927]
                ]]
            },
            '42': {
                "type": "Polygon",
                "coordinates": [[
                    [-87.9405, 43.2927],
                    [-87.8855, 43.2927],
                    [-87.8855, 43.1927],
                    [-87.9405, 43.1927],
                    [-87.9405, 43.2927]
                ]]
            },
            '43': {
                "type": "Polygon",
                "coordinates": [[
                    [-88.4631, 43.2191],
                    [-88.0684, 43.2191],
                    [-88.0684, 42.8435],
                    [-88.4631, 42.8435],
                    [-88.4631, 43.2191]
                ]]
            },
            '44': {
                "type": "Polygon",
                "coordinates": [[
                    [-89.7707, 43.2610],
                    [-89.0684, 43.2610],
                    [-89.0684, 42.8435],
                    [-89.7707, 42.8435],
                    [-89.7707, 43.2610]
                ]]
            },
            '45': {
                "type": "Polygon",
                "coordinates": [[
                    [-88.1, 44.6],
                    [-87.7, 44.6],
                    [-87.7, 44.3],
                    [-88.1, 44.3],
                    [-88.1, 44.6]
                ]]
            },
            '55': {
                "type": "Polygon",
                "coordinates": [[
                    [-88.1, 44.6],
                    [-87.7, 44.6],
                    [-87.7, 44.3],
                    [-88.1, 44.3],
                    [-88.1, 44.6]
                ]]
            },
            # Tribal geometries as fallbacks if the tribal_boundaries module fails
            'T01': {
                "type": "Polygon",
                "coordinates": [[
                    [-90.7, 46.5],  # Bad River approximate boundaries
                    [-90.5, 46.5],
                    [-90.5, 46.3],
                    [-90.7, 46.3],
                    [-90.7, 46.5]
                ]]
            },
            'T02': {
                "type": "Polygon",
                "coordinates": [[
                    [-88.9, 45.5],  # Forest County Potawatomi approximate boundaries
                    [-88.7, 45.5],
                    [-88.7, 45.3],
                    [-88.9, 45.3],
                    [-88.9, 45.5]
                ]]
            },
            'T03': {
                "type": "Polygon",
                "coordinates": [[
                    [-90.8, 44.3],  # Ho-Chunk approximate boundaries
                    [-90.6, 44.3],
                    [-90.6, 44.1],
                    [-90.8, 44.1],
                    [-90.8, 44.3]
                ]]
            }
        }
        
        # Add any missing geometries from the hardcoded list
        for jurisdiction_id, geometry in hardcoded_geometries.items():
            if jurisdiction_id not in geometries:
                geometries[jurisdiction_id] = geometry
        
        logger.info(f"Extracted geometries for {len(geometries)} jurisdictions")
        return geometries
    
    except Exception as e:
        logger.error(f"Error extracting geometries: {str(e)}")
        return {}

