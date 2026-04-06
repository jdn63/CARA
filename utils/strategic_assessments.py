"""
Strategic Assessments Module

Thin wrappers around the StrategicAirQualityAssessment and
StrategicExtremeHeatAssessment classes for use in the risk orchestrator.
These assessments focus on long-term planning horizons rather than
acute/current conditions.
"""

import logging
from typing import Any, Dict, Optional

from utils.strategic_air_quality import StrategicAirQualityAssessment
from utils.strategic_extreme_heat import StrategicExtremeHeatAssessment

logger = logging.getLogger(__name__)

_strategic_air_quality: Optional[StrategicAirQualityAssessment] = None
_strategic_heat: Optional[StrategicExtremeHeatAssessment] = None


def get_strategic_air_quality_assessment(county_name: str, jurisdiction_id: Optional[str] = None) -> Dict[str, Any]:
    """Get strategic air quality assessment focused on long-term planning."""
    global _strategic_air_quality

    try:
        if _strategic_air_quality is None:
            _strategic_air_quality = StrategicAirQualityAssessment()
        return _strategic_air_quality.get_strategic_air_quality_assessment(county_name, jurisdiction_id)
    except Exception as e:
        logger.error(f"Error getting strategic air quality assessment: {str(e)}")
        return {
            'strategic_assessment': {
                'baseline_risk': 0.4,
                'seasonal_risk': 0.4,
                'trend_risk': 0.4,
                'climate_projection_risk': 0.4,
                'vulnerability_score': 0.4
            },
            'temporal_components': {
                'baseline': 0.24,
                'seasonal': 0.10,
                'trend': 0.06,
                'acute': 0.0
            },
            'composite_risk_score': 0.40,
            'planning_context': {
                'assessment_type': 'fallback',
                'focus': 'annual_preparedness_planning'
            }
        }


def get_strategic_heat_assessment(county_name: str, jurisdiction_id: Optional[str] = None) -> Dict[str, Any]:
    """Get strategic extreme heat assessment focused on climate adaptation planning."""
    global _strategic_heat

    try:
        if _strategic_heat is None:
            _strategic_heat = StrategicExtremeHeatAssessment()
        return _strategic_heat.get_strategic_heat_assessment(county_name, jurisdiction_id)
    except Exception as e:
        logger.error(f"Error getting strategic heat assessment: {str(e)}")
        return {
            'strategic_assessment': {
                'baseline_vulnerability': 0.5,
                'climate_projection_impact': 0.5,
                'urban_heat_island_factor': 2.0,
                'seasonal_risk': 0.5,
                'infrastructure_vulnerability': 0.5
            },
            'temporal_components': {
                'baseline': 0.30,
                'seasonal': 0.125,
                'trend': 0.075,
                'acute': 0.0
            },
            'composite_risk_score': 0.50,
            'planning_context': {
                'assessment_type': 'fallback',
                'focus': 'long_term_heat_preparedness'
            }
        }
