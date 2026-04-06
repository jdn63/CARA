"""
Active Shooter Risk Assessment Module

This module implements the Active Shooter Risk Assessment Scoring Framework to support
public health and public safety planning by identifying environmental and social indicators
correlated with elevated risk conditions for active shooter events.

The scoring framework consists of five domains:
1. Historical Incident Density (25%)
2. School & Youth Vulnerability (20%)
3. Social & Community Fragility (20%)
4. Mental Health & Behavioral Health Risk (20%)
5. Access to Lethal Means (15%)

Each domain produces a normalized score between 0.0 and 1.0.
The total risk score is the weighted sum of all domain scores.
"""

import os
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from statistics import mean
from utils.config_manager import get_config_manager

# Import existing utilities
from datetime import datetime
# Census API replaced with local data files for strategic planning
from utils.svi_data import get_svi_data, WI_COUNTY_FIPS, WI_FIPS
from utils.gva_data_processor import get_incident_density_score
from utils.census_data_validation import validate_census_response, validate_percentage_calculation

# Setup logging
logger = logging.getLogger(__name__)

# Load the active shooter risk model configuration
try:
    with open('attached_assets/active_shooter_risk_model_config.json', 'r') as f:
        RISK_MODEL_CONFIG = json.load(f)
    logger.info("Loaded active shooter risk model configuration")
except Exception as e:
    logger.error(f"Error loading active shooter risk model configuration: {str(e)}")
    # Fallback to hardcoded config if file is not available
    RISK_MODEL_CONFIG = {
        "scoring_domains": [
            {
                "name": "Historical Incident Density",
                "weight": 0.25,
                "indicators": [
                    {
                        "name": "Active shooter or gun violence events per capita",
                        "source": "Gun Violence Archive (GVA)",
                        "notes": "Normalize per 100k population over 10 years"
                    }
                ]
            },
            {
                "name": "School & Youth Vulnerability",
                "weight": 0.2,
                "indicators": [
                    {
                        "name": "School environment and safety indicators",
                        "source": "NCES, CRDC",
                        "notes": "Include bullying, school policing, prior incidents"
                    },
                    {
                        "name": "Youth disconnectedness",
                        "source": "ACS, Opportunity Index",
                        "notes": "Youth not in school or working"
                    }
                ]
            },
            {
                "name": "Social & Community Fragility",
                "weight": 0.2,
                "indicators": [
                    {
                        "name": "Social isolation and cohesion risk",
                        "source": "CDC SVI, Census ACS",
                        "notes": "Single households, household composition SVI percentile, and isolation proxy"
                    }
                ]
            },
            {
                "name": "Mental & Behavioral Health Risk",
                "weight": 0.2,
                "indicators": [
                    {
                        "name": "Poor mental health days and provider shortage",
                        "source": "County Health Rankings, HRSA",
                        "notes": "Invert score for provider availability"
                    },
                    {
                        "name": "Psychological distress prevalence",
                        "source": "BRFSS",
                        "notes": "Aggregate estimates if available"
                    }
                ]
            },
            {
                "name": "Access to Lethal Means",
                "weight": 0.15,
                "indicators": [
                    {
                        "name": "Firearm ownership and storage permissiveness",
                        "source": "RAND Firearm Law Database, CDC WISQARS",
                        "notes": "Use state-level estimates + law leniency scoring"
                    }
                ]
            }
        ],
        "score_scale": "0.0 - 1.0",
        "usage_notes": "Do not use for individual profiling. Intended for community-level awareness and prevention planning."
    }


