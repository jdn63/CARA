"""Module for calculating utilities-related risk scores"""
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from utils.svi_data import get_svi_data
from utils.risk_calculation import calculate_residual_risk
from utils.eagle_i_outages import get_outage_metrics

# Get module logger (centralized config in core.py)
logger = logging.getLogger(__name__)

# Constants for API endpoints and data sources
DOE_DISTURBANCE_URL = "https://www.oe.netl.doe.gov/download.aspx?type=OE417"
PSC_OUTAGE_URL = "https://psc.wi.gov/Pages/ServiceType/Electric.aspx"
EPA_WATER_URL = "https://www.epa.gov/enviro/sdwis-search"
FCC_COMMS_URL = "https://www.fcc.gov/disaster-information-reporting-system-dirs-0"

# FEMA's Community Lifelines categories relevant to utilities
UTILITY_LIFELINES = [
    "Power",
    "Water",
    "Communications",
    "Transportation",
    "Hazardous Materials"
]

# Mapping of Wisconsin counties to predominant electric utilities
COUNTY_UTILITY_MAP = {
    "Milwaukee": ["WE Energies"],
    "Dane": ["Madison Gas and Electric", "Alliant Energy"],
    "Waukesha": ["WE Energies"],
    "Brown": ["Wisconsin Public Service"],
    "Racine": ["WE Energies"],
    "Outagamie": ["WE Energies", "Wisconsin Public Service"],
    "Kenosha": ["WE Energies"],
    "Washington": ["WE Energies"],
    "Winnebago": ["Wisconsin Public Service", "Alliant Energy"],
    "Rock": ["Alliant Energy"],
    # Additional counties would be added here
}

# NOTE (2026-07 data-source integrity audit): a previous version carried a
# COUNTY_WATER_SYSTEM_MAP with per-county water-system counts that were not
# drawn from any real inventory (EPA SDWIS was cited but never fetched).
# The map has been removed; private-well reliance is now an urban/rural
# heuristic, disclosed as such in the data_sources labels below.

def calculate_electrical_outage_risk(county_name: str) -> Dict:
    """
    Calculate multi-dimensional electrical outage risk based on three components:
    1. Exposure: Historical outage frequency, seasonal patterns, grid vulnerability
    2. Vulnerability: Population and infrastructure dependency on electrical power
    3. Resilience: Backup systems, restoration capacity, alternative power options
    
    Args:
        county_name: The name of the Wisconsin county
        
    Returns:
        Dictionary with component scores and an overall risk score
    """
    logger.info(f"Calculating electrical outage risk for {county_name}")
    
    # Get SVI data to incorporate into vulnerability calculations
    try:
        svi_data = get_svi_data(county_name)
        socioeconomic_svi = svi_data.get("socioeconomic", 0.5)
        housing_svi = svi_data.get("housing_transportation", 0.5)
    except Exception as e:
        logger.warning(f"Unable to get SVI data: {e}. Using default values.")
        socioeconomic_svi = 0.5
        housing_svi = 0.5
    
    # Exposure: prefer real DOE/ORNL EAGLE-I recorded outage history
    # (seed artifact built by scripts/build_eagle_i_seed.py); fall back
    # to the disclosed rule-based proxy only if the seed is missing.
    eagle_metrics = get_outage_metrics(county_name)
    if eagle_metrics and eagle_metrics.get("exposure_score") is not None:
        exposure_score = eagle_metrics["exposure_score"]
        exposure_source = "eagle_i"
    else:
        exposure_score = _calculate_electrical_exposure(county_name)
        exposure_source = "proxy_fallback"
        logger.warning(
            "EAGLE-I outage data missing for %s; using proxy exposure",
            county_name)
    
    # Calculate vulnerability component (incorporating SVI data)
    vulnerability_score = _calculate_electrical_vulnerability(county_name, socioeconomic_svi, housing_svi)
    
    # Calculate resilience component
    resilience_score = _calculate_electrical_resilience(county_name)
    
    # Calculate traditional weighted risk score (for comparison/backward compatibility)
    traditional_risk = (0.4 * exposure_score + 0.4 * vulnerability_score - 0.2 * resilience_score + 1) / 2
    
    # Ensure the traditional risk is between 0 and 1
    traditional_risk = max(0, min(1, traditional_risk))
    
    # Calculate the new residual risk using our formula
    # For electrical outage risk:
    # - exposure_score represents exposure (likelihood of outages)
    # - vulnerability_score represents vulnerability (impact on community)
    # - resilience_score represents resilience (higher = better response capacity)
    # Note: resilience_score is already using the correct scale (higher = better)
    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_score
    )
    
    if exposure_source == "eagle_i":
        data_sources = [
            "DOE/ORNL EAGLE-I recorded electricity outages 2014-2025 "
            "(county level, 15-minute resolution; exposure component)",
            "CARA rule-based county proxy model (vulnerability and "
            "resilience components)",
            "CDC Social Vulnerability Index (vulnerability component)"
        ]
    else:
        data_sources = [
            "CARA rule-based county proxy model (urban/rural grid heuristics; EAGLE-I seed unavailable)",
            "CDC Social Vulnerability Index (vulnerability component)"
        ]

    result = {
        "overall_risk": residual_risk,  # Use the new residual risk as overall score
        "traditional_risk": traditional_risk,  # Keep the old calculation for reference
        "components": {
            "exposure": exposure_score,
            "vulnerability": vulnerability_score,
            "resilience": resilience_score
        },
        "exposure_source": exposure_source,
        "data_sources": data_sources
    }
    if eagle_metrics:
        result["outage_history"] = {
            "hours_per_customer_per_year": eagle_metrics.get(
                "hours_per_customer_per_year"),
            "customer_hours_out_per_year": eagle_metrics.get(
                "customer_hours_out_per_year"),
            "peak_customers_out": eagle_metrics.get("peak_customers_out"),
            "modeled_customers": eagle_metrics.get("modeled_customers"),
        }
    return result

