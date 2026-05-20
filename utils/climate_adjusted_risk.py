#!/usr/bin/env python3
"""
Climate-Adjusted Risk Analysis for Extreme Heat Events

This module provides enhanced extreme heat risk assessment based entirely on 
publicly accessible, quantitative datasets and scientific research:

DATA SOURCES:
1. NOAA/NWS climate projections and historical temperature data
2. EPA heat threshold guidelines and physiological research
3. CDC Social Vulnerability Index (SVI) demographic data
4. Wisconsin DHS Heat Vulnerability Index (DHS ArcGIS MapServer,
   block-group features aggregated to county; see utils/wi_dhs_hvi.py)
5. Census Bureau American Community Survey (ACS) data
6. USGS geographic and topographic data
7. Peer-reviewed climate science publications

METHODOLOGY IMPROVEMENTS:
- Climate change trends from NOAA/IPCC projections (quantified)
- Wet bulb temperature calculations based on meteorological science
- Vulnerability factors derived from CDC SVI and Census data
- Geographic risk variation from USGS and state data
- Heat thresholds from EPA/CDC public health guidelines
- All calculations transparent and replicable using public data
"""

import requests
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import math
import os
import json

# Get module logger (centralized config in core.py)
logger = logging.getLogger(__name__)

class ClimateAdjustedHeatRisk:
    """
    Enhanced extreme heat risk assessment incorporating climate change science
    and wet bulb temperature considerations.
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Wisconsin-specific heat thresholds (revised for climate change)
        self.heat_thresholds = {
            'moderate': 85,      # Previously 80°F - increased due to climate adaptation
            'high': 90,          # Previously 85°F - more frequent occurrence
            'very_high': 95,     # Previously 90°F - dangerous for vulnerable populations
            'extreme': 100,      # Previously 95°F - life-threatening
            'critical': 105      # New threshold for extreme events
        }
        
        # Wet bulb temperature critical thresholds (°F)
        self.wet_bulb_thresholds = {
            'concern': 79,       # 26°C - prolonged exposure becomes dangerous
            'dangerous': 82,     # 28°C - healthy adults at risk
            'lethal': 95         # 35°C - human survivability limit
        }
        
        # Climate change adjustment factors based on NOAA/IPCC published research
        # Sources: NOAA State Climate Summaries, IPCC AR6 Working Group I
        self.climate_adjustments = {
            'frequency_multiplier': 1.4,    # NOAA: 40% increase in heat events by 2050 (RCP4.5)
            'intensity_increase': 3.0,      # NOAA: 2-4°F warming by 2050 for Great Lakes region
            'duration_multiplier': 1.6,     # IPCC AR6: 60% increase in heat wave duration
            'consecutive_day_increase': 2.2  # EPA: 2.2x increase in multi-day heat events
        }
        
        # Data source references for transparency and replicability
        self.data_sources = {
            'climate_projections': 'NOAA State Climate Summaries - Wisconsin (2022)',
            'heat_thresholds': 'EPA Climate Change and Heat Islands (2021)',
            'wet_bulb_calculations': 'NOAA Technical Report OAR CPO-2 (2020)',
            'vulnerability_data': 'CDC Social Vulnerability Index 2020',
            'geographic_data': 'USGS National Map and Wisconsin DNR',
            'methodology_basis': 'IPCC AR6 Working Group I Chapter 11 (2021)'
        }

    def calculate_enhanced_heat_risk(self, county_name: str, jurisdiction_id: str = None) -> Dict[str, Any]:
        """
        Calculate extreme heat risk for TWO distinct horizons, returned in
        the same dict so the PHRAT composite and the strategic-trajectory
        panel cannot drift apart.

        Review finding Q7 (2026-05-20): the prior implementation baked
        2050 climate-trajectory multipliers (frequency 1.4, wet-bulb
        humidity 1.2, mid-century warming trend 1.35) directly into the
        12-month PHRAT score. Because base_HIF (1.3) * trend (1.35) =
        1.755 was capped at 1.6, every county silently received the
        maximum 2050 health-impact ceiling regardless of present-day
        conditions. The dashboard simultaneously labeled the composite
        "Annual Strategic (12-month)" — a horizon mismatch.

        Resolution: compute the EVR transform twice.
          - PRESENT-DAY: climate multipliers = 1.0 across the board.
            This is the value PHRAT consumes via overall_risk.
          - TRAJECTORY-2050: the original mid-century multipliers
            (NOAA WICCI, IPCC AR6). Surfaced separately on the
            dashboard as a planning trajectory; NOT composited.
        """
        try:
            vulnerability_data = self._calculate_enhanced_vulnerability(county_name, jurisdiction_id)
            resilience_data = self._calculate_climate_resilience(county_name)

            present_exposure = self._calculate_climate_adjusted_exposure(county_name, horizon='present_day')
            present_wet_bulb = self._calculate_wet_bulb_risk(county_name, horizon='present_day')
            present_trend = self._calculate_climate_trend_factor(county_name, horizon='present_day')
            present_risk = self._calculate_comprehensive_risk(
                present_exposure, vulnerability_data, resilience_data,
                present_wet_bulb, present_trend
            )

            traj_exposure = self._calculate_climate_adjusted_exposure(county_name, horizon='trajectory_2050')
            traj_wet_bulb = self._calculate_wet_bulb_risk(county_name, horizon='trajectory_2050')
            traj_trend = self._calculate_climate_trend_factor(county_name, horizon='trajectory_2050')
            traj_risk = self._calculate_comprehensive_risk(
                traj_exposure, vulnerability_data, resilience_data,
                traj_wet_bulb, traj_trend
            )

            return {
                'county_name': county_name,
                'jurisdiction_id': jurisdiction_id,
                'assessment_date': datetime.now().isoformat(),
                'horizon': 'present_day_12_month',
                'overall_risk': present_risk,
                'exposure': present_exposure,
                'vulnerability': vulnerability_data,
                'resilience': resilience_data,
                'wet_bulb_risk': present_wet_bulb,
                'climate_trend_factor': present_trend,
                'risk_level': self._determine_risk_level(present_risk),
                'key_concerns': self._identify_key_concerns(
                    present_exposure, vulnerability_data, present_wet_bulb
                ),
                'trajectory_2050': {
                    'horizon': '2025_to_2050',
                    'overall_risk': traj_risk,
                    'risk_level': self._determine_risk_level(traj_risk),
                    'delta_vs_present_day': round(traj_risk - present_risk, 4),
                    'exposure': traj_exposure,
                    'wet_bulb_risk': traj_wet_bulb,
                    'climate_trend_factor': traj_trend,
                    'multipliers_applied': {
                        'noaa_frequency_multiplier': self.climate_adjustments['frequency_multiplier'],
                        'wet_bulb_humidity_factor': 1.2,
                        'noaa_wicci_warming_trend': 1.35,
                    },
                    'note': (
                        'Separate planning trajectory. NOT composited into the '
                        'PHRAT 12-month risk score. Based on NOAA State Climate '
                        'Summaries (WI) and IPCC AR6 RCP4.5 mid-century projections.'
                    ),
                },
                'methodology': 'Climate-Adjusted Heat Risk Assessment v3.0 (horizon-separated)',
                'data_sources': self.data_sources,
                'calculation_basis': {
                    'exposure_calculation_present': 'NOAA annual heat-day count (normalized to [0, 0.95]); no 2050 frequency multiplier applied',
                    'exposure_calculation_trajectory_2050': 'NOAA annual heat-day count * 1.4 (NOAA mid-century frequency multiplier)',
                    'vulnerability_calculation': 'Weighted CDC SVI 2022 themes (socioeconomic 30%, housing-transportation 20%, household-composition 15%, minority-status 10%) + Census ACS population aged 65+ factor (25%)',
                    'resilience_calculation': 'Inverse CDC SVI socioeconomic (20%) and housing-transportation (10%) from a 0.5 baseline, clamped to [0.1, 0.9]',
                    'wet_bulb_calculation_present': 'Statewide NOAA Great Lakes wet-bulb baseline (no humidity-projection multiplier)',
                    'wet_bulb_calculation_trajectory_2050': 'Statewide baseline * 1.2 humidity projection factor',
                    'climate_trend_present': '1.0 (no mid-century warming applied)',
                    'climate_trend_trajectory_2050': '1.35 (NOAA WICCI mid-century midpoint)',
                    'overall_formula_present': '(0.7*Exposure + 0.3*Wet_Bulb) * V * (2.0 - R) * 1.3 (base heat HIF)',
                    'overall_formula_trajectory_2050': '(0.7*Exposure_2050 + 0.3*Wet_Bulb_2050) * V * (2.0 - R) * min(1.6, 1.3*1.35)',
                }
            }

        except Exception as e:
            logger.error(f"Error calculating enhanced heat risk for {county_name}: {str(e)}")
            return self._get_fallback_assessment(county_name)

    def _calculate_climate_adjusted_exposure(self, county_name: str, horizon: str = 'present_day') -> Dict[str, float]:
        """
        Calculate heat exposure from NOAA annual heat-day counts.

        Replaces the previous hand-keyed per-county base_exposure dictionary
        (72 author-assigned values) with a derivation from the Wisconsin
        annual heat-day data in utils/wisconsin_climate_data.py
        (NOAA climate-normals based). The NOAA frequency multiplier is then
        applied as before.

        The +15% urban-county heat-island bonus (formerly a hand-picked list
        of 7 counties) was removed because it had the same anti-pattern
        documented in utils/natural_hazards_risk.py: an uncited county list
        that produced abrupt cliffs between adjacent counties. Urban heat
        island effects are partly captured by NOAA station siting; if a
        continuous per-county imperviousness or population-density signal
        becomes available it should be folded in here as a smooth term.
        """
        from utils.wisconsin_climate_data import get_wisconsin_heat_days

        annual_heat_days = get_wisconsin_heat_days(county_name) or 12
        # Wisconsin observed annual heat-day range: roughly 5 (far north)
        # to 20 (southern urban). Normalize to [0, 0.95].
        base_exposure = max(0.0, min(0.95, annual_heat_days / 20.0))

        # Horizon gate (Q7): the NOAA frequency multiplier is a 2050
        # mid-century projection and only applies to the trajectory
        # horizon. For the present-day 12-month PHRAT score it must be
        # 1.0 so the strategic composite reflects current conditions.
        if horizon == 'trajectory_2050':
            frequency_multiplier = self.climate_adjustments['frequency_multiplier']
        else:
            frequency_multiplier = 1.0

        climate_adjusted_exposure = min(
            0.95,
            base_exposure * frequency_multiplier
        )

        return {
            'horizon': horizon,
            'base_exposure': base_exposure,
            'annual_heat_days': annual_heat_days,
            'frequency_multiplier_applied': frequency_multiplier,
            'climate_adjusted': climate_adjusted_exposure,
            'heat_island_factor': 1.0,
            'final_exposure': climate_adjusted_exposure,
            'confidence': 0.85
        }


    def _calculate_enhanced_vulnerability(self, county_name: str, jurisdiction_id: str = None) -> Dict[str, float]:
        """
        Calculate heat vulnerability from CDC SVI 2022 themes + Census ACS
        population aged 65+ percentage.

        Replaces the previous hand-keyed per-county base_vulnerability
        dictionary (72 author-assigned values) and the hand-picked +25%
        "high heat vulnerability" list of 6 counties. Weights follow
        heat-specific vulnerability literature: socioeconomic status and
        housing/AC access dominate, with elderly share applied as a
        heat-physiology-specific factor.
        """
        from utils.svi_data import get_svi_data
        from utils.census_data_loader import wisconsin_census

        try:
            svi_raw = get_svi_data(county_name) or {}
            svi = {
                'socioeconomic': svi_raw.get('socioeconomic', 0.5),
                'housing_transportation': svi_raw.get('housing_transportation', 0.5),
                'household_composition': svi_raw.get('household_composition', 0.5),
                'minority_status': svi_raw.get('minority_status', 0.5),
            }
        except Exception as e:
            logger.warning(f"SVI fetch failed for {county_name}: {e}; using statewide median 0.5")
            svi = {'socioeconomic': 0.5, 'housing_transportation': 0.5,
                   'household_composition': 0.5, 'minority_status': 0.5}

        try:
            elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name) or 18.7
        except Exception as e:
            logger.warning(f"Census elderly fetch failed for {county_name}: {e}; using WI median 18.7")
            elderly_pct = 18.7

        # Normalize elderly%: WI county range roughly 10-30%, map to [0, 1].
        elderly_factor = max(0.0, min(1.0, (elderly_pct - 10.0) / 20.0))

        vulnerability_raw = (
            0.30 * svi['socioeconomic'] +
            0.20 * svi['housing_transportation'] +
            0.15 * svi['household_composition'] +
            0.10 * svi['minority_status'] +
            0.25 * elderly_factor
        )

        final_vulnerability = max(0.0, min(0.85, vulnerability_raw))

        return {
            'base_vulnerability': vulnerability_raw,
            'svi_themes': svi,
            'elderly_pct': elderly_pct,
            'elderly_factor': elderly_factor,
            'final_vulnerability': final_vulnerability,
            'confidence': 0.80
        }


    def _calculate_climate_resilience(self, county_name: str) -> Dict[str, float]:
        """
        Calculate heat resilience from inverse CDC SVI socioeconomic and
        housing-transportation themes.

        Replaces the previous hand-keyed per-county base_resilience dictionary
        (72 author-assigned values with judgment comments such as "Strong
        county resources, university research" and "Limited rural resources")
        and the uncited 15% climate-adaptation penalty applied uniformly to
        every county.

        Mirrors the inverse-SVI pattern used in
        utils/natural_hazards_risk.py._calculate_em_resilience. A continuous
        capacity index (cooling-center counts per capita, hospital beds per
        capita) could be folded in here as a smooth term if a cited Wisconsin
        source becomes available.
        """
        from utils.svi_data import get_svi_data

        try:
            svi_raw = get_svi_data(county_name) or {}
            svi_socio = svi_raw.get('socioeconomic', 0.5)
            svi_housing = svi_raw.get('housing_transportation', 0.5)
        except Exception as e:
            logger.warning(f"SVI fetch failed for {county_name}: {e}; using statewide median 0.5")
            svi_socio = 0.5
            svi_housing = 0.5

        resilience_raw = 0.5
        resilience_raw += (1.0 - svi_socio) * 0.20
        resilience_raw += (1.0 - svi_housing) * 0.10

        final_resilience = max(0.1, min(0.9, resilience_raw))

        return {
            'base_resilience': resilience_raw,
            'svi_socioeconomic': svi_socio,
            'svi_housing_transportation': svi_housing,
            'climate_adaptation_penalty': 1.0,
            'final_resilience': final_resilience,
            'confidence': 0.75
        }


    def _calculate_wet_bulb_risk(self, county_name: str, horizon: str = 'present_day') -> Dict[str, float]:
        """
        Calculate wet-bulb temperature risk from a statewide NOAA Great Lakes
        mid-century baseline.

        The previous hand-keyed per-county wet-bulb dictionary (72 author-
        assigned values) had no source citation; per-county wet-bulb
        projections at this resolution are not publicly available for
        Wisconsin. A single statewide baseline (midpoint of NOAA Great Lakes
        region wet-bulb projections) is used instead. If higher-resolution
        NOAA gridded wet-bulb data becomes available, this function should
        derive a county-specific value from that grid.
        """
        # NOAA Great Lakes region projected mid-century wet-bulb risk midpoint
        statewide_baseline = 0.60
        # Horizon gate (Q7): the 20% humidity rise is a mid-century
        # projection and only applies to the trajectory horizon.
        if horizon == 'trajectory_2050':
            climate_humidity_increase = 1.2
        else:
            climate_humidity_increase = 1.0
        final_wet_bulb_risk = min(0.85, statewide_baseline * climate_humidity_increase)

        return {
            'horizon': horizon,
            'base_wet_bulb_risk': statewide_baseline,
            'climate_humidity_factor': climate_humidity_increase,
            'final_wet_bulb_risk': final_wet_bulb_risk,
            'confidence': 0.65,
            'note': 'Statewide NOAA Great Lakes baseline; per-county wet-bulb grid not yet integrated'
        }


    def _calculate_climate_trend_factor(self, county_name: str, horizon: str = 'present_day') -> Dict[str, float]:
        """
        Apply a single statewide warming trend factor from NOAA WICCI.

        The previous N/S/E/W regional gradient (per-county region assignment
        with +25%/30%/35%/45% trend bonuses) and the +10% urban-county
        amplification list were hand-coded county lists with the same anti-
        pattern documented in utils/natural_hazards_risk.py. NOAA WICCI 2021
        Assessment projects ~3-5 degrees F warming statewide by mid-century
        with only a small north/south gradient; the per-county geographic
        differentiation in the heat formula now comes from the exposure
        component (NOAA annual heat-day counts), not from a hand-keyed
        trend multiplier.
        """
        # Horizon gate (Q7): the NOAA WICCI 1.35 mid-century warming
        # midpoint applies only to the trajectory horizon. For the
        # present-day 12-month PHRAT score the trend factor is 1.0 so
        # the EVR HIF reduces to the base heat HIF (1.3) without
        # silently saturating against the 1.6 cap.
        if horizon == 'trajectory_2050':
            statewide_trend = 1.35
        else:
            statewide_trend = 1.0

        return {
            'horizon': horizon,
            'region': 'wisconsin_statewide',
            'base_trend': statewide_trend,
            'urban_amplification': 1.0,
            'final_trend_factor': statewide_trend,
            'confidence': 0.85
        }


    def _calculate_comprehensive_risk(self, exposure: Dict, vulnerability: Dict,
                                    resilience: Dict, wet_bulb: Dict,
                                    climate_trend: Dict) -> float:
        """
        Calculate comprehensive extreme-heat risk using a SINGLE transparent
        EVR-consistent transform.

        Formula:
            risk = E_combined * V * (2.0 - R) * HIF_combined

        Where:
            E_combined = 0.7 * base_exposure + 0.3 * wet_bulb_exposure
                (humidity is part of heat exposure, not a separate amplifier)
            V          = final_vulnerability
            R          = final_resilience
            HIF_combined = base_HIF (1.3) * climate_trend_factor, capped at 1.6
                (climate trend amplifies health consequences of heat)

        Result is clamped to [0, 1] inside calculate_residual_risk.

        This replaces the prior two-stage formula (base EVR then uncapped
        wet-bulb and trend multipliers, with a late 0.1-0.9 clamp in
        data_processor.py) which produced opaque amplification and
        artificial bunching at the top of the heat domain.
        """
        from utils.risk_calculation import calculate_residual_risk

        # Extract final component values, defensively clamped to [0, 1]
        exposure_score = max(0.0, min(1.0, exposure['final_exposure']))
        vulnerability_score = max(0.0, min(1.0, vulnerability['final_vulnerability']))
        resilience_score = max(0.0, min(1.0, resilience['final_resilience']))
        wet_bulb_score = max(0.0, min(1.0, wet_bulb['final_wet_bulb_risk']))
        trend_factor = max(0.5, min(2.0, climate_trend['final_trend_factor']))

        # Single combined exposure term: heat frequency + humidity
        combined_exposure = (0.7 * exposure_score) + (0.3 * wet_bulb_score)
        combined_exposure = max(0.0, min(1.0, combined_exposure))

        # Single combined health-impact factor: base heat HIF * climate trend
        # Heat HIF baseline is 1.3 (elevated). Trend factor typically 1.0-1.3.
        # Capped at 1.6 to keep the HIF inside a defensible health-amplifier range.
        base_heat_hif = 1.3
        combined_hif = min(1.6, base_heat_hif * trend_factor)

        # Single EVR-consistent transform (output is clamped to [0, 1] internally)
        final_risk = calculate_residual_risk(
            exposure=combined_exposure,
            vulnerability=vulnerability_score,
            resilience=resilience_score,
            health_impact_factor=combined_hif
        )

        logger.debug(
            "Extreme heat EVR: E_base=%.2f, wet_bulb=%.2f -> E_combined=%.2f; "
            "V=%.2f; R=%.2f; trend=%.2f -> HIF_combined=%.2f; risk=%.3f",
            exposure_score, wet_bulb_score, combined_exposure,
            vulnerability_score, resilience_score, trend_factor,
            combined_hif, final_risk
        )

        return final_risk

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on comprehensive score."""
        if risk_score >= 0.85:
            return "Critical"
        elif risk_score >= 0.70:
            return "Very High"
        elif risk_score >= 0.55:
            return "High"
        elif risk_score >= 0.40:
            return "Moderate"
        else:
            return "Low"

    def _identify_key_concerns(self, exposure: Dict, vulnerability: Dict, 
                             wet_bulb: Dict) -> List[str]:
        """Identify key concerns based on risk components."""
        concerns = []
        
        if exposure['final_exposure'] >= 0.70:
            concerns.append("High frequency of extreme heat events expected")
        
        if vulnerability['final_vulnerability'] >= 0.70:
            concerns.append("Vulnerable population at significant risk")
        
        if wet_bulb['final_wet_bulb_risk'] >= 0.65:
            concerns.append("Dangerous wet bulb temperatures possible")
        
        if exposure['heat_island_factor'] > 1.1:
            concerns.append("Urban heat island effect amplifies risk")
        
        return concerns

    def _get_fallback_assessment(self, county_name: str) -> Dict[str, Any]:
        """Return an explicit "unavailable" assessment when calculation fails.

        Previously this method silently assigned every county overall_risk=0.70
        ("High") on any exception, which corrupted the PHRAT composite by
        injecting a fabricated High value whenever the heat calculator failed.
        Real data is required: when the calculation cannot be completed, the
        domain is marked unavailable so the composite will renormalize over
        the remaining real-data domains and the dashboard surfaces the gap
        honestly.
        """
        return {
            'county_name': county_name,
            'overall_risk': None,
            'risk_level': 'Unavailable',
            'horizon': 'present_day_12_month',
            'exposure': {'final_exposure': None},
            'vulnerability': {'final_vulnerability': None},
            'resilience': {'final_resilience': None},
            'wet_bulb_risk': {'final_wet_bulb_risk': None},
            'climate_trend_factor': {'final_trend_factor': None},
            'trajectory_2050': None,
            'metrics': {
                'heat_advisories': None,
                'annual_heat_days': None,
                'ed_visits': None,
            },
            'data_quality': {
                'available': False,
                'reason': 'Climate-adjusted heat risk calculation failed',
                'classification': 'unavailable',
            },
            'error': 'Unable to calculate climate-adjusted heat assessment',
            'key_concerns': [],
            'methodology': 'Heat risk unavailable - no synthetic substitute used',
            'data_sources': [],
        }

# Initialize the climate-adjusted heat risk calculator
climate_heat_risk = ClimateAdjustedHeatRisk()

def calculate_enhanced_extreme_heat_risk(county_name: str, jurisdiction_id: str = None) -> Dict[str, Any]:
    """
    Main function to calculate enhanced extreme heat risk with climate considerations.
    
    Args:
        county_name: County name for assessment
        jurisdiction_id: Optional jurisdiction ID
        
    Returns:
        Enhanced extreme heat risk assessment with real-time metrics
    """
    # Get the enhanced heat risk calculation
    heat_risk_data = climate_heat_risk.calculate_enhanced_heat_risk(county_name, jurisdiction_id)
    
    # Import and add real-time metrics
    try:
        from utils.extreme_heat_metrics import get_extreme_heat_metrics
        real_time_metrics = get_extreme_heat_metrics(county_name)
        
        # Add real-time metrics to the existing metrics structure
        if 'metrics' not in heat_risk_data:
            heat_risk_data['metrics'] = {}
        
        heat_risk_data['metrics'].update({
            'annual_heat_days': real_time_metrics.get('annual_heat_days'),
            'heat_advisories': real_time_metrics.get('heat_advisories'),
            'elderly_percentage': real_time_metrics.get('elderly_percentage'),
            'ed_visits': real_time_metrics.get('ed_visits'),
            'real_time_data_sources': real_time_metrics.get('data_sources', {}),
            'last_updated': real_time_metrics.get('last_updated')
        })
        
        logger.info(f"Added real-time heat metrics for {county_name}")
        
    except Exception as e:
        logger.warning(f"Could not fetch real-time heat metrics for {county_name}: {e}")
        # Use Wisconsin climate data as fallback when real-time data is unavailable
        try:
            from utils.wisconsin_climate_data import (
                get_wisconsin_heat_days, get_wisconsin_elderly_population,
                get_wisconsin_heat_ed_visits, get_wisconsin_heat_advisories
            )
            
            if 'metrics' not in heat_risk_data:
                heat_risk_data['metrics'] = {}
            
            heat_risk_data['metrics'].update({
                'annual_heat_days': get_wisconsin_heat_days(county_name),
                'heat_advisories': get_wisconsin_heat_advisories(county_name),
                'elderly_percentage': get_wisconsin_elderly_population(county_name),
                'ed_visits': get_wisconsin_heat_ed_visits(county_name),
                'data_sources': 'Wisconsin climate data fallback',
                'real_time_data_note': 'Using historical Wisconsin climate data'
            })
            logger.info(f"Using Wisconsin climate data fallback for {county_name}")
        except Exception as fallback_error:
            logger.error(f"Failed to get fallback data for {county_name}: {fallback_error}")
            # Only use None as last resort
            if 'metrics' not in heat_risk_data:
                heat_risk_data['metrics'] = {}
            heat_risk_data['metrics'].update({
                'annual_heat_days': 'N/A',
                'heat_advisories': 'N/A',
                'elderly_percentage': 'N/A',
                'ed_visits': 'N/A',
                'real_time_data_note': 'Data temporarily unavailable'
            })
    
    return heat_risk_data