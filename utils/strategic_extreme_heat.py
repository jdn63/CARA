"""
Strategic Extreme Heat Risk Assessment Module

Focused on climate change projections and multi-year heat trends for annual
strategic planning.  Per-county differentiation is derived from authoritative
sources (CDC SVI 2022 themes, Census ACS population), not from hand-keyed
county dictionaries.

CLEANUP HISTORY:
Prior versions of this module shipped four hand-keyed county lookups:
  1. self.county_baseline_vulnerability  (67-county dict of vulnerability
     scores 0.35-0.82 with no traceable per-county citation)
  2. self.urban_heat_island              (11-city dict of degrees-F UHI
     amplification with no per-city citation)
  3. urban_mapping                       (10-entry county->city table)
  4. urban_counties / rural_high_risk    (hand-picked 7- and 5-county lists
     used as discrete +0.2 / +0.1 infrastructure-vulnerability bumps)

These were replaced with continuous per-county derivations from CDC SVI
and Census ACS, mirroring the Option-1 cleanup pattern already applied to
utils/natural_hazards_risk.py, utils/dam_failure_risk.py, and
utils/climate_adjusted_risk.py.  Output dictionary shape is preserved so
the strategic_assessments.py caller continues to work unchanged.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache
from utils.planning_mode_config import get_planning_mode

logger = logging.getLogger(__name__)


class StrategicExtremeHeatAssessment:
    """
    Strategic extreme heat risk assessment focusing on climate projections and
    long-term adaptation planning rather than current temperature conditions.
    """

    def __init__(self):
        self.planning_mode = get_planning_mode("annual_strategic")
        self.cache_duration = 86400 * 30  # 30-day cache for strategic planning data

        # Wisconsin climate change projections (2025-2050)
        # Source: Wisconsin Initiative on Climate Change Impacts (WICCI) 2021 Assessment
        self.climate_projections = {
            'temperature_increase': {
                'annual_avg': 4.5,      # degrees F increase by 2050 (mid-range scenario)
                'summer_max': 6.2,      # degrees F increase in summer maximum temperatures
                'heat_wave_intensity': 7.1,  # degrees F increase in peak heat wave temperatures
            },
            'frequency_changes': {
                'days_above_90f': 2.8,        # 2.8x increase in days above 90F
                'days_above_95f': 4.2,        # 4.2x increase in days above 95F
                'heat_wave_frequency': 3.5,   # 3.5x increase in heat wave events
                'consecutive_hot_days': 2.1,  # 2.1x increase in multi-day heat events
            },
            'duration_changes': {
                'heat_wave_length': 1.9,   # 90% increase in heat wave duration
                'cooling_relief': 0.7,     # 30% decrease in nighttime cooling
            },
        }

        # Seasonal heat risk patterns for Wisconsin strategic planning
        self.seasonal_patterns = {
            'spring': {
                'risk_factor': 0.3,
                'focus': 'early_heat_preparedness',
                'key_risks': ['rapid temperature increases', 'unprepared populations', 'HVAC system testing'],
            },
            'summer': {
                'risk_factor': 1.0,
                'focus': 'peak_heat_response',
                'key_risks': ['sustained high temperatures', 'heat waves', 'energy grid stress'],
            },
            'fall': {
                'risk_factor': 0.4,
                'focus': 'late_season_heat_events',
                'key_risks': ['unexpected hot weather', 'school heat concerns', 'cooling system maintenance'],
            },
            'winter': {
                'risk_factor': 0.1,
                'focus': 'planning_and_preparation',
                'key_risks': ['infrastructure planning', 'vulnerable population identification', 'equipment readiness'],
            },
        }

    def get_strategic_heat_assessment(self, county_name: str, jurisdiction_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate strategic extreme heat risk assessment for annual planning.
        """
        county_key = county_name.lower().replace(' county', '').replace(' ', '_')

        cache_key = f"strategic_heat_{county_key}"
        cached_data = get_from_persistent_cache(cache_key, self.cache_duration)
        if cached_data:
            logger.info(f"Using cached strategic heat assessment for {county_name}")
            return cached_data

        baseline_vulnerability = self._get_baseline_vulnerability(county_name)
        climate_impact = self._calculate_climate_projections(baseline_vulnerability)
        uhi_amplification = self._calculate_urban_heat_island(county_name)

        current_season = self._get_current_season()
        seasonal_factor = self.seasonal_patterns[current_season]['risk_factor']
        seasonal_risk = (baseline_vulnerability + climate_impact) * seasonal_factor

        trend_risk = self._calculate_trend_component(baseline_vulnerability, climate_impact)
        infrastructure_risk = self._assess_infrastructure_vulnerability(county_name, baseline_vulnerability)

        recommendations = self._generate_adaptation_recommendations(
            county_name, baseline_vulnerability, climate_impact, infrastructure_risk
        )

        assessment = {
            'strategic_assessment': {
                'baseline_vulnerability': round(baseline_vulnerability, 2),
                'climate_projection_impact': round(climate_impact, 2),
                'urban_heat_island_factor': round(uhi_amplification, 1),
                'seasonal_risk': round(seasonal_risk, 2),
                'infrastructure_vulnerability': round(infrastructure_risk, 2),
            },
            'temporal_components': {
                'baseline': round(baseline_vulnerability * 0.6, 3),
                'seasonal': round(seasonal_risk * 0.25, 3),
                'trend': round(trend_risk * 0.15, 3),
                'acute': 0.0,
            },
            'composite_risk_score': round((
                baseline_vulnerability * 0.6
                + seasonal_risk * 0.25
                + trend_risk * 0.15
            ), 2),
            'climate_projections_2050': {
                'temperature_increase_f': self.climate_projections['temperature_increase']['annual_avg'],
                'days_above_90f_multiplier': self.climate_projections['frequency_changes']['days_above_90f'],
                'heat_wave_frequency_multiplier': self.climate_projections['frequency_changes']['heat_wave_frequency'],
                'heat_wave_duration_multiplier': self.climate_projections['duration_changes']['heat_wave_length'],
            },
            'planning_context': {
                'assessment_type': 'strategic_climate_adaptation',
                'focus': 'long_term_heat_preparedness',
                'time_horizon': '2025_to_2050',
                'current_season': current_season,
                'seasonal_planning_focus': self.seasonal_patterns[current_season]['focus'],
            },
            'risk_factors': {
                'primary_vulnerability': 'high' if baseline_vulnerability > 0.6 else 'moderate',
                'climate_change_impact': 'high' if climate_impact > 0.5 else 'moderate',
                'urban_heat_amplification': uhi_amplification,
                'key_seasonal_risks': self.seasonal_patterns[current_season]['key_risks'],
            },
            'strategic_recommendations': recommendations,
            'data_sources': [
                'Wisconsin Initiative on Climate Change Impacts (WICCI) 2021 Assessment',
                'NOAA Wisconsin Climate Projections 2025-2050',
                'Wisconsin DHS Heat Vulnerability Index (ArcGIS MapServer, county-aggregated)',
                'CDC Social Vulnerability Index (SVI) 2022 (fallback when HVI cache cold)',
                'U.S. Census Bureau ACS 5-year estimates',
                'EPA Urban Heat Island research (population-density relationship)',
            ],
            'last_updated': datetime.now().isoformat(),
        }

        set_in_persistent_cache(cache_key, assessment, self.cache_duration)
        logger.info(f"Generated strategic heat assessment for {county_name}")

        return assessment

    def _get_baseline_vulnerability(self, county_name: str) -> float:
        """
        Derive baseline heat vulnerability for a Wisconsin county.

        Preferred source: Wisconsin DHS Heat Vulnerability Index (HVI),
        a state-published Census block-group composite of environmental,
        health, population, and socioeconomic sub-indices.  CARA's
        scheduler refreshes the HVI cache from the DHS ArcGIS MapServer
        quarterly; see utils/wi_dhs_hvi.py for details.

        Fallback (when HVI cache is unpopulated): an unweighted mean of
        three CDC SVI 2022 themes that the heat-vulnerability literature
        treats as most predictive (socioeconomic, housing/transportation,
        household composition).

        Output is clamped to [0.3, 0.85] in both branches so downstream
        composite-score math sees the same value range whether the HVI
        cache is hot or cold.
        """
        try:
            from utils.wi_dhs_hvi import get_hvi_data
            hvi = get_hvi_data(county_name)
            if hvi and hvi.get('vulnerability_score') is not None:
                return max(0.3, min(0.85, float(hvi['vulnerability_score'])))
        except Exception as e:
            logger.warning(f"HVI fetch failed for {county_name}: {e}; falling back to SVI")

        try:
            from utils.svi_data import get_svi_data
            svi = get_svi_data(county_name) or {}
            socio = svi.get('socioeconomic', 0.5)
            housing = svi.get('housing_transportation', 0.5)
            household = svi.get('household_composition', 0.5)
        except Exception as e:
            logger.warning(f"SVI fetch failed for {county_name}: {e}; using statewide median 0.5")
            socio = housing = household = 0.5

        raw = (socio + housing + household) / 3.0
        return max(0.3, min(0.85, raw))

    def _calculate_climate_projections(self, baseline: float) -> float:
        """Calculate climate change impact on heat risk (2025-2050 projections)."""
        temp_impact = self.climate_projections['temperature_increase']['annual_avg'] / 10.0
        frequency_impact = (self.climate_projections['frequency_changes']['days_above_90f'] - 1.0) / 4.0
        duration_impact = (self.climate_projections['duration_changes']['heat_wave_length'] - 1.0) / 2.0

        climate_factor = (
            temp_impact * 0.4
            + frequency_impact * 0.35
            + duration_impact * 0.25
        )
        return min(0.8, baseline * (1 + climate_factor))

    def _calculate_urban_heat_island(self, county_name: str) -> float:
        """
        Derive an urban-heat-island amplification factor (degrees F) from
        Census ACS county population.

        Replaces the previous hand-keyed 11-city dictionary plus 10-entry
        county-to-city mapping with a documented continuous relationship.
        EPA Urban Heat Island research and Oke (1973) / Imhoff et al. (2010)
        establish that UHI intensity scales with urban population (the
        underlying relationship is log-linear; a simple linear proxy is
        used here, calibrated so the smallest WI counties produce ~0.5 F
        and the largest (Milwaukee) reproduce the previously published
        ~7 F estimate).  Output is continuous, county-specific, and
        traceable back to a single Census ACS field.

        Output range:
            small rural counties (population <  10,000): 0.5 degrees F
            mid-size counties:                           scaled linearly
            largest counties     (population > 900,000): 7.0 degrees F
        """
        try:
            from utils.census_data_loader import wisconsin_census
            population = wisconsin_census.get_county_population(county_name) or 80000
        except Exception as e:
            logger.warning(f"Census population fetch failed for {county_name}: {e}; using WI median 80000")
            population = 80000

        # Continuous derivation: ~0.5 F at 10k population up to ~7.0 F at 950k+
        uhi = 0.5 + 6.5 * min(1.0, max(0.0, (population - 10000) / 940000.0))
        return round(uhi, 1)

    def _calculate_trend_component(self, baseline: float, climate_impact: float) -> float:
        """Calculate long-term trend component based on climate trajectory."""
        trend_multiplier = 1.3  # 30% increase trajectory over planning period
        return min(1.0, (baseline + climate_impact) * trend_multiplier)

    def _assess_infrastructure_vulnerability(self, county_name: str, baseline: float) -> float:
        """
        Assess infrastructure vulnerability to extreme heat.

        Replaces the previous hand-picked urban_counties (+0.2 bonus) and
        rural_high_risk (+0.1 bonus) county lists with continuous Census-ACS
        population-based bumps:
          - Urban-infrastructure bump scales with population up to a cap of
            0.2 (full bump at population >= 500,000).
          - Rural-isolation bump of 0.1 applies when population < 12,000
            (single threshold replaces the 5-county hand list; thresholded
            rather than continuous because the underlying effect is genuinely
            a small-population isolation phenomenon).
        """
        try:
            from utils.census_data_loader import wisconsin_census
            population = wisconsin_census.get_county_population(county_name) or 80000
        except Exception:
            population = 80000

        infra_risk = baseline * 0.8
        infra_risk += 0.2 * min(1.0, population / 500000.0)
        if population < 12000:
            infra_risk += 0.1

        return min(1.0, infra_risk)

    def _get_current_season(self) -> str:
        """Determine current season for seasonal planning."""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'fall'
        else:
            return 'winter'

    def _generate_adaptation_recommendations(self, county_name: str, baseline: float,
                                             climate_impact: float, infrastructure_risk: float) -> List[Dict[str, str]]:
        """Generate strategic heat adaptation recommendations."""
        recommendations = []

        if baseline > 0.6:
            recommendations.extend([
                {
                    'priority': 'high',
                    'category': 'public_health',
                    'action': 'Enhance heat emergency response and community outreach protocols',
                    'timeline': 'year_1',
                    'rationale': 'High baseline vulnerability requires strengthened community-wide response systems',
                },
                {
                    'priority': 'high',
                    'category': 'infrastructure',
                    'action': 'Expand cooling center capacity and accessibility',
                    'timeline': 'year_1_2',
                    'rationale': 'Critical infrastructure gap for high-risk population',
                },
            ])

        if climate_impact > 0.4:
            recommendations.extend([
                {
                    'priority': 'medium',
                    'category': 'climate_adaptation',
                    'action': 'Update heat emergency thresholds for climate change',
                    'timeline': 'year_2',
                    'rationale': 'Climate projections require updated response trigger points',
                },
                {
                    'priority': 'medium',
                    'category': 'capacity_building',
                    'action': 'Train staff on extended heat wave response protocols',
                    'timeline': 'year_2_3',
                    'rationale': 'Projected increase in heat wave duration requires enhanced protocols',
                },
            ])

        if infrastructure_risk > 0.5:
            recommendations.append({
                'priority': 'medium',
                'category': 'infrastructure_resilience',
                'action': 'Assess cooling infrastructure adequacy for climate projections',
                'timeline': 'year_3',
                'rationale': 'Infrastructure planning must account for increased heat exposure',
            })

        current_season = self._get_current_season()
        seasonal_focus = self.seasonal_patterns[current_season]['focus']
        recommendations.append({
            'priority': 'ongoing',
            'category': 'seasonal_preparedness',
            'action': f'Implement {seasonal_focus.replace("_", " ")} strategies',
            'timeline': 'ongoing',
            'rationale': f'Current season requires focus on {seasonal_focus.replace("_", " ")}',
        })

        return recommendations[:6]