def _calculate_electrical_exposure(county_name: str) -> float:
    """
    Calculate exposure component of electrical outage risk.
    
    Factors:
    - Historical outage frequency
    - Seasonal patterns (higher risk during severe weather seasons)
    - Grid infrastructure age and condition
    - Geographic factors (rural areas typically higher risk)
    
    Returns:
        Exposure score between 0-1
    """
    # Determine primary utility providers for this county
    utility_providers = COUNTY_UTILITY_MAP.get(county_name, ["Unknown"])
    
    # Check historical outage data for these providers
    # Note: In a production environment, this would connect to actual outage databases
    
    # Base exposure factors from known Wisconsin patterns
    base_factors = {
        # Rural counties generally have higher exposure due to longer lines,
        # fewer redundancies, and more exposure to weather
        "urban_rural_factor": 0.7 if county_name in ["Milwaukee", "Dane", "Waukesha", "Brown"] else 0.9,
        
        # Grid age factor - older infrastructure in certain counties
        "grid_age_factor": 0.8 if county_name in ["Milwaukee", "Racine", "Kenosha"] else 0.6,
        
        # Weather exposure - some counties more prone to weather impacts
        "weather_exposure": 0.8 if county_name in ["Bayfield", "Ashland", "Douglas"] else 0.6
    }
    
    # Calculate composite exposure score
    exposure_score = (
        0.4 * base_factors["urban_rural_factor"] +
        0.3 * base_factors["grid_age_factor"] +
        0.3 * base_factors["weather_exposure"]
    )
    
    return exposure_score

def _calculate_electrical_vulnerability(county_name: str, socioeconomic_svi: float, housing_svi: float) -> float:
    """
    Calculate vulnerability component of electrical outage risk.
    
    Factors:
    - Population density and distribution
    - Critical infrastructure dependency (hospitals, water systems)
    - Economic factors (business dependency)
    - Socioeconomic vulnerability (from SVI)
    
    Returns:
        Vulnerability score between 0-1
    """
    # Base vulnerability factors
    base_factors = {
        # Critical infrastructure dependency - higher in urban/industrial counties
        "critical_infrastructure": 0.9 if county_name in ["Milwaukee", "Dane", "Brown"] else 0.6,
        
        # Medical dependency - counties with more healthcare facilities
        "medical_dependency": 0.8 if county_name in ["Milwaukee", "Dane", "La Crosse"] else 0.5,
        
        # Population density - higher density means more people affected
        "population_density": 0.9 if county_name in ["Milwaukee", "Waukesha", "Dane"] else 0.6
    }
    
    # Calculate composite vulnerability score, incorporating SVI data
    # SVI data significantly impacts vulnerability - those with fewer resources are more vulnerable
    vulnerability_score = (
        0.3 * base_factors["critical_infrastructure"] +
        0.2 * base_factors["medical_dependency"] +
        0.2 * base_factors["population_density"] +
        0.3 * ((socioeconomic_svi + housing_svi) / 2)  # SVI components most relevant to power outages
    )
    
    return vulnerability_score

