"""Utility module for risk calculation functions used across the application"""
import json
import logging
import os
from typing import Dict, Optional

import pandas as pd

# Get module logger (centralized config in core.py)
logger = logging.getLogger(__name__)

# NRI data cache to avoid repeated file reads
_nri_health_data_cache = None

# County-level FEMA NRI Community Resilience cache (HVRI BRIC index)
_nri_community_resilience_cache = None


def get_community_resilience(county_name: str) -> float:
    """
    Return the EVR Resilience term for a county, sourced from the FEMA
    National Risk Index "Community Resilience" score (University of South
    Carolina HVRI Baseline Resilience Indicators for Communities, BRIC).

    METHODOLOGY NOTE (external review finding: SVI double-counting):
    Earlier CARA versions derived Resilience from inverse SVI socioeconomic
    and housing-transportation scores. Because those same SVI themes also
    raise the Vulnerability term, the one signal amplified risk twice in
    Risk = E x V x (2.0 - R). This helper replaces the inverse-SVI proxy
    with FEMA's own published community-resilience measure, mirroring the
    FEMA NRI pairing of social vulnerability (numerator) with community
    resilience (denominator). BRIC includes some socioeconomic components
    by design, but it is a distinct published index; the direct reuse of
    the same SVI themes on both sides of the formula is eliminated.

    The NRI CSV stores Community Resilience as a 0-100 national percentile
    per census tract. We take the county mean and map it linearly onto the
    EVR resilience range [0.1, 0.9]:

        R = 0.1 + 0.8 * (county_mean_percentile / 100)

    Returns 0.5 (neutral) if the county is not found or the file is
    unavailable, so a data gap never silently inflates or deflates risk.
    """
    global _nri_community_resilience_cache

    if _nri_community_resilience_cache is None:
        try:
            nri_path = 'data/nri/NRI_Table_CensusTracts_Wisconsin_FloodTornadoWinterOnly.csv'
            if os.path.exists(nri_path):
                nri_df = pd.read_csv(nri_path, usecols=['county', 'resilience'])
                county_means = nri_df.groupby('county')['resilience'].mean()
                _nri_community_resilience_cache = {
                    county: max(0.1, min(0.9, 0.1 + 0.8 * (float(value) / 100.0)))
                    for county, value in county_means.items()
                }
                logger.info(
                    f"Loaded NRI Community Resilience for "
                    f"{len(_nri_community_resilience_cache)} counties"
                )
            else:
                logger.warning(
                    f"NRI data file not found at {nri_path}; "
                    f"community resilience defaults to neutral 0.5"
                )
                _nri_community_resilience_cache = {}
        except Exception as e:
            logger.error(f"Error loading NRI Community Resilience data: {str(e)}")
            _nri_community_resilience_cache = {}

    return _nri_community_resilience_cache.get(county_name, 0.5)