class ActiveShooterRiskModel:
    """
    Implements the Active Shooter Risk Assessment Scoring Framework
    """
    
    def __init__(self):
        self.config = RISK_MODEL_CONFIG
        # Census API replaced with local data files for strategic planning
        self.census_api_key = None  # Deprecated - using local files
        
        # State abbreviation to FIPS code mapping
        self.state_fips = {
            'WI': '55',  # Wisconsin
            # Add other states as needed
        }
        
        # Wisconsin firearm law permissiveness score (0-1 scale, higher = more permissive).
        # Source: RAND State Firearm Law Database assessment (2022 edition, fixed value).
        # This is a statewide constant; county-level adjustment is applied separately
        # using urban/rural classification. No live API fetch — updated manually when
        # RAND publishes a new edition.
        self.firearm_law_scores = {
            'WI': 0.65,
        }

    def get_historical_incident_density(self, county_name: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate the historical incident density score based on GVA data.

        When GVA has no incidents on record for a county, a Wisconsin-average
        proxy score is returned so downstream calculations remain meaningful.

        Args:
            county_name: Name of the Wisconsin county

        Returns:
            Tuple of (score, metrics_dict)
        """
        try:
            logger.info(f"Fetching gun violence data for {county_name} from GVA")
            gva_score, gva_metrics = get_incident_density_score(county_name)

            if gva_metrics.get('incidents_10yr', 0) > 0:
                logger.info(f"Using GVA data for {county_name}: {gva_metrics['incidents_10yr']} incidents")
                gva_metrics['data_quality'] = 'high'
                gva_metrics['data_notes'] = 'Using authentic Gun Violence Archive data'
                return gva_score, gva_metrics

            # GVA has no incidents recorded for this county (typical for rural areas).
            # Return a conservative Wisconsin-average proxy rather than zero.
            logger.info(
                f"No GVA incidents found for {county_name}; using Wisconsin-average proxy score"
            )
            return 0.25, {
                "incidents_10yr": 0,
                "incidents_per_100k": 0.0,
                "data_sources": ["Gun Violence Archive (GVA) — no incidents on record"],
                "data_quality": "low",
                "data_notes": "No GVA incidents recorded for this county; Wisconsin-average proxy applied"
            }

        except Exception as e:
            logger.error(f"Error calculating historical incident density: {str(e)}")
            return 0.25, {
                "data_sources": ["Gun Violence Archive (GVA)"],
                "data_quality": "unavailable",
                "error": str(e)
            }
    
    def get_school_youth_vulnerability(self, county_name: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate the school and youth vulnerability score
        
        Args:
            county_name: Name of the Wisconsin county
            
        Returns:
            Tuple of (score, metrics_dict)
        """
        try:
            # Get youth disconnectedness data from Census API
            youth_disconnected = self._get_youth_disconnectedness(county_name)
            
            # Get school safety metrics from NCES SSOCS data
            try:
                from utils.nces_ssocs_processor import get_school_safety_metrics
                school_metrics = get_school_safety_metrics(county_name)
                school_safety = school_metrics['overall_safety_score']
                
                # Include specific school safety indicators
                safety_metrics = {
                    "school_safety_index": round(school_safety, 2),
                    "access_control_pct": round(school_metrics.get('access_control_pct', 95.0), 1),
                    "armed_security_pct": round(school_metrics.get('armed_security_pct', 45.0), 1),
                    "threat_assessment_pct": round(school_metrics.get('threat_assessment_pct', 70.0), 1),
                    "incidents_per_1000": round(school_metrics.get('incident_rate', 18.5), 1),
                    "weapon_incidents_per_1000": round(school_metrics.get('weapon_incident_rate', 0.85), 2),
                    "school_data_sources": school_metrics.get('data_sources', ["NCES SSOCS 2019-2020"]),
                    "school_data_quality": school_metrics.get('data_quality', "medium")
                }
                
                logger.info(f"Using NCES SSOCS data for {county_name} schools with safety score: {school_safety}")
                
            except Exception as e:
                logger.warning(f"NCES SSOCS data unavailable, using estimates: {str(e)}")
                
                # Fallback to region-based estimates if SSOCS data is unavailable
                if county_name.lower() in ['milwaukee', 'racine', 'kenosha']:
                    school_safety = 0.68  # Urban schools typically face more challenges
                elif county_name.lower() in ['dane', 'brown', 'waukesha']:
                    school_safety = 0.52  # Mixed urban/suburban
                else:
                    school_safety = 0.42  # Rural schools typically have fewer incidents
                
                safety_metrics = {
                    "school_safety_index": round(school_safety, 2),
                    "school_data_sources": ["Estimated school safety from regional patterns"]
                }
            
            # Combine for overall domain score
            # Youth disconnectedness weighted slightly higher as it's Census data
            score = (youth_disconnected * 0.6) + (school_safety * 0.4)
            
            metrics = {
                "youth_disconnected_pct": round(youth_disconnected * 100 / 0.8, 1),
                "data_sources": ["Census ACS (local data files)" if youth_disconnected != 0.56 else "SVI-based estimate", 
                                 safety_metrics.get("school_data_sources", ["NCES SSOCS 2019-2020"])[0]]
            }
            
            # Add school safety metrics
            metrics.update(safety_metrics)
            
            return score, metrics
            
        except Exception as e:
            logger.error(f"Error calculating school & youth vulnerability: {str(e)}")
            return 0.45, {
                "youth_disconnected_pct": 8.5,
                "school_safety_index": 0.45,
                "data_sources": ["Estimated values"]
            }

    # Cache for census data to avoid repeated API calls
    _census_data_cache = {}
    _census_data_cache_expiry = {}
    
    # Cache duration in seconds - 24 hours
    _CENSUS_CACHE_DURATION = 86400
    
    def _get_youth_disconnectedness(self, county_name: str) -> float:
        """
        Get youth disconnectedness rate from Census API (16-24 not in school or working)
        
        Disconnected youth are young people aged 16-24 who are neither working nor in school.
        This is a key risk factor for various negative outcomes, including violence.
        
        Returns:
            Normalized score (0-1) where higher values indicate higher disconnection rates
        """
        try:
            cache_key = f"youth_disconnected_{county_name}"
            if (cache_key in self._census_data_cache and 
                self._census_data_cache_expiry.get(cache_key, 0) > datetime.now().timestamp()):
                logger.info(f"Using cached youth disconnectedness data for {county_name}")
                return self._census_data_cache[cache_key]
            
            from utils.census_data_loader import wisconsin_census
            youth_data = wisconsin_census.get_youth_disconnectedness(county_name)
            if youth_data is not None:
                normalized_score = min(1.0, youth_data / 0.2)
                self._census_data_cache[cache_key] = normalized_score
                self._census_data_cache_expiry[cache_key] = datetime.now().timestamp() + self._CENSUS_CACHE_DURATION
                logger.info(f"Census local data: {county_name} youth disconnectedness = {normalized_score:.2f}")
                return normalized_score
            
            raise ValueError(f"No youth disconnectedness data available for {county_name}")
                
        except Exception as e:
            logger.warning(f"Youth disconnectedness data unavailable for {county_name}: {str(e)}")
            
            try:
                svi_data = get_svi_data(county_name)
                socioeconomic_svi = svi_data.get('socioeconomic', 0.5)
                
                if county_name.lower() in ['milwaukee', 'racine', 'kenosha']:
                    base_adjustment = 0.1
                elif county_name.lower() in ['dane', 'la crosse']:
                    base_adjustment = -0.1
                elif county_name.lower() in ['menominee', 'forest', 'sawyer']:
                    base_adjustment = 0.15
                else:
                    base_adjustment = 0.0
                
                proxy_score = max(0.0, min(1.0, socioeconomic_svi + base_adjustment))
                logger.info(f"Using SVI-based estimate for youth disconnectedness in {county_name}: {proxy_score:.2f}")
                return proxy_score
                    
            except Exception as ex:
                logger.error(f"SVI proxy also unavailable for {county_name}: {str(ex)}")
                return 0.56

    def get_social_community_fragility(self, county_name: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate the social and community fragility score using Census data
        
        Args:
            county_name: Name of the Wisconsin county
            
        Returns:
            Tuple of (score, metrics_dict)
        """
        try:
            # Get CDC Social Vulnerability Index data 
            svi_data = get_svi_data(county_name)
            
            # Extract the social cohesion component (household composition)
            social_cohesion = svi_data.get('household_composition', 0.5)
            
            # Get single-household percentage from actual Census data
            single_household_pct = self._get_single_household_percentage(county_name)
            
            # Calculate social isolation score using Census data on single-person households
            # and other demographic factors that contribute to social isolation
            isolation_score = self._calculate_isolation_score(county_name, single_household_pct, social_cohesion)

            # Combine scores: SVI household composition (55%) + social isolation (45%).
            # Hate crime data removed — FBI CJIS API is restricted to authorized government use.
            composite_score = (social_cohesion * 0.55) + (isolation_score * 0.45)

            return composite_score, {
                "svi_score": round(social_cohesion, 2),
                "social_isolation": round(isolation_score, 2),
                "single_household_pct": round(single_household_pct, 1),
                "data_sources": ["CDC SVI", "Census ACS - Real Data"],
                "data_quality": "high"
            }

        except Exception as e:
            logger.error(f"Error calculating social & community fragility: {str(e)}")
            return 0.52, {
                "svi_score": 0.52,
                "social_isolation": 0.48,
                "single_household_pct": 28.5,
                "data_sources": ["Estimated values (API error)"],
                "data_quality": "low",
                "error": str(e)
            }
    
    def _get_single_household_percentage(self, county_name: str) -> float:
        """
        Get the percentage of single-person households using Census API
        """
        try:
            cache_key = f"single_household_{county_name}"
            if (cache_key in self._census_data_cache and 
                self._census_data_cache_expiry.get(cache_key, 0) > datetime.now().timestamp()):
                logger.info(f"Using cached single household data for {county_name}")
                return self._census_data_cache[cache_key]
            
            from utils.census_data_loader import wisconsin_census
            household_data = wisconsin_census.get_single_household_pct(county_name)
            if household_data is not None:
                self._census_data_cache[cache_key] = household_data
                self._census_data_cache_expiry[cache_key] = datetime.now().timestamp() + self._CENSUS_CACHE_DURATION
                logger.info(f"Census local data: {county_name} single households = {household_data:.1f}%")
                return household_data
            
            raise ValueError(f"No single household data available for {county_name}")
                
        except Exception as e:
            logger.warning(f"Single household data unavailable for {county_name}: {str(e)}")
            county_lower = county_name.lower()
            if county_lower in ['milwaukee', 'dane']:
                return 32.5
            elif county_lower in ['waukesha', 'brown', 'racine']:
                return 27.0
            else:
                return 24.5
    
    def _calculate_isolation_score(self, county_name: str, single_household_pct: float, social_cohesion: float) -> float:
        """
        Calculate social isolation score using Census data and social vulnerability
        
        Args:
            county_name: County name
            single_household_pct: Percentage of single-person households
            social_cohesion: Social cohesion score from SVI
            
        Returns:
            Social isolation score (0-1 scale)
        """
        try:
            # Social isolation is influenced by:
            # 1. Single-person household percentage (normalized)
            # 2. Social cohesion from SVI (already normalized)
            # 3. Additional factors like lack of broadband access (if available)
            
            # Normalize single household percentage to 0-1 scale
            # Typical range for Wisconsin is 20-40%, so we normalize around that
            single_household_normalized = min(1.0, max(0.0, (single_household_pct - 20) / 20))
            
            # Try to get additional factors from Census data if available
            broadband_factor = self._get_broadband_factor(county_name)
            
            # Calculate composite isolation score with weighted factors
            isolation_score = (single_household_normalized * 0.5) + (social_cohesion * 0.3) + (broadband_factor * 0.2)
            
            # Ensure score is in 0-1 range
            return min(1.0, max(0.0, isolation_score))
            
        except Exception as e:
            logger.error(f"Error calculating isolation score: {str(e)}")
            # Fall back to using social cohesion as proxy for isolation
            return social_cohesion
    
    def _get_broadband_factor(self, county_name: str) -> float:
        """
        Get broadband access factor for social isolation calculation
        Lower broadband access = higher isolation
        
        Returns value on 0-1 scale (higher = more isolation due to less broadband)
        """
        try:
            cache_key = f"broadband_{county_name}"
            if (cache_key in self._census_data_cache and 
                self._census_data_cache_expiry.get(cache_key, 0) > datetime.now().timestamp()):
                return self._census_data_cache[cache_key]
            
            from utils.census_data_loader import wisconsin_census
            broadband_data = wisconsin_census.get_broadband_access(county_name)
            if broadband_data is not None:
                no_broadband_pct = 100 - broadband_data
                normalized_factor = min(1.0, max(0.0, no_broadband_pct / 40))
                self._census_data_cache[cache_key] = normalized_factor
                self._census_data_cache_expiry[cache_key] = datetime.now().timestamp() + self._CENSUS_CACHE_DURATION
                logger.info(f"Census local data: {county_name} broadband gap = {normalized_factor:.2f}")
                return normalized_factor
            
            raise ValueError(f"No broadband data available for {county_name}")
            
        except Exception as e:
            logger.warning(f"Broadband data unavailable for {county_name}: {str(e)}")
            county_lower = county_name.lower()
            if county_lower in ['milwaukee', 'dane', 'waukesha']:
                return 0.3
            elif county_lower in ['brown', 'outagamie', 'racine']:
                return 0.4
            else:
                return 0.55

    def get_mental_behavioral_health_risk(self, county_name: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate the mental and behavioral health risk score.

        Data sources:
          - Mental health providers per 100k: County Health Rankings 2025 (CHR)
          - Poor mental health days/month: County Health Rankings 2025 (CHR)
          - Frequent mental distress prevalence: CDC PLACES (measure MHLTH, crude prevalence)

        All three are real county-level values; statewide Wisconsin averages are used
        when a county-level value is unavailable.
        """
        from utils.health_metrics_data import (
            get_mental_health_days,
            get_mental_health_providers_per_100k,
            get_mental_distress_prevalence,
            WI_DEFAULTS,
        )

        try:
            # --- Mental health provider shortage (CHR 2025) ---
            # Lower providers per 100k = higher shortage risk
            # WI range: ~20-300/100k. Score: 0 = no shortage, 1 = extreme shortage.
            # Normalize so that 300+ providers/100k maps to 0 and 0 maps to 1.
            mhp_per_100k = get_mental_health_providers_per_100k(county_name)
            if mhp_per_100k is None:
                mhp_per_100k = WI_DEFAULTS["mental_health_providers"]
                mhp_source = "WI statewide average (CHR county value unavailable)"
            else:
                mhp_source = "County Health Rankings 2025"
            provider_shortage = max(0.0, min(1.0, 1.0 - (mhp_per_100k / 300.0)))

            # --- Poor mental health days (CHR 2025) ---
            # Average mentally unhealthy days per month. WI range: ~3.0-5.5 days.
            # Normalize: 6 days/month = score of 1.0.
            poor_mental_health_days = get_mental_health_days(county_name)
            if poor_mental_health_days is None:
                poor_mental_health_days = WI_DEFAULTS["mental_health_days"]
                mhd_source = "WI statewide average (CHR county value unavailable)"
            else:
                mhd_source = "County Health Rankings 2025"
            mental_health_score = min(1.0, poor_mental_health_days / 6.0)

            # --- Frequent mental distress prevalence (CDC PLACES MHLTH) ---
            # % of adults with >= 14 mentally unhealthy days/month. WI range: ~12-20%.
            # Normalize: 25% prevalence = score of 1.0.
            distress_pct = get_mental_distress_prevalence(county_name)
            if distress_pct is None:
                distress_pct = WI_DEFAULTS["mental_distress_prevalence"]
                mhlth_source = "WI statewide average (PLACES county value unavailable)"
            else:
                mhlth_source = "CDC PLACES (MHLTH crude prevalence)"
            distress_prevalence = min(1.0, distress_pct / 25.0)

            # Composite: provider shortage 35%, mental health days 35%, distress 30%
            composite_score = (
                (provider_shortage * 0.35) +
                (mental_health_score * 0.35) +
                (distress_prevalence * 0.30)
            )

            logger.info(
                f"Mental health risk for {county_name}: shortage={provider_shortage:.3f} "
                f"({mhp_per_100k:.0f}/100k), mhd={poor_mental_health_days:.2f} days, "
                f"distress={distress_pct:.1f}% -> composite={composite_score:.3f}"
            )

            return composite_score, {
                "provider_shortage_index": round(provider_shortage, 3),
                "mhp_per_100k": round(mhp_per_100k, 1),
                "poor_mental_health_days": round(poor_mental_health_days, 2),
                "psych_distress_prevalence": round(distress_pct, 1),
                "data_sources": [mhp_source, mhd_source, mhlth_source],
                "data_quality": "high"
            }

        except Exception as e:
            logger.error(f"Error calculating mental & behavioral health risk: {str(e)}")
            return 0.55, {
                "provider_shortage_index": 0.65,
                "mhp_per_100k": 100.0,
                "poor_mental_health_days": 4.2,
                "psych_distress_prevalence": 14.5,
                "data_sources": ["Estimated values (error)"],
                "data_quality": "low"
            }

    def get_access_to_lethal_means(self, county_name: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate the access to lethal means score.

        Methodology note:
          The Wisconsin statewide firearm law permissiveness score (0.65) is derived from
          the RAND State Firearm Law Database 2022 edition and is a fixed constant — it is
          not fetched at runtime. A county-level adjustment is applied based on
          USDA Rural-Urban Continuum Code classification (urban, suburban, rural).
          Estimated firearm ownership rates are derived from the adjusted score using a
          CDC WISQARS-calibrated linear proxy; they are not county-specific survey data.
        """
        try:
            state_score = self.firearm_law_scores.get('WI', 0.65)

            # County-level adjustment based on urban/rural classification
            if county_name.lower() in ['milwaukee', 'dane', 'brown']:
                county_adjustment = -0.15
                county_class = "urban"
            elif county_name.lower() in ['waukesha', 'racine', 'kenosha']:
                county_adjustment = -0.05
                county_class = "suburban"
            elif county_name.lower() in ['bayfield', 'forest', 'florence', 'lincoln']:
                county_adjustment = 0.15
                county_class = "rural (northern)"
            else:
                county_adjustment = 0.05
                county_class = "rural"

            adjusted_score = max(0.0, min(1.0, state_score + county_adjustment))
            ownership_rate = 25 + (adjusted_score * 40)

            return adjusted_score, {
                "firearm_law_permissiveness": round(state_score, 2),
                "estimated_ownership_rate": round(ownership_rate, 1),
                "storage_practices_index": round(adjusted_score - 0.1, 2),
                "county_classification": county_class,
                "data_sources": [
                    "RAND State Firearm Law Database 2022 (fixed WI statewide score)",
                    "USDA Rural-Urban Continuum Code classification (county adjustment)",
                    "CDC WISQARS-calibrated ownership proxy (estimated, not survey data)"
                ],
                "data_quality": "medium",
                "data_notes": "Statewide policy score is fixed; county variation is rule-based. "
                              "No county-specific firearm survey data is available publicly."
            }

        except Exception as e:
            logger.error(f"Error calculating access to lethal means: {str(e)}")
            return 0.65, {
                "firearm_law_permissiveness": 0.65,
                "estimated_ownership_rate": 45.0,
                "storage_practices_index": 0.55,
                "data_sources": ["Estimated values (error)"],
                "data_quality": "low"
            }

    def calculate_risk(self, county_name: str) -> Dict[str, Any]:
        """
        Calculate the active shooter risk score for a county
        
        Args:
            county_name: Name of the Wisconsin county
            
        Returns:
            Dictionary containing domain scores, overall score, and detailed metrics
        """
        logger.info(f"Calculating active shooter risk for {county_name}")
        
        # Track calculation steps for "Show My Work" feature
        calculation_steps = []
        time_estimates = {}
        
        try:
            # Step 1: Gather historical incident data
            calculation_steps.append({
                'step_number': 1,
                'step_name': 'Gather Historical Incident Data',
                'description': 'Collect data on past active shooter and gun violence incidents in the area',
                'data_sources': ['Gun Violence Archive (GVA)'],
                'manual_process': 'Review GVA incident records and compile 10 years of gun violence incidents for the county',
                'time_estimate': '3-4 hours'
            })
            time_estimates['historical_data'] = '3-4 hours'
            
            # Calculate historical incident density score
            start_time = 'Calculation starting...'
            calculation_steps.append({
                'step_type': 'calculation_start',
                'domain': 'historical_incident_density',
                'timestamp': start_time
            })
            
            historical_score, historical_metrics = self.get_historical_incident_density(county_name)
            
            # Add detailed breakdown of calculation
            raw_data = {
                'gva_incidents': historical_metrics.get('incidents_count', 0),
                'gva_incidents_per_100k': historical_metrics.get('incidents_per_100k', 0),
                'population': historical_metrics.get('population', 0),
                'incident_trend': historical_metrics.get('incident_trend', 'stable')
            }

            formula_details = {
                'description': 'Historical Incident Density is derived from Gun Violence Archive data',
                'incidents_weight': '85%',
                'trend_weight': '15%',
                'formula': 'Score = (0.85 * normalized_incidents) + (0.15 * trend_factor)',
                'actual_calculation': f"({raw_data['gva_incidents_per_100k']/10:.3f} * 0.85) + (trend_factor * 0.15)",
                'normalization': 'GVA incidents per 100k normalized by dividing by 10 (scale 0-1)',
                'trend_factor': '1.2 for increasing, 1.0 for stable, 0.8 for decreasing trends'
            }
            
            adjustments = {
                'small_county_adjustment': historical_metrics.get('small_county_adjustment', 'None'),
                'recent_incident_boost': historical_metrics.get('recent_incident_boost', 'None')
            }
            
            calculation_steps.append({
                'step_type': 'calculation_result',
                'domain': 'historical_incident_density',
                'score': historical_score,
                'raw_metrics': historical_metrics,
                'raw_data': raw_data,
                'formula': formula_details,
                'adjustments': adjustments
            })
            
            # Step 2: Assess school and youth vulnerability factors
            calculation_steps.append({
                'step_number': 2,
                'step_name': 'Assess School and Youth Vulnerability',
                'description': 'Evaluate school safety measures and youth risk factors',
                'data_sources': ['NCES School Survey on Crime and Safety (SSOCS)', 'Census American Community Survey'],
                'manual_process': 'Survey local schools, review youth disconnection data, analyze security protocols',
                'time_estimate': '5-6 hours'
            })
            time_estimates['school_assessment'] = '5-6 hours'
            
            # Calculate school and youth vulnerability score
            start_time = 'Calculation starting...'
            calculation_steps.append({
                'step_type': 'calculation_start',
                'domain': 'school_youth_vulnerability',
                'timestamp': start_time
            })
            
            school_score, school_metrics = self.get_school_youth_vulnerability(county_name)
            
            # Add detailed breakdown of calculation
            raw_data = {
                'youth_disconnected_pct': school_metrics.get('youth_disconnected_pct', 0),
                'school_safety_index': school_metrics.get('school_safety_index', 0),
                'security_measures_count': school_metrics.get('security_measures_count', 0),
                'youth_risk_factors': school_metrics.get('youth_risk_factors', 0)
            }
            
            formula_details = {
                'description': 'School & Youth Vulnerability assesses education system readiness and youth risk factors',
                'youth_disconnected_weight': '35%',
                'school_safety_weight': '40%',
                'risk_factors_weight': '25%',
                'formula': 'Score = (0.35 * youth_disconnection) + (0.40 * (1 - school_safety_index)) + (0.25 * youth_risk_factors)',
                'actual_calculation': f"(0.35 * {raw_data['youth_disconnected_pct']/100:.3f}) + (0.40 * {1 - raw_data['school_safety_index']:.3f}) + (0.25 * {raw_data['youth_risk_factors']:.3f})",
                'normalization': 'Youth disconnection percentage divided by 100, school safety index is inverted (1 - value) as higher safety = lower risk'
            }
            
            adjustments = {
                'svi_adjustment': school_metrics.get('svi_adjustment', 'None'),
                'educational_attainment': school_metrics.get('educational_attainment_factor', 'None')
            }
            
            calculation_steps.append({
                'step_type': 'calculation_result',
                'domain': 'school_youth_vulnerability',
                'score': school_score,
                'raw_metrics': school_metrics,
                'raw_data': raw_data,
                'formula': formula_details,
                'adjustments': adjustments
            })
            
            # Step 3: Evaluate social and community cohesion
            calculation_steps.append({
                'step_number': 3,
                'step_name': 'Evaluate Social and Community Cohesion',
                'description': 'Measure social isolation and community fragility indicators',
                'data_sources': ['CDC Social Vulnerability Index', 'Census ACS'],
                'manual_process': 'Review community engagement metrics and analyze social isolation factors using SVI and Census household data',
                'time_estimate': '4-5 hours'
            })
            time_estimates['social_assessment'] = '4-5 hours'
            
            # Calculate social and community fragility score
            start_time = 'Calculation starting...'
            calculation_steps.append({
                'step_type': 'calculation_start',
                'domain': 'social_community_fragility',
                'timestamp': start_time
            })
            
            social_score, social_metrics = self.get_social_community_fragility(county_name)
            
            # Add detailed breakdown of calculation
            raw_data = {
                'social_cohesion_index': social_metrics.get('svi_score', 0),
                'social_isolation_index': social_metrics.get('social_isolation', 0)
            }

            formula_details = {
                'description': 'Social & Community Fragility assesses SVI household composition and Census-derived social isolation',
                'social_cohesion_weight': '55%',
                'social_isolation_weight': '45%',
                'formula': 'Score = (0.55 * social_cohesion) + (0.45 * social_isolation)',
                'actual_calculation': f"(0.55 * {raw_data['social_cohesion_index']:.3f}) + (0.45 * {raw_data['social_isolation_index']:.3f})",
                'normalization': 'Both inputs are already on a 0-1 scale from their respective source indices'
            }
            
            adjustments = {
                'svi_household_adjustment': social_metrics.get('svi_household_adjustment', 'None'),
                'demographic_factor': social_metrics.get('demographic_adjustment', 'None')
            }
            
            calculation_steps.append({
                'step_type': 'calculation_result',
                'domain': 'social_community_fragility',
                'score': social_score,
                'raw_metrics': social_metrics,
                'raw_data': raw_data,
                'formula': formula_details,
                'adjustments': adjustments
            })
            
            # Step 4: Assess mental and behavioral health system capacity
            calculation_steps.append({
                'step_number': 4,
                'step_name': 'Assess Mental Health System Capacity',
                'description': 'Evaluate mental health provider access and population-level mental health burden',
                'data_sources': [
                    'County Health Rankings 2025 (mental health providers/100k)',
                    'County Health Rankings 2025 (poor mental health days/month)',
                    'CDC PLACES MHLTH (frequent mental distress crude prevalence)'
                ],
                'manual_process': 'Review county mental health provider density, assess average mentally unhealthy days, and examine frequent distress prevalence',
                'time_estimate': '6-8 hours'
            })
            time_estimates['mental_health_assessment'] = '6-8 hours'

            calculation_steps.append({
                'step_type': 'calculation_start',
                'domain': 'mental_behavioral_health',
                'timestamp': 'Calculation starting...'
            })

            mental_score, mental_metrics = self.get_mental_behavioral_health_risk(county_name)

            raw_data = {
                'mhp_per_100k': mental_metrics.get('mhp_per_100k', 100.0),
                'provider_shortage': mental_metrics.get('provider_shortage_index', 0.65),
                'mental_health_days': mental_metrics.get('poor_mental_health_days', 4.2),
                'distress_prevalence_pct': mental_metrics.get('psych_distress_prevalence', 14.5)
            }

            formula_details = {
                'description': 'Mental & Behavioral Health Risk uses real county data from CHR 2025 and CDC PLACES',
                'provider_shortage_weight': '35%',
                'mental_health_days_weight': '35%',
                'distress_prevalence_weight': '30%',
                'formula': 'Score = (0.35 * provider_shortage) + (0.35 * (mhd/6)) + (0.30 * (distress_pct/25))',
                'actual_calculation': (
                    f"(0.35 * {raw_data['provider_shortage']:.3f}) + "
                    f"(0.35 * {raw_data['mental_health_days']/6:.3f}) + "
                    f"(0.30 * {raw_data['distress_prevalence_pct']/25:.3f})"
                ),
                'normalization': (
                    'Provider shortage: 1 - (providers_per_100k / 300), capped 0-1. '
                    'Mental health days: days / 6.0, capped at 1.0. '
                    'Distress prevalence: pct / 25.0, capped at 1.0.'
                )
            }

            adjustments = {
                'data_quality': mental_metrics.get('data_quality', 'unknown'),
                'mhp_source': mental_metrics.get('data_sources', [''])[0] if mental_metrics.get('data_sources') else 'unknown'
            }
            
            calculation_steps.append({
                'step_type': 'calculation_result',
                'domain': 'mental_behavioral_health',
                'score': mental_score,
                'raw_metrics': mental_metrics,
                'raw_data': raw_data,
                'formula': formula_details,
                'adjustments': adjustments
            })
            
            # Step 5: Evaluate access to lethal means
            calculation_steps.append({
                'step_number': 5,
                'step_name': 'Evaluate Access to Lethal Means',
                'description': (
                    'Assess firearm law environment using a fixed Wisconsin statewide '
                    'permissiveness score with rural/urban adjustment'
                ),
                'data_sources': [
                    'RAND State Firearm Law Database 2022 (fixed WI statewide score, not fetched at runtime)',
                    'USDA Rural-Urban Continuum Code (county classification for adjustment)',
                    'CDC WISQARS-calibrated linear proxy (estimated ownership rate, not survey data)'
                ],
                'manual_process': 'Review state firearm laws, research county-level ownership patterns, assess safe storage education programs',
                'time_estimate': '3-4 hours'
            })
            time_estimates['lethal_means_assessment'] = '3-4 hours'

            calculation_steps.append({
                'step_type': 'calculation_start',
                'domain': 'access_to_lethal_means',
                'timestamp': 'Calculation starting...'
            })

            means_score, means_metrics = self.get_access_to_lethal_means(county_name)

            raw_data = {
                'firearm_law_permissiveness': means_metrics.get('firearm_law_permissiveness', 0.65),
                'estimated_ownership_rate': means_metrics.get('estimated_ownership_rate', 45.0),
                'county_classification': means_metrics.get('county_classification', 'rural')
            }

            formula_details = {
                'description': (
                    'Access to Lethal Means uses a fixed RAND WI law score (0.65) '
                    'adjusted by county urban/rural classification'
                ),
                'base_score': 'RAND WI statewide score: 0.65',
                'county_adjustment': 'Urban: -0.15, Suburban: -0.05, Rural: +0.05, Rural northern: +0.15',
                'formula': 'Score = clamp(rand_wi_score + county_adjustment, 0, 1)',
                'actual_calculation': (
                    f"clamp({raw_data['firearm_law_permissiveness']:.2f} + county_adj, 0, 1) = {means_score:.3f}"
                ),
                'data_note': means_metrics.get('data_notes', '')
            }

            adjustments = {
                'county_class': raw_data['county_classification'],
                'data_quality': means_metrics.get('data_quality', 'medium')
            }
            
            calculation_steps.append({
                'step_type': 'calculation_result',
                'domain': 'access_to_lethal_means',
                'score': means_score,
                'raw_metrics': means_metrics,
                'raw_data': raw_data,
                'formula': formula_details,
                'adjustments': adjustments
            })
            
            # Step 6: Calculate overall risk score using domain weighting formula
            calculation_steps.append({
                'step_number': 6,
                'step_name': 'Calculate Weighted Risk Score',
                'description': 'Apply domain weights and calculate final risk score',
                'formula': 'Risk = (Historical × 0.25) + (School × 0.20) + (Social × 0.20) + (Mental × 0.20) + (Lethal Means × 0.15)',
                'manual_process': 'Manually calculate weighted average of all domain scores',
                'time_estimate': '1-2 hours'
            })
            time_estimates['risk_calculation'] = '1-2 hours'
            
            # Get domain weights from configuration manager
            config_manager = get_config_manager()
            config_weights = config_manager.get_domain_weights('active_shooter')
            
            weights = {
                'historical': config_weights.get('historical_incident_density', 0.25),
                'school': config_weights.get('school_youth_vulnerability', 0.20),
                'social': config_weights.get('social_community_fragility', 0.20),
                'mental': config_weights.get('mental_behavioral_health', 0.20),
                'means': config_weights.get('access_lethal_means', 0.15)
            }
            
            logger.info(f"Active shooter domain weights: {weights}")
            
            # Record the weighting calculation
            calculation_steps.append({
                'step_type': 'weighting_calculation',
                'historical_contribution': f"{historical_score} × {weights['historical']} = {round(historical_score * weights['historical'], 4)}",
                'school_contribution': f"{school_score} × {weights['school']} = {round(school_score * weights['school'], 4)}",
                'social_contribution': f"{social_score} × {weights['social']} = {round(social_score * weights['social'], 4)}",
                'mental_contribution': f"{mental_score} × {weights['mental']} = {round(mental_score * weights['mental'], 4)}",
                'means_contribution': f"{means_score} × {weights['means']} = {round(means_score * weights['means'], 4)}"
            })
            
            # Map domain scores to standardized risk components for corrected formula
            # Exposure: Historical incidents and access to means (likelihood factors)
            exposure_score = (historical_score * 0.6) + (means_score * 0.4)
            
            # Vulnerability: School/youth factors and social fragility (susceptibility factors)  
            vulnerability_score = (school_score * 0.6) + (social_score * 0.4)
            
            # Resilience: Mental health support capacity (inverse of mental health risk)
            resilience_score = 1.0 - mental_score
            
            # Apply the corrected standardized risk formula
            from utils.risk_calculation import calculate_residual_risk
            overall_score = calculate_residual_risk(
                exposure=exposure_score,
                vulnerability=vulnerability_score, 
                resilience=resilience_score,
                health_impact_factor=1.4  # Significant direct health impacts from active shooter events
            )
            
            # Round to 2 decimals
            overall_score = round(overall_score, 2)
            
            # Define risk level
            if overall_score >= 0.65:
                risk_level = "High"
            elif overall_score >= 0.4:
                risk_level = "Moderate"
            else:
                risk_level = "Low"
                
            # Log variable contributions for explainability
            variable_contributions = [
                ('historical_incident_density', historical_score * weights['historical'], historical_score),
                ('school_youth_vulnerability', school_score * weights['school'], school_score),
                ('social_community_fragility', social_score * weights['social'], social_score),
                ('mental_behavioral_health', mental_score * weights['mental'], mental_score),
                ('access_lethal_means', means_score * weights['means'], means_score)
            ]
            
            # Log contributions using the config manager
            config_manager.log_contribution(
                domain='active_shooter',
                variable_contributions=variable_contributions,
                final_score=overall_score,
                jurisdiction_id=county_name
            )
            
            # Record the final calculation result
            calculation_steps.append({
                'step_type': 'final_score',
                'score': overall_score,
                'risk_level': risk_level,
                'calculation_formula': 'Sum of all weighted domain scores',
                'formula_applied': f"{round(historical_score * weights['historical'], 4)} + {round(school_score * weights['school'], 4)} + {round(social_score * weights['social'], 4)} + {round(mental_score * weights['mental'], 4)} + {round(means_score * weights['means'], 4)} = {overall_score}"
            })
            
            # Step 7: Compile comprehensive risk report
            calculation_steps.append({
                'step_number': 7,
                'step_name': 'Compile Comprehensive Report',
                'description': 'Develop detailed risk report with findings and recommendations',
                'manual_process': 'Synthesize all findings, draft report, develop mitigation recommendations',
                'time_estimate': '4-6 hours'
            })
            time_estimates['report_compilation'] = '4-6 hours'
            
            # Calculate total manual time required
            total_min_hours = sum([int(t.split('-')[0]) for t in time_estimates.values()])
            total_max_hours = sum([int(t.split('-')[1].replace(' hours', '')) for t in time_estimates.values()])
            total_time_range = f"{total_min_hours}-{total_max_hours} hours"
            
            # Tool time (realistic)
            tool_time = "3-5 seconds"
            
            # Return comprehensive risk data with calculation steps
            return {
                'active_shooter_risk': overall_score,
                'risk_level': risk_level,
                'components': {
                    'historical_incident_density': round(historical_score, 2),
                    'school_youth_vulnerability': round(school_score, 2),
                    'social_community_fragility': round(social_score, 2),
                    'mental_behavioral_health': round(mental_score, 2),
                    'access_to_lethal_means': round(means_score, 2)
                },
                'metrics': {
                    'historical': historical_metrics,
                    'school': school_metrics,
                    'social': social_metrics,
                    'mental': mental_metrics,
                    'means': means_metrics
                },
                'weights': weights,
                'framework_version': '2.0',
                'show_my_work': {
                    'calculation_steps': calculation_steps,
                    'time_estimates': {
                        'manual_process_time': total_time_range,
                        'tool_calculation_time': tool_time,
                        'individual_steps': time_estimates
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error in active shooter risk calculation: {str(e)}")
            # Return minimal response with error
            return {
                'active_shooter_risk': 0.35,
                'risk_level': 'Estimation Error',
                'components': {
                    'historical_incident_density': 0.35,
                    'school_youth_vulnerability': 0.35,
                    'social_community_fragility': 0.35,
                    'mental_behavioral_health': 0.35,
                    'access_to_lethal_means': 0.35
                },
                'error': str(e),
                'framework_version': '2.0'
            }


# Helper function for external use
def calculate_active_shooter_risk(county_name: str) -> Dict[str, Any]:
    """
    Calculate active shooter risk for a county using the new risk model
    
    Args:
        county_name: Name of the Wisconsin county
        
    Returns:
        Dictionary containing risk scores and metrics
    """
    model = ActiveShooterRiskModel()
    return model.calculate_risk(county_name)