def _calculate_electrical_resilience(county_name: str) -> float:
    """
    Calculate resilience component of electrical outage risk.
    
    Factors:
    - Backup power prevalence (generators, alternative sources)
    - Utility restoration capacity
    - Community emergency plans
    - Mutual aid agreements
    
    Returns:
        Resilience score between 0-1
    """
    # Base resilience factors - higher scores mean BETTER resilience (lower risk)
    base_factors = {
        # Urban areas typically have better restoration times
        "restoration_capacity": 0.8 if county_name in ["Milwaukee", "Dane", "Waukesha"] else 0.6,
        
        # Some counties have more developed emergency plans
        "emergency_plans": 0.7 if county_name in ["Milwaukee", "Dane", "Brown", "La Crosse"] else 0.5,
        
        # Backup power systems more common in some areas
        "backup_systems": 0.7 if county_name in ["Milwaukee", "Waukesha", "Dane"] else 0.5,
        
        # Community resources to respond to outages
        "community_resources": 0.8 if county_name in ["Dane", "Milwaukee", "Brown"] else 0.6
    }
    
    # Calculate composite resilience score
    resilience_score = (
        0.3 * base_factors["restoration_capacity"] +
        0.2 * base_factors["emergency_plans"] +
        0.3 * base_factors["backup_systems"] +
        0.2 * base_factors["community_resources"]
    )
    
    return resilience_score

def calculate_utilities_disruption_risk(county_name: str) -> Dict:
    """
    Calculate multi-dimensional utilities disruption risk based on three components,
    focusing on water, sewer, and communications systems.
    
    1. Exposure: System age, breakdown frequency, geographic vulnerabilities
    2. Vulnerability: Population dependency, critical services reliance
    3. Resilience: Backup systems, emergency response capacity
    
    Args:
        county_name: The name of the Wisconsin county
        
    Returns:
        Dictionary with component scores and an overall risk score
    """
    logger.info(f"Calculating utilities disruption risk for {county_name}")
    
    # Get SVI data to incorporate into vulnerability calculations
    try:
        svi_data = get_svi_data(county_name)
        socioeconomic_svi = svi_data.get("socioeconomic", 0.5)
        housing_svi = svi_data.get("housing_transportation", 0.5)
    except Exception as e:
        logger.warning(f"Unable to get SVI data: {e}. Using default values.")
        socioeconomic_svi = 0.5
        housing_svi = 0.5
    
    # Calculate exposure component
    exposure_score = _calculate_utilities_exposure(county_name)
    
    # Calculate vulnerability component (incorporating SVI data)
    vulnerability_score = _calculate_utilities_vulnerability(county_name, socioeconomic_svi, housing_svi)
    
    # Calculate resilience component
    resilience_score = _calculate_utilities_resilience(county_name)
    
    # Calculate traditional weighted risk score (for comparison/backward compatibility)
    traditional_risk = (0.4 * exposure_score + 0.4 * vulnerability_score - 0.2 * resilience_score + 1) / 2
    
    # Ensure the traditional risk is between 0 and 1
    traditional_risk = max(0, min(1, traditional_risk))
    
    # Calculate the new residual risk using our formula
    # For utilities disruption risk:
    # - exposure_score represents exposure (likelihood of disruption)
    # - vulnerability_score represents vulnerability (impact on community)
    # - resilience_score represents resilience (higher = better response capacity)
    # Note: resilience_score is already using the correct scale (higher = better)
    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_score
    )
    
    from utils.sdwis_water import get_water_system_metrics
    sdwis = get_water_system_metrics(county_name)
    if sdwis and sdwis.get("private_well_reliance") is not None:
        data_sources = [
            "EPA SDWIS public water systems (active system counts and "
            "population served; private-well reliance estimate)",
            "CARA rule-based county proxy model (communications and "
            "infrastructure-age heuristics)",
            "CDC Social Vulnerability Index (vulnerability component)"
        ]
        water_data_source = "epa_sdwis"
    else:
        data_sources = [
            "CARA rule-based county proxy model (water/communications heuristics; SDWIS cache not yet warmed)",
            "CDC Social Vulnerability Index (vulnerability component)"
        ]
        water_data_source = "proxy_fallback"

    result = {
        "overall_risk": residual_risk,  # Use the new residual risk as overall score
        "traditional_risk": traditional_risk,  # Keep the old calculation for reference
        "components": {
            "exposure": exposure_score,
            "vulnerability": vulnerability_score,
            "resilience": resilience_score
        },
        "water_data_source": water_data_source,
        "data_sources": data_sources
    }
    if sdwis:
        result["water_systems"] = {
            "active_systems_total": sdwis.get("active_systems_total"),
            "cws_count": sdwis.get("cws_count"),
            "cws_population_served": sdwis.get("cws_population_served"),
            "private_well_reliance": sdwis.get("private_well_reliance"),
        }
    return result