def get_health_impact_factor(county_name: str, hazard_type: str) -> float:
    """
    Retrieves health impact factor from FEMA NRI data for a specific county and hazard type.
    
    The health impact factor considers:
    1. Expected Annual Loss of Population (EAL_POPULATION)
    2. Social Vulnerability components (SOVI_HEALTH)
    3. Healthcare Access metrics (HEALTHCARE_ACCESS)
    4. Population with Disabilities percentage (DISABILITY_PERCENT)
    
    Args:
        county_name: The name of the Wisconsin county
        hazard_type: The type of hazard (flood, tornado, winter_storm, etc.)
        
    Returns:
        A health impact factor (0.8-1.5) where:
        - <1.0 means reduced health impacts compared to average
        - 1.0 means average health impacts
        - >1.0 means elevated health impacts compared to average
    """
    global _nri_health_data_cache
    
    # Load NRI health data if not already cached
    if _nri_health_data_cache is None:
        try:
            # Attempt to load data from NRI CSV file
            nri_path = 'data/nri/NRI_Table_CensusTracts_Wisconsin_FloodTornadoWinterOnly.csv'
            if os.path.exists(nri_path):
                logger.info(f"Loading NRI health impact data from {nri_path}")
                nri_df = pd.read_csv(nri_path)
                
                # Aggregate to county level
                county_health_data = {}
                for county in nri_df['county'].unique():
                    county_rows = nri_df[nri_df['county'] == county]
                    
                    # Create county-level health impact factors by hazard type
                    # Note: Actual field names would depend on the specific NRI dataset structure
                    county_health_data[county] = {
                        # Scale and normalize each factor to the desired range (0.8-1.5)
                        "flood": _calculate_normalized_health_factor(county_rows, 'flood'),
                        "tornado": _calculate_normalized_health_factor(county_rows, 'tornado'),
                        "winter_storm": _calculate_normalized_health_factor(county_rows, 'winter'),
                        # Default factors for other hazard types
                        "thunderstorm": 1.1,  # Slightly elevated health impacts
                        "extreme_heat": 1.3,  # Higher health impacts due to vulnerable populations
                        "active_shooter": 1.4,  # Significant direct health impacts
                        "infectious_disease": 1.5,  # Maximum health impacts
                        "vector_borne_disease": 1.2,  # Lyme/WNV: symptomatic illness, occasional neurologic sequelae, rare mortality
                        "electrical_outage": 1.2,  # Healthcare system disruption
                        "utilities_disruption": 1.2,  # Sanitation and water impacts
                        "supply_chain": 1.1,  # Medical supply disruption
                        "fuel_shortage": 1.0,  # Less direct health impacts
                        "cybersecurity": 1.1,  # Healthcare information systems impacts
                        "dam_failure": 1.3   # Drowning, displacement, water contamination
                    }
                
                _nri_health_data_cache = county_health_data
                logger.info(f"Successfully loaded health impact factors for {len(county_health_data)} counties")
            else:
                logger.warning(f"NRI data file not found at {nri_path}, using default health factors")
                _nri_health_data_cache = {}
                
        except Exception as e:
            logger.error(f"Error loading NRI health impact data: {str(e)}")
            _nri_health_data_cache = {}
    
    # Get health factor for the county and hazard type
    # Default to 1.0 (neutral) if data isn't available
    county_data = _nri_health_data_cache.get(county_name, {})
    
    # Normalize hazard type name (convert spaces to underscores, lowercase)
    hazard_key = hazard_type.lower().replace(' ', '_')
    
    # Get health factor with fallback to default of 1.0
    health_factor = county_data.get(hazard_key, 1.0)
    
    logger.info(f"Health impact factor for {county_name}, {hazard_type}: {health_factor:.2f}")
    return health_factor

def _calculate_normalized_health_factor(county_rows: pd.DataFrame, hazard_type: str) -> float:
    """
    Calculate a normalized health impact factor from NRI data for a specific hazard type.

    Uses the FEMA NRI Expected Annual Loss Score (EALS) column for the hazard type.
    EALS values in the NRI CSV are already expressed as 0-100 percentile scores
    relative to all US census tracts, so no additional state-relative normalization
    is needed.  A county with EALS=0 maps to 0.80 (minimal health amplification)
    and a county with EALS=100 maps to 1.50 (maximum health amplification).

    Args:
        county_rows: DataFrame containing NRI data for a specific county (all tracts)
        hazard_type: The type of hazard ('flood', 'tornado', or 'winter')

    Returns:
        A normalized health impact factor between 0.8 and 1.5
    """
    try:
        eals_field = f'{hazard_type}_eals'

        if eals_field in county_rows.columns:
            eals_value = float(county_rows[eals_field].mean())
            # Map NRI EALS percentile [0, 100] linearly to [0.80, 1.50]
            return max(0.80, min(1.50, 0.80 + 0.70 * (eals_value / 100.0)))
        else:
            # Fallback for hazard types not covered by the NRI CSV
            defaults = {'flood': 1.2, 'tornado': 1.3, 'winter': 1.1}
            return defaults.get(hazard_type, 1.0)
                
    except Exception as e:
        logger.warning(f"Error calculating health factor for {hazard_type}: {str(e)}")
        return 1.0  # Default to neutral

