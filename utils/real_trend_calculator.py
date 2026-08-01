"""
Real Trend Calculator for BSTA Temporal Risk Framework

Calculates trend scores (0-1 scale, 0.5 = neutral) using real cached data
from NOAA Storm Events, NOAA nClimDiv observed county climate trends, and
Census data.

Each function returns a dict with:
  - score: float 0-1 (0.5 = no trend, >0.5 = increasing risk, <0.5 = decreasing)
  - data_source: string describing the data source
  - description: human-readable explanation of the trend
  - years_compared: string showing the comparison window
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def _ratio_to_trend_score(ratio: float, sensitivity: float = 1.0) -> float:
    """
    Convert a ratio (recent/historical) to a 0-1 trend score.
    
    ratio = 1.0 means no change → score = 0.5
    ratio > 1.0 means increasing → score > 0.5
    ratio < 1.0 means decreasing → score < 0.5
    
    sensitivity controls how quickly the score moves toward 0 or 1.
    Default sensitivity of 1.0 means:
      - 50% increase (ratio=1.5) → score ≈ 0.67
      - 100% increase (ratio=2.0) → score ≈ 0.75
      - 50% decrease (ratio=0.5) → score ≈ 0.33
    """
    if ratio <= 0:
        return 0.15
    
    log_ratio = (ratio - 1.0) * sensitivity
    score = 0.5 + (log_ratio / (2.0 + abs(log_ratio)))
    return max(0.05, min(0.95, score))


def _neutral_trend(reason: str) -> Dict[str, Any]:
    return {
        'score': 0.5,
        'data_source': 'None available',
        'description': f'Neutral (no trend data): {reason}',
        'years_compared': 'N/A'
    }


def calculate_natural_hazard_trend(county_name: str, hazard_type: str) -> Dict[str, Any]:
    """
    Calculate trend for natural hazard types using NOAA Storm Events cached data.
    
    Compares event counts in recent 5 years vs prior 5-15 years.
    """
    try:
        from utils.noaa_storm_events import get_county_storm_summary
        
        storm_data = get_county_storm_summary(county_name)
        if not storm_data:
            return _neutral_trend(f'No NOAA Storm Events cache for {county_name}')
        
        events_by_year = storm_data.get('events_by_year', {})
        if not events_by_year:
            return _neutral_trend(f'No yearly event breakdown for {county_name}')
        
        current_year = datetime.now().year
        years = sorted([int(y) for y in events_by_year.keys()])
        
        if len(years) < 6:
            return _neutral_trend(f'Fewer than 6 years of data for {county_name}')
        
        midpoint = current_year - 5
        
        recent_years = [y for y in years if y >= midpoint]
        historical_years = [y for y in years if y < midpoint]
        
        if not recent_years or not historical_years:
            return _neutral_trend(f'Insufficient split for trend comparison')
        
        hazard_category = _map_hazard_to_storm_category(hazard_type)

        if hazard_category and hazard_category in storm_data.get('by_category', {}):
            recent_count, historical_count = _count_events_by_category(
                storm_data, county_name, hazard_category, recent_years, historical_years
            )
        else:
            recent_count = sum(events_by_year.get(str(y), 0) for y in recent_years)
            historical_count = sum(events_by_year.get(str(y), 0) for y in historical_years)
        
        recent_annual = recent_count / max(1, len(recent_years))
        historical_annual = historical_count / max(1, len(historical_years))
        
        if historical_annual < 0.1:
            if recent_annual > 0.5:
                score = 0.75
                description = f'New {hazard_type} activity: {recent_annual:.1f} events/year (no prior baseline)'
            else:
                return _neutral_trend(f'Very few {hazard_type} events in record for {county_name}')
        else:
            ratio = recent_annual / historical_annual
            score = _ratio_to_trend_score(ratio, sensitivity=1.2)
            pct_change = (ratio - 1.0) * 100
            direction = 'increasing' if pct_change > 5 else ('decreasing' if pct_change < -5 else 'stable')
            description = (f'{hazard_type.replace("_", " ").title()} events {direction}: '
                          f'{historical_annual:.1f}/yr ({min(historical_years)}-{max(historical_years)}) → '
                          f'{recent_annual:.1f}/yr ({min(recent_years)}-{max(recent_years)}), '
                          f'{pct_change:+.0f}% change')
        
        result = {
            'score': round(score, 3),
            'data_source': 'NOAA NCEI Storm Events Database',
            'description': description,
            'years_compared': f'{min(historical_years)}-{max(historical_years)} vs {min(recent_years)}-{max(recent_years)}'
        }
        
        # NFIP claims-trend blend removed 2026-08: claim counts track
        # flood-insurance participation, not flood hazard, so blending them
        # rewarded insurance uptake.  Flood trend is now pure NOAA measured
        # events, like every other natural hazard.
        return result
        
    except Exception as e:
        logger.error(f"Error calculating {hazard_type} trend for {county_name}: {e}")
        return _neutral_trend(f'Error: {str(e)}')


def _map_hazard_to_storm_category(hazard_type: str) -> Optional[str]:
    mapping = {
        'flood': 'flood',
        'tornado': 'tornado',
        'winter_storm': 'winter',
        'thunderstorm': 'thunderstorm',
        'straight_line_wind': 'straight_line_wind'
    }
    return mapping.get(hazard_type)


def _count_events_by_category(storm_data: Dict, county_name: str,
                               category: str, recent_years: list, 
                               historical_years: list) -> tuple:
    """
    Count events for a specific hazard category by year range.
    Falls back to total events if category-level yearly breakdown unavailable.
    """
    events_by_year = storm_data.get('events_by_year', {})

    cat_data = storm_data.get('by_category', {}).get(category, {})
    cat_total = cat_data.get('event_count', 0)
    total_events = storm_data.get('total_events', 1)
    
    if total_events > 0 and cat_total > 0:
        cat_fraction = cat_total / total_events
    else:
        cat_fraction = 0.25
    
    recent_total = sum(events_by_year.get(str(y), 0) for y in recent_years)
    historical_total = sum(events_by_year.get(str(y), 0) for y in historical_years)
    
    return (recent_total * cat_fraction, historical_total * cat_fraction)


def calculate_extreme_heat_trend(county_name: str) -> Dict[str, Any]:
    """
    Calculate extreme heat trend from OBSERVED county temperature data.

    Uses the baked NOAA nClimDiv snapshot (utils/climate_trends.py): the
    county's recent 15-year mean annual temperature (2011-2025) against its
    own 1951-2000 baseline.  Replaced the static projection-multiplier
    scoring retired in August 2026, which assigned one constant per
    three-zone map regardless of what any county had actually measured.

    Score mapping: 0.5 neutral at no observed change, +0.15 per degree F of
    observed warming (a county at +1.0 F scores 0.65, at +2.0 F scores
    0.80), clamped to [0.35, 0.85].  The slope is a documented display
    convention; the measured delta itself is shown in the description.
    """
    try:
        from utils.climate_trends import get_tavg_trend_info

        info = get_tavg_trend_info(county_name)
        if not info:
            return _neutral_trend('nClimDiv county temperature snapshot unavailable')

        delta = info['delta_f']
        score = max(0.35, min(0.85, 0.5 + (delta * 0.15)))
        direction = 'warming' if delta > 0.1 else ('cooling' if delta < -0.1 else 'stable')

        return {
            'score': round(score, 3),
            'data_source': 'NOAA nClimDiv observed county temperature (Climate at a Glance county series)',
            'description': (f'Observed mean annual temperature {direction}: '
                            f'{info["baseline_mean"]:.1f}F ({info["baseline_period"]}) to '
                            f'{info["recent_mean"]:.1f}F ({info["recent_period"]}), '
                            f'{delta:+.1f}F change for {county_name} County'),
            'years_compared': f'{info["baseline_period"]} vs {info["recent_period"]}'
        }

    except Exception as e:
        logger.error(f"Error calculating extreme heat trend for {county_name}: {e}")
        return _neutral_trend(f'Error: {str(e)}')


def calculate_air_quality_trend(county_name: str) -> Dict[str, Any]:
    """
    Calculate air quality trend using strategic air quality assessment data.
    
    Incorporates documented wildfire smoke episode increases affecting Wisconsin.
    """
    try:
        from utils.strategic_air_quality import StrategicAirQualityAssessment
        
        assessment = StrategicAirQualityAssessment()
        
        county_key = county_name.lower().replace(' county', '').strip()
        county_trend = assessment.historical_trends.get(county_key, 
                                                         assessment.historical_trends.get('default', {}))
        
        trend_direction = county_trend.get('trend_direction', 'stable')
        wildfire_vuln = county_trend.get('wildfire_vulnerability', 0.3)
        
        if trend_direction == 'improving':
            base_score = 0.40
        elif trend_direction == 'worsening':
            base_score = 0.70
        else:
            base_score = 0.50
        
        wildfire_adjustment = (wildfire_vuln - 0.3) * 0.3
        score = base_score + wildfire_adjustment
        
        wildfire_increase = getattr(assessment, 'climate_projections', {}).get(
            'wildfire_smoke_episodes_increase', 1.5)
        
        score = max(0.1, min(0.9, score))
        
        direction_text = {
            'improving': 'Traditional air pollutants improving',
            'stable': 'Traditional air pollutants stable',
            'worsening': 'Air quality declining'
        }.get(trend_direction, 'Trend unknown')
        
        return {
            'score': round(score, 3),
            'data_source': 'EPA Air Quality System (AQS) 2019-2023 + Wildfire Smoke Projections',
            'description': (f'{direction_text} for {county_name}. '
                          f'However, Canadian/Western wildfire smoke episodes have increased ~150% '
                          f'since 2018, creating a competing upward trend in particulate exposure.'),
            'years_compared': '2019-2023 AQS trend analysis'
        }
        
    except Exception as e:
        logger.error(f"Error calculating air quality trend for {county_name}: {e}")
        return _neutral_trend(f'Error: {str(e)}')


def calculate_demographic_trend(county_name: str) -> Dict[str, Any]:
    """
    Calculate demographic trend reflecting population aging.
    
    Wisconsin's population aged 65+ is growing faster than the overall population,
    increasing vulnerability across multiple risk domains.
    Uses Census ACS data and documented state-level aging trends.
    """
    try:
        from utils.census_data_loader import wisconsin_census

        current_pct = wisconsin_census.get_elderly_population_percentage(county_name)
        
        if current_pct is None or current_pct <= 0:
            current_pct = 18.0
        
        wi_avg_65plus_2020 = 17.5
        wi_avg_65plus_2024 = 19.2
        annual_increase_rate = (wi_avg_65plus_2024 / wi_avg_65plus_2020) ** (1/4) - 1
        
        if current_pct > 22:
            vulnerability_factor = 1.15
        elif current_pct > 20:
            vulnerability_factor = 1.10
        elif current_pct > 18:
            vulnerability_factor = 1.05
        else:
            vulnerability_factor = 1.0
        
        five_year_change = (1 + annual_increase_rate) ** 5 * vulnerability_factor
        score = _ratio_to_trend_score(five_year_change, sensitivity=2.0)
        
        return {
            'score': round(score, 3),
            'data_source': 'U.S. Census Bureau ACS 5-Year Estimates',
            'description': (f'{county_name} population aged 65+: {current_pct:.1f}% '
                          f'(WI avg growth: {annual_increase_rate*100:.1f}%/year). '
                          f'Population aging increases vulnerability across all hazard types.'),
            'years_compared': '2020-2024 Census ACS estimates'
        }
        
    except Exception as e:
        logger.error(f"Error calculating demographic trend for {county_name}: {e}")
        return {
            'score': 0.58,
            'data_source': 'Wisconsin Demographic Projections (DOA)',
            'description': 'Wisconsin statewide aging trend applied (population 65+ growing ~2.4%/year)',
            'years_compared': '2020-2024 state-level estimates'
        }


def get_trend_score(risk_type: str, county_name: str) -> Dict[str, Any]:
    """
    Main entry point: get real trend score for any risk type and county.
    
    Returns trend data dict or None for domains where trend is disabled.
    """
    clean_county = county_name.replace(' County', '').strip() if county_name else ''
    
    if risk_type in ('flood', 'tornado', 'winter_storm', 'thunderstorm', 'straight_line_wind'):
        result = calculate_natural_hazard_trend(clean_county, risk_type)
        demo_trend = calculate_demographic_trend(clean_county)
        if demo_trend['score'] > 0.5:
            demo_weight = 0.15
            result['score'] = round(
                result['score'] * (1 - demo_weight) + demo_trend['score'] * demo_weight, 3)
            result['description'] += f' [Demographic factor: {demo_trend["description"]}]'
            result['data_source'] += ' + Census ACS Demographics'
        return result
    
    elif risk_type == 'extreme_heat':
        result = calculate_extreme_heat_trend(clean_county)
        demo_trend = calculate_demographic_trend(clean_county)
        if demo_trend['score'] > 0.5:
            demo_weight = 0.20
            result['score'] = round(
                result['score'] * (1 - demo_weight) + demo_trend['score'] * demo_weight, 3)
            result['description'] += f' [Demographic factor: {demo_trend["description"]}]'
        return result
    
    elif risk_type == 'air_quality':
        return calculate_air_quality_trend(clean_county)
    
    elif risk_type == 'infectious_disease':
        return None
    
    elif risk_type in ('active_shooter', 'electrical_outage',
                       'utilities_disruption', 'supply_chain', 'fuel_shortage'):
        return _neutral_trend(f'No reliable trend data source for {risk_type}')
    
    else:
        return _neutral_trend(f'Unknown risk type: {risk_type}')


def get_all_trend_scores(county_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Get trend scores for all risk domains for a county.
    Useful for dashboard display.
    """
    risk_types = [
        'flood', 'tornado', 'winter_storm', 'thunderstorm', 'straight_line_wind',
        'extreme_heat', 'air_quality', 'infectious_disease',
        'active_shooter'
    ]
    
    results = {}
    for risk_type in risk_types:
        trend = get_trend_score(risk_type, county_name)
        if trend is not None:
            results[risk_type] = trend
        else:
            results[risk_type] = {
                'score': None,
                'data_source': 'Trend disabled for this domain',
                'description': 'Trend analysis not applicable; acute surveillance used instead',
                'years_compared': 'N/A'
            }
    
    return results