def _comms_vulnerability(county_name: str) -> float:
    """
    Communications vulnerability input for utilities exposure. Prefers
    the real ACS broadband subscription percentile (warmed by the
    scheduler job refresh_all_acs_broadband); falls back to the
    disclosed urban/rural rule when the cache is empty.
    """
    from utils.acs_broadband import get_broadband_metrics
    bb = get_broadband_metrics(county_name)
    if bb and bb.get("comms_vulnerability") is not None:
        return bb["comms_vulnerability"]
    return 0.8 if county_name not in ["Milwaukee", "Dane", "Waukesha", "Brown"] else 0.5

def _calculate_utilities_exposure(county_name: str) -> float:
    """
    Calculate exposure component of utilities disruption risk.
    
    Factors:
    - Water/sewer system age and condition
    - Communications infrastructure reliability
    - Historical disruption patterns
    - Geographic vulnerabilities (flooding, soil conditions)
    
    Returns:
        Exposure score between 0-1
    """
    # Private-well reliance: prefer the real EPA SDWIS-derived estimate
    # (1 - CWS population served / county population, warmed by the
    # scheduler job refresh_all_epa_sdwis). Fall back to the disclosed
    # urban/rural rule only when the cache has no entry.
    from utils.sdwis_water import get_water_system_metrics
    sdwis = get_water_system_metrics(county_name)
    if sdwis and sdwis.get("private_well_reliance") is not None:
        private_well_reliance = sdwis["private_well_reliance"]
    elif county_name in ["Milwaukee", "Racine", "Kenosha"]:
        private_well_reliance = 0.4
    elif county_name in ["Dane", "Waukesha", "Brown"]:
        private_well_reliance = 0.5
    else:
        private_well_reliance = 0.6
    
    # Base exposure factors from known Wisconsin patterns
    base_factors = {
        # Water infrastructure age - older in established urban counties
        "water_infrastructure_age": 0.8 if county_name in ["Milwaukee", "Racine", "Kenosha"] else 0.6,
        
        # Communications vulnerability - real ACS broadband subscription
        # share when cached, otherwise the disclosed urban/rural rule
        "comms_vulnerability": _comms_vulnerability(county_name),
        
        # Geographic risk factors (flooding impact on utilities)
        "geographic_vulnerability": 0.7 if county_name in ["Crawford", "Vernon", "La Crosse"] else 0.5,
        
        # System complexity - more complex systems have more failure points
        "system_complexity": 0.7 if county_name in ["Milwaukee", "Dane", "Brown"] else 0.5
    }
    
    # Systems with more private wells have higher exposure (less regulation/monitoring)
    private_systems_factor = private_well_reliance
    
    # Calculate composite exposure score
    exposure_score = (
        0.3 * base_factors["water_infrastructure_age"] +
        0.2 * base_factors["comms_vulnerability"] +
        0.2 * base_factors["geographic_vulnerability"] +
        0.1 * base_factors["system_complexity"] +
        0.2 * private_systems_factor
    )
    
    return exposure_score