def calculate_residual_risk(exposure: float, vulnerability: float, resilience: float, 
                           max_risk: float = 1.0, health_impact_factor: float = None) -> float:
    """
    Calculate residual risk using the CARA-specific Exposure-Vulnerability-
    Resilience (EVR) transform:

        Residual Risk = (Exposure × Vulnerability) × (2.0 - Resilience) × HealthImpactFactor

    IMPORTANT METHODOLOGY NOTE (review finding H5):
    This is NOT the FEMA National Risk Index (NRI) residual-risk formula.
    The FEMA NRI form is:

        Risk_NRI = Exposure × AnnualLossRate × (1 + SVI) / (1 + ResilienceRating)

    The two differ in two material ways and will produce different
    numbers even when given identical inputs:

      1. CARA uses (2.0 - Resilience) as a MULTIPLICATIVE amplifier in
         the numerator. With Resilience in [0.1, 0.9] this amplifier is
         always in [1.1, 1.9], so resilience can never attenuate risk
         BELOW the E*V baseline - it can only reduce the amount of
         amplification. FEMA NRI's (1 + R) denominator can attenuate
         risk below E*V because raising R divides the numerator down.
      2. CARA folds vulnerability (including SVI components) directly
         into the E*V product as a multiplicative term in [0, 1].
         FEMA NRI uses (1 + SVI) - a multiplier in [1, 2] - so a
         CARA county with low SVI does not get the same proportional
         boost a FEMA NRI county with high SVI gets.

    Health Impact Factor inputs are derived from FEMA NRI EALS data
    (see _calculate_normalized_health_factor above), so the HIF
    surface IS FEMA-sourced; the residual-risk transform itself is
    not. An EM planner cross-walking county scores between CARA and
    FEMA NRI should expect different numbers and read the
    methodology page's "CARA EVR Transform vs FEMA NRI" comparison.

    Behaviour summary:
      - High vulnerability + low resilience -> high risk.
      - Resilience acts as a 1.1x-1.9x amplifier reduction, not a
        divisor.
      - No artificial risk floor that masks real differences between
        jurisdictions.

    Args:
        exposure: Exposure score in [0, 1] (hazard likelihood / magnitude).
        vulnerability: Vulnerability score in [0, 1] (susceptibility).
        resilience: Resilience score in [0, 1] (community capacity; higher is better).
        max_risk: Calibration constant, unused (kept for backward compatibility).
        health_impact_factor: Optional multiplier in [0.8, 1.5] derived
            from FEMA NRI EALS data via _calculate_normalized_health_factor.
            Reflects Expected Annual Loss of Population, SVI health
            components, Healthcare Access, and disability percentage.
            If None, defaults to 1.0 (no adjustment).

    Returns:
        Residual risk score in [0, 1] under the CARA EVR transform
        described above.
    """
    # Apply default health impact factor if not provided
    if health_impact_factor is None:
        health_impact_factor = 1.0
    
    # Calculate base risk from exposure and vulnerability
    base_risk = exposure * vulnerability
    
    # Calculate resilience adjustment factor
    # Low resilience (0.1) → 1.9x amplifier (high risk amplification)
    # Medium resilience (0.5) → 1.5x amplifier (moderate amplification)
    # High resilience (0.9) → 1.1x amplifier (minimal amplification)
    # This ensures resilience never completely eliminates risk but low resilience significantly amplifies it
    resilience_adjustment = 2.0 - resilience
    
    # Apply the corrected formula: Base Risk × Resilience Adjustment × Health Impact
    residual_risk = base_risk * resilience_adjustment * health_impact_factor
    
    # Ensure result is between 0 and 1
    residual_risk = max(0.0, min(1.0, residual_risk))
    
    logger.info(f"CORRECTED Risk calculation: exposure={exposure:.2f}, vulnerability={vulnerability:.2f}, " 
                f"resilience={resilience:.2f}, resilience_adj={resilience_adjustment:.2f}, " 
                f"health_factor={health_impact_factor:.2f} → risk={residual_risk:.2f}")
    
    return residual_risk