def _calculate_utilities_vulnerability(county_name: str, socioeconomic_svi: float, housing_svi: float) -> float:
    """
    Calculate vulnerability component of utilities disruption risk.
    
    Factors:
    - Population dependency on municipal systems
    - Critical services reliance (hospitals, emergency services)
    - Socioeconomic vulnerability (from SVI)
    - Alternative access options
    
    Returns:
        Vulnerability score between 0-1
    """
    # Base vulnerability factors
    base_factors = {
        # Population dependency - higher in urban areas
        "population_dependency": 0.9 if county_name in ["Milwaukee", "Dane", "Waukesha"] else 0.6,
        
        # Critical services dependency
        "critical_services": 0.8 if county_name in ["Milwaukee", "Dane", "La Crosse", "Brown"] else 0.6,
        
        # Alternative access - fewer options in some areas
        "alternative_access": 0.7 if county_name not in ["Milwaukee", "Dane", "Waukesha"] else 0.4
    }
    
    # Calculate composite vulnerability score, incorporating SVI data
    # SVI significantly impacts utility vulnerability - housing quality and economic resources
    # directly affect ability to manage during disruptions
    vulnerability_score = (
        0.3 * base_factors["population_dependency"] +
        0.2 * base_factors["critical_services"] +
        0.2 * base_factors["alternative_access"] +
        0.3 * ((socioeconomic_svi + housing_svi) / 2)  # SVI components most relevant to utilities
    )
    
    return vulnerability_score

def _calculate_utilities_resilience(county_name: str) -> float:
    """
    Calculate resilience component of utilities disruption risk.
    
    Factors:
    - Emergency response plans
    - Backup systems availability
    - Restoration capacity
    - Mutual aid agreements
    
    Returns:
        Resilience score between 0-1
    """
    # Base resilience factors - higher scores mean BETTER resilience (lower risk)
    base_factors = {
        # Emergency response capabilities
        "emergency_response": 0.8 if county_name in ["Milwaukee", "Dane", "Brown"] else 0.6,
        
        # Restoration capacity - faster in urban areas
        "restoration_capacity": 0.7 if county_name in ["Milwaukee", "Dane", "Waukesha", "Brown"] else 0.5,
        
        # Backup systems - more prevalent in some counties
        "backup_systems": 0.7 if county_name in ["Milwaukee", "Waukesha", "Dane"] else 0.5,
        
        # Regional cooperation and mutual aid
        "regional_cooperation": 0.8 if county_name in ["Dane", "Milwaukee", "Brown", "Waukesha"] else 0.6
    }
    
    # Calculate composite resilience score
    resilience_score = (
        0.3 * base_factors["emergency_response"] +
        0.3 * base_factors["restoration_capacity"] +
        0.2 * base_factors["backup_systems"] +
        0.2 * base_factors["regional_cooperation"]
    )
    
    return resilience_score

def calculate_supply_chain_risk(county_name: str) -> Dict:
    """
    Calculate multi-dimensional supply chain disruption risk based on three components:
    1. Exposure: Transportation network vulnerability, supplier concentration
    2. Vulnerability: Critical supply dependency, population needs
    3. Resilience: Alternative suppliers, stockpiles, emergency plans
    
    Args:
        county_name: The name of the Wisconsin county
        
    Returns:
        Dictionary with component scores and an overall risk score
    """
    logger.info(f"Calculating supply chain disruption risk for {county_name}")
    
    # Get SVI data to incorporate into vulnerability calculations
    try:
        svi_data = get_svi_data(county_name)
        socioeconomic_svi = svi_data.get("socioeconomic", 0.5)
    except Exception as e:
        logger.warning(f"Unable to get SVI data: {e}. Using default values.")
        socioeconomic_svi = 0.5
    
    # Calculate exposure component
    exposure_score = _calculate_supply_chain_exposure(county_name)
    
    # Calculate vulnerability component (incorporating SVI data)
    vulnerability_score = _calculate_supply_chain_vulnerability(county_name, socioeconomic_svi)
    
    # Calculate resilience component
    resilience_score = _calculate_supply_chain_resilience(county_name)
    
    # Calculate traditional weighted risk score (for comparison/backward compatibility)
    traditional_risk = (0.4 * exposure_score + 0.4 * vulnerability_score - 0.2 * resilience_score + 1) / 2
    
    # Ensure the traditional risk is between 0 and 1
    traditional_risk = max(0, min(1, traditional_risk))
    
    # Calculate the new residual risk using our formula
    # For supply chain risk:
    # - exposure_score represents exposure (likelihood of supply chain disruptions)
    # - vulnerability_score represents vulnerability (impact on community)
    # - resilience_score represents resilience (higher = better response capacity)
    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_score
    )
    
    return {
        "overall_risk": residual_risk,  # Use the new residual risk as overall score
        "traditional_risk": traditional_risk,  # Keep the old calculation for reference
        "components": {
            "exposure": exposure_score,
            "vulnerability": vulnerability_score,
            "resilience": resilience_score
        },
        "data_sources": [
            "CARA rule-based county proxy model (transportation/retail heuristics; no live infrastructure feed)",
            "CDC Social Vulnerability Index (vulnerability component)"
        ]
    }

def _calculate_supply_chain_exposure(county_name: str) -> float:
    """
    Calculate exposure component of supply chain disruption risk.
    
    Factors:
    - Transportation network redundancy
    - Geographic isolation factors
    - Supplier concentration
    - Historical disruption patterns
    
    Returns:
        Exposure score between 0-1
    """
    # Base exposure factors from known Wisconsin patterns
    base_factors = {
        # Transportation network - more isolated counties have higher exposure
        "transportation_isolation": 0.8 if county_name not in ["Milwaukee", "Dane", "Waukesha", "Brown", "Racine"] else 0.5,
        
        # Route redundancy - fewer alternative routes means higher exposure
        "route_redundancy": 0.7 if county_name not in ["Milwaukee", "Dane", "Waukesha", "Brown"] else 0.4,
        
        # Supplier concentration - less diversity means higher exposure
        "supplier_concentration": 0.6 if county_name in ["Milwaukee", "Dane", "Brown"] else 0.8,
        
        # Weather impacts on transportation - northern counties face more challenges
        "weather_vulnerability": 0.8 if county_name in ["Bayfield", "Douglas", "Ashland", "Iron"] else 0.6
    }
    
    # Calculate composite exposure score
    exposure_score = (
        0.3 * base_factors["transportation_isolation"] +
        0.3 * base_factors["route_redundancy"] +
        0.2 * base_factors["supplier_concentration"] +
        0.2 * base_factors["weather_vulnerability"]
    )
    
    return exposure_score

def _calculate_supply_chain_vulnerability(county_name: str, socioeconomic_svi: float) -> float:
    """
    Calculate vulnerability component of supply chain disruption risk.
    
    Factors:
    - Population dependency on external supplies
    - Critical supply needs (medical, food)
    - Socioeconomic vulnerability
    - Business dependency
    
    Returns:
        Vulnerability score between 0-1
    """
    # Base vulnerability factors
    base_factors = {
        # Population dependency on external supplies - varies by county
        "population_dependency": 0.8 if county_name in ["Milwaukee", "Dane"] else 0.6,
        
        # Critical supply needs - healthcare, specialized facilities
        "critical_needs": 0.8 if county_name in ["Milwaukee", "Dane", "La Crosse", "Brown"] else 0.6,
        
        # Business dependency on supply chains
        "business_dependency": 0.7 if county_name in ["Milwaukee", "Waukesha", "Brown"] else 0.5,
        
        # Food access vulnerability - food deserts in some areas
        "food_access": 0.7 if county_name in ["Milwaukee", "Racine", "Kenosha"] else 0.5
    }
    
    # Calculate composite vulnerability score, incorporating SVI data
    # Socioeconomic status directly impacts ability to prepare for supply disruptions
    vulnerability_score = (
        0.25 * base_factors["population_dependency"] +
        0.25 * base_factors["critical_needs"] +
        0.2 * base_factors["business_dependency"] +
        0.1 * base_factors["food_access"] +
        0.2 * socioeconomic_svi  # SVI component most relevant to supply chain vulnerability
    )
    
    return vulnerability_score

def _calculate_supply_chain_resilience(county_name: str) -> float:
    """
    Calculate resilience component of supply chain disruption risk.
    
    Factors:
    - Alternative supplier options
    - Local production capacity
    - Emergency stockpiles
    - Community resource sharing capacity
    
    Returns:
        Resilience score between 0-1
    """
    # Base resilience factors - higher scores mean BETTER resilience (lower risk)
    base_factors = {
        # Alternative supplier access - better in urban areas
        "alternative_suppliers": 0.8 if county_name in ["Milwaukee", "Dane", "Brown"] else 0.5,
        
        # Local production capacity - agricultural counties have advantages
        "local_production": 0.8 if county_name in ["Dane", "Marathon", "Fond du Lac"] else 0.5,
        
        # Emergency stockpiles and preparations
        "emergency_stockpiles": 0.7 if county_name in ["Milwaukee", "Dane", "Brown"] else 0.5,
        
        # Community resource sharing networks
        "community_networks": 0.7 if county_name in ["Dane", "La Crosse", "Eau Claire"] else 0.5
    }
    
    # Calculate composite resilience score
    resilience_score = (
        0.3 * base_factors["alternative_suppliers"] +
        0.3 * base_factors["local_production"] +
        0.2 * base_factors["emergency_stockpiles"] +
        0.2 * base_factors["community_networks"]
    )
    
    return resilience_score

def calculate_fuel_shortage_risk(county_name: str) -> Dict:
    """
    Calculate multi-dimensional fuel shortage risk based on three components:
    1. Exposure: Fuel distribution network vulnerability, historical patterns
    2. Vulnerability: Population and services dependency on fuel
    3. Resilience: Alternative fuel options, emergency reserves
    
    Args:
        county_name: The name of the Wisconsin county
        
    Returns:
        Dictionary with component scores and an overall risk score
    """
    logger.info(f"Calculating fuel shortage risk for {county_name}")
    
    # Get SVI data to incorporate into vulnerability calculations
    try:
        svi_data = get_svi_data(county_name)
        socioeconomic_svi = svi_data.get("socioeconomic", 0.5)
        housing_svi = svi_data.get("housing_transportation", 0.5)
    except Exception as e:
        logger.warning(f"Unable to get SVI data: {e}. Using default values.")
        socioeconomic_svi = 0.5
        housing_svi = 0.5
    
    # Calculate exposure component
    exposure_score = _calculate_fuel_shortage_exposure(county_name)
    
    # Calculate vulnerability component (incorporating SVI data)
    vulnerability_score = _calculate_fuel_shortage_vulnerability(county_name, socioeconomic_svi, housing_svi)
    
    # Calculate resilience component
    resilience_score = _calculate_fuel_shortage_resilience(county_name)
    
    # Calculate traditional weighted risk score (for comparison/backward compatibility)
    traditional_risk = (0.4 * exposure_score + 0.4 * vulnerability_score - 0.2 * resilience_score + 1) / 2
    
    # Ensure the traditional risk is between 0 and 1
    traditional_risk = max(0, min(1, traditional_risk))
    
    # Calculate the new residual risk using our formula
    # For fuel shortage risk:
    # - exposure_score represents exposure (likelihood of fuel supply disruptions)
    # - vulnerability_score represents vulnerability (impact on community)
    # - resilience_score represents resilience (higher = better response capacity)
    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_score
    )
    
    from utils.census_cbp_fuel import get_fuel_station_metrics
    cbp = get_fuel_station_metrics(county_name)
    if cbp and cbp.get("fuel_access_exposure") is not None:
        fuel_data_source = "census_cbp"
        fuel_data_sources = [
            "Census County Business Patterns (gasoline station density, "
            "NAICS 447)",
            "CARA rule-based county proxy model (pipeline and storage "
            "heuristics)",
            "CDC Social Vulnerability Index (vulnerability component)"
        ]
    else:
        fuel_data_source = "proxy_fallback"
        fuel_data_sources = [
            "CARA rule-based county proxy model (fuel distribution heuristics; CBP cache not yet warmed)",
            "CDC Social Vulnerability Index (vulnerability component)"
        ]

    result = {
        "overall_risk": residual_risk,  # Use the new residual risk as overall score
        "traditional_risk": traditional_risk,  # Keep the old calculation for reference
        "components": {
            "exposure": exposure_score,
            "vulnerability": vulnerability_score,
            "resilience": resilience_score
        },
        "fuel_data_source": fuel_data_source,
        "data_sources": fuel_data_sources
    }
    if cbp:
        result["fuel_stations"] = {
            "gas_stations": cbp.get("gas_stations"),
            "stations_per_10k": cbp.get("stations_per_10k"),
            "cbp_year": cbp.get("cbp_year"),
        }
    return result

def _calculate_fuel_shortage_exposure(county_name: str) -> float:
    """
    Calculate exposure component of fuel shortage risk.
    
    Factors:
    - Distance from fuel distribution centers
    - Pipeline access
    - Historical fuel supply disruptions
    - Transportation network vulnerability
    
    Returns:
        Exposure score between 0-1
    """
    # Distribution isolation: prefer the real Census CBP gas-station
    # density metric (NAICS 447 establishments per 10,000 residents,
    # warmed by the scheduler job refresh_all_census_cbp_fuel). Fall
    # back to the disclosed urban/rural rule when the cache is empty.
    from utils.census_cbp_fuel import get_fuel_station_metrics
    cbp = get_fuel_station_metrics(county_name)
    if cbp and cbp.get("fuel_access_exposure") is not None:
        distribution_isolation = cbp["fuel_access_exposure"]
    else:
        distribution_isolation = 0.8 if county_name not in ["Milwaukee", "Dane", "Waukesha", "Brown", "Racine"] else 0.4

    # Base exposure factors from known Wisconsin patterns
    base_factors = {
        # Distribution network access - more isolated counties have higher exposure
        "distribution_isolation": distribution_isolation,
        
        # Pipeline proximity - counties without direct pipeline access are more vulnerable
        "pipeline_access": 0.6 if county_name in ["Milwaukee", "Dane", "Rock", "Brown"] else 0.8,
        
        # Weather impacts on fuel delivery - northern counties face more challenges
        "weather_vulnerability": 0.8 if county_name in ["Bayfield", "Douglas", "Ashland", "Iron"] else 0.5,
        
        # Storage capacity - limited in some areas
        "storage_capacity": 0.7 if county_name not in ["Milwaukee", "Dane", "Brown"] else 0.4
    }
    
    # Calculate composite exposure score
    exposure_score = (
        0.3 * base_factors["distribution_isolation"] +
        0.3 * base_factors["pipeline_access"] +
        0.2 * base_factors["weather_vulnerability"] +
        0.2 * base_factors["storage_capacity"]
    )
    
    return exposure_score

def _calculate_fuel_shortage_vulnerability(county_name: str, socioeconomic_svi: float, housing_svi: float) -> float:
    """
    Calculate vulnerability component of fuel shortage risk.
    
    Factors:
    - Population car dependency
    - Critical services fuel needs (emergency, healthcare)
    - Socioeconomic vulnerability
    - Heating fuel dependency (especially in winter)
    
    Returns:
        Vulnerability score between 0-1
    """
    # Base vulnerability factors
    base_factors = {
        # Car dependency - rural areas more dependent on private vehicles
        "car_dependency": 0.6 if county_name in ["Milwaukee", "Dane"] else 0.9,
        
        # Critical services fuel needs
        "critical_services": 0.7 if county_name in ["Milwaukee", "Dane", "La Crosse", "Brown"] else 0.6,
        
        # Heating fuel dependency - varies by county and availability of alternatives
        "heating_dependency": 0.8 if county_name in ["Bayfield", "Douglas", "Ashland", "Iron", "Vilas"] else 0.6,
        
        # Agricultural dependency
        "agricultural_dependency": 0.8 if county_name in ["Dane", "Marathon", "Fond du Lac", "Dodge"] else 0.4
    }
    
    # Calculate composite vulnerability score, incorporating SVI data
    # Both socioeconomic status and housing/transportation directly impact fuel vulnerability
    vulnerability_score = (
        0.25 * base_factors["car_dependency"] +
        0.2 * base_factors["critical_services"] +
        0.2 * base_factors["heating_dependency"] +
        0.15 * base_factors["agricultural_dependency"] +
        0.2 * ((socioeconomic_svi + housing_svi) / 2)  # SVI components most relevant to fuel vulnerability
    )
    
    return vulnerability_score

def _calculate_fuel_shortage_resilience(county_name: str) -> float:
    """
    Calculate resilience component of fuel shortage risk.
    
    Factors:
    - Alternative transportation options
    - Alternative heating options
    - Emergency fuel reserves
    - Energy flexibility
    
    Returns:
        Resilience score between 0-1
    """
    # Base resilience factors - higher scores mean BETTER resilience (lower risk)
    base_factors = {
        # Alternative transportation - better in urban areas
        "alternative_transportation": 0.8 if county_name in ["Milwaukee", "Dane"] else 0.4,
        
        # Alternative heating options
        "alternative_heating": 0.7 if county_name in ["Dane", "Marathon", "Fond du Lac"] else 0.5,
        
        # Emergency reserves and planning
        "emergency_reserves": 0.7 if county_name in ["Milwaukee", "Dane", "Brown"] else 0.5,
        
        # Community support networks
        "community_networks": 0.8 if county_name in ["Dane", "La Crosse", "Eau Claire"] else 0.6
    }
    
    # Calculate composite resilience score
    resilience_score = (
        0.3 * base_factors["alternative_transportation"] +
        0.3 * base_factors["alternative_heating"] +
        0.2 * base_factors["emergency_reserves"] +
        0.2 * base_factors["community_networks"]
    )
    
    return resilience_score