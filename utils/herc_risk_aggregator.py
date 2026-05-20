"""
HERC Risk Aggregation Module

This module calculates real risk scores for HERC regions by aggregating
risk data from all constituent jurisdictions within each region.

Includes database-backed caching for instant dashboard loading and
background pre-computation to prevent timeout issues.
"""

import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from statistics import mean, median

from utils.jurisdictions_code import jurisdictions
from utils.jurisdiction_mapping_code import jurisdiction_mapping
from utils.herc_data import get_all_herc_regions
from utils.data_processor import process_risk_data
from utils.config_manager import get_config_manager

logger = logging.getLogger(__name__)

# Cache for HERC region risk data (TTL: 1 hour)
_herc_cache: Dict[str, Dict[str, Any]] = {}
_herc_cache_ttl = 3600  # 1 hour in seconds

# Cache for individual jurisdiction risk data (TTL: 30 minutes)
_jurisdiction_cache: Dict[str, Dict[str, Any]] = {}
_jurisdiction_cache_ttl = 1800  # 30 minutes


def _get_cached_jurisdiction_risk(jurisdiction_id: str) -> Optional[Dict[str, Any]]:
    """Get cached jurisdiction risk data if available and not expired."""
    if jurisdiction_id in _jurisdiction_cache:
        cached = _jurisdiction_cache[jurisdiction_id]
        if time.time() - cached.get('_cached_at', 0) < _jurisdiction_cache_ttl:
            return cached
    return None


_JURISDICTION_CACHE_MAX = 150  # slightly above the total 101-jurisdiction count
_HERC_CACHE_MAX = 10          # only 7 HERC regions; small headroom for reruns


def _evict_oldest(cache: Dict[str, Any], max_size: int) -> None:
    """Remove the oldest entry when the cache exceeds max_size."""
    if len(cache) >= max_size:
        oldest_key = min(cache, key=lambda k: cache[k].get('_cached_at', 0))
        del cache[oldest_key]


def _cache_jurisdiction_risk(jurisdiction_id: str, risk_data: Dict[str, Any]) -> None:
    """Cache jurisdiction risk data, evicting the oldest entry if needed."""
    _evict_oldest(_jurisdiction_cache, _JURISDICTION_CACHE_MAX)
    risk_data['_cached_at'] = time.time()
    _jurisdiction_cache[jurisdiction_id] = risk_data


class HERCRiskAggregator:
    """
    Aggregates risk data for HERC regions from constituent jurisdictions.
    """
    
    def __init__(self):
        self.herc_regions = get_all_herc_regions()
        
    def get_jurisdictions_for_herc_region(self, herc_id: str) -> List[Dict[str, Any]]:
        """
        Get all jurisdictions that belong to a HERC region.
        
        Args:
            herc_id: ID of the HERC region
            
        Returns:
            List of jurisdiction dictionaries
        """
        # Find the HERC region
        region = next((r for r in self.herc_regions if r.get('id') == herc_id), None)
        if not region:
            logger.error(f"HERC region not found: {herc_id}")
            return []
        
        counties = region.get('counties', [])
        region_jurisdictions = []
        
        # Find all jurisdictions that belong to these counties
        for jurisdiction in jurisdictions:
            jurisdiction_id = jurisdiction['id']
            county = jurisdiction_mapping.get(jurisdiction_id)
            
            if county in counties:
                region_jurisdictions.append(jurisdiction)
        
        logger.info(f"Found {len(region_jurisdictions)} jurisdictions in HERC region {herc_id} ({region.get('name')})")
        return region_jurisdictions
    
    def calculate_herc_region_risk(self, herc_id: str) -> Optional[Dict[str, Any]]:
        """
        Calculate aggregated risk scores for a HERC region.
        
        Uses caching to prevent timeout issues from multiple API calls.
        
        Args:
            herc_id: ID of the HERC region
            
        Returns:
            Dictionary containing aggregated risk scores and metrics
        """
        try:
            # Check HERC-level cache first
            if herc_id in _herc_cache:
                cached = _herc_cache[herc_id]
                if time.time() - cached.get('_cached_at', 0) < _herc_cache_ttl:
                    logger.info(f"Returning cached HERC risk data for region {herc_id}")
                    return cached
            
            # Get region info
            region = next((r for r in self.herc_regions if r.get('id') == herc_id), None)
            if not region:
                logger.error(f"HERC region not found: {herc_id}")
                return None
            
            # Get all jurisdictions in this region
            region_jurisdictions = self.get_jurisdictions_for_herc_region(herc_id)
            
            if not region_jurisdictions:
                logger.warning(f"No jurisdictions found for HERC region {herc_id}")
                return None
            
            # Two-stage mean aggregation (review finding H7): group
            # jurisdictions by county, average within each county, then
            # average across unique counties. This ensures every county
            # in the HERC region contributes once to the regional mean
            # regardless of how many local health departments cover it.
            # Prior code averaged across raw jurisdictions, which biased
            # regional scores toward counties with fragmented governance
            # (e.g. Milwaukee County has 10 jurisdictions in the HERC
            # rollup but only one county worth of actual exposure).
            #
            # Each per-domain bucket is keyed by county; we collect
            # jurisdiction-level scores inside each bucket and reduce
            # twice at the end (within-county mean, then across-county
            # mean). Natural-hazard subcomponents and temporal-risk
            # components use the same two-stage approach.
            DOMAINS = (
                'natural_hazards', 'health_metrics', 'active_shooter',
                'extreme_heat', 'air_quality', 'cybersecurity',
                'utilities', 'dam_failure', 'vector_borne_disease',
            )
            NH_COMPONENTS = ('flood', 'tornado', 'winter_storm', 'thunderstorm')
            TEMPORAL_HAZARDS = (
                'flood', 'tornado', 'winter_storm', 'extreme_heat',
                'thunderstorm', 'health', 'active_shooter',
            )
            TEMPORAL_COMPONENTS = ('baseline', 'seasonal', 'trend', 'acute')

            # county -> domain -> list[float]
            domain_by_county: Dict[str, Dict[str, List[float]]] = defaultdict(
                lambda: defaultdict(list)
            )
            # county -> nh_component -> list[float]
            nh_by_county: Dict[str, Dict[str, List[float]]] = defaultdict(
                lambda: defaultdict(list)
            )
            # county -> hazard -> {composite_scores: [], baseline: [], ...}
            temporal_by_county: Dict[str, Dict[str, Dict[str, List[float]]]] = defaultdict(
                lambda: defaultdict(
                    lambda: {k: [] for k in ('composite_scores',) + TEMPORAL_COMPONENTS}
                )
            )
            # county -> list of jurisdiction total_risk_scores
            total_by_county: Dict[str, List[float]] = defaultdict(list)

            successful_calculations = 0

            for jurisdiction in region_jurisdictions:
                try:
                    jurisdiction_id = jurisdiction['id']
                    # Use the canonical county mapping so a jurisdiction's
                    # bucket survives any cosmetic name differences between
                    # jurisdictions_code and herc_data.
                    county = (
                        jurisdiction_mapping.get(jurisdiction_id)
                        or jurisdiction.get('county')
                        or jurisdiction_id  # last-resort: unique key per jurisdiction
                    )

                    # Check jurisdiction cache first
                    cached_data = _get_cached_jurisdiction_risk(jurisdiction_id)
                    if cached_data:
                        risk_data = cached_data.get('risk_data', {})
                        domain_scores = cached_data.get('domain_scores', {})
                    else:
                        risk_data = process_risk_data(jurisdiction_id)
                        domain_scores = {
                            'natural_hazards': risk_data.get('natural_hazards_risk', 0.0),
                            'health_metrics': risk_data.get('health_risk', 0.0),
                            'active_shooter': risk_data.get('active_shooter_risk', 0.0),
                            'extreme_heat': risk_data.get('extreme_heat_risk', 0.0),
                            'air_quality': risk_data.get('air_quality_risk', 0.0),
                            'cybersecurity': risk_data.get('cybersecurity_risk', 0.0),
                            'utilities': risk_data.get('utilities', {}).get('overall', 0.0),
                            'dam_failure': risk_data.get('dam_failure_risk', 0.0),
                            'vector_borne_disease': risk_data.get('vector_borne_disease_risk', 0.0),
                        }

                        # Cache for future use
                        _cache_jurisdiction_risk(jurisdiction_id, {
                            'risk_data': risk_data,
                            'domain_scores': domain_scores
                        })

                    for domain in DOMAINS:
                        domain_by_county[county][domain].append(
                            domain_scores.get(domain, 0.0)
                        )

                    nh_detail = risk_data.get('natural_hazards', {}) or {}
                    for comp in NH_COMPONENTS:
                        nh_by_county[county][comp].append(nh_detail.get(comp, 0.0))

                    temporal_risk_detail = risk_data.get('temporal_risk_detail', {}) or {}
                    for hazard in TEMPORAL_HAZARDS:
                        hazard_temporal = temporal_risk_detail.get(hazard)
                        if isinstance(hazard_temporal, dict):
                            bucket = temporal_by_county[county][hazard]
                            bucket['composite_scores'].append(
                                hazard_temporal.get('composite_score', 0.0)
                            )
                            components = hazard_temporal.get('temporal_components', {}) or {}
                            for comp_key in TEMPORAL_COMPONENTS:
                                bucket[comp_key].append(components.get(comp_key, 0.0))

                    total_by_county[county].append(risk_data.get('total_risk_score', 0.0))
                    successful_calculations += 1

                except Exception as e:
                    logger.warning(f"Failed to calculate risk for jurisdiction {jurisdiction.get('id')}: {e}")
                    continue

            if successful_calculations == 0:
                logger.error(f"No successful risk calculations for HERC region {herc_id}")
                return None

            def _two_stage_mean(by_county: Dict[str, Dict[str, List[float]]],
                                key: str) -> float:
                """Within-county mean, then across-county mean.

                Counties missing the key contribute nothing. Returns 0.0
                when no county has any value for the key (e.g. a domain
                where every jurisdiction failed to populate it).
                """
                county_means = []
                for _county, dmap in by_county.items():
                    vals = dmap.get(key) or []
                    if vals:
                        county_means.append(mean(vals))
                return mean(county_means) if county_means else 0.0

            natural_hazards_avg = _two_stage_mean(domain_by_county, 'natural_hazards')
            health_avg = _two_stage_mean(domain_by_county, 'health_metrics')
            active_shooter_avg = _two_stage_mean(domain_by_county, 'active_shooter')
            extreme_heat_avg = _two_stage_mean(domain_by_county, 'extreme_heat')
            air_quality_avg = _two_stage_mean(domain_by_county, 'air_quality')
            cybersecurity_avg = _two_stage_mean(domain_by_county, 'cybersecurity')
            utilities_avg = _two_stage_mean(domain_by_county, 'utilities')
            dam_failure_avg = _two_stage_mean(domain_by_county, 'dam_failure')
            vector_borne_disease_avg = _two_stage_mean(domain_by_county, 'vector_borne_disease')

            flood_avg = _two_stage_mean(nh_by_county, 'flood')
            tornado_avg = _two_stage_mean(nh_by_county, 'tornado')
            winter_storm_avg = _two_stage_mean(nh_by_county, 'winter_storm')
            thunderstorm_avg = _two_stage_mean(nh_by_county, 'thunderstorm')

            unique_counties_count = len(domain_by_county)
            
            # Get weights configuration for total risk calculation
            config_manager = get_config_manager()
            weights = config_manager.get_overall_weights()
            
            # Calculate regional total risk score from aggregated domain scores
            total_risk = (
                natural_hazards_avg * weights.get('natural_hazards', 0.35) +
                health_avg * weights.get('health_metrics', 0.20) +
                active_shooter_avg * weights.get('active_shooter', 0.15) +
                extreme_heat_avg * weights.get('extreme_heat', 0.15) +
                cybersecurity_avg * weights.get('cybersecurity', 0.15) +
                dam_failure_avg * weights.get('dam_failure', 0.0) +
                vector_borne_disease_avg * weights.get('vector_borne_disease', 0.0)
            )
            
            # Aggregated metrics use the two-stage county mean above so
            # counties with multiple local health departments (e.g.
            # Milwaukee) no longer over-weight the regional rollup.
            aggregated_risk = {
                'herc_id': herc_id,
                'name': region.get('name'),
                'counties': region.get('counties', []),
                'jurisdiction_count': len(region_jurisdictions),
                'unique_counties_count': unique_counties_count,
                'aggregation_method': 'two_stage_county_mean',
                'successful_calculations': successful_calculations,

                # Overall scores - recalculated from aggregated domain scores
                'total_risk_score': round(total_risk, 4),

                # Domain scores (within-county mean, then across-county mean)
                'natural_hazards_risk': natural_hazards_avg,
                'health_risk': health_avg,
                'active_shooter_risk': active_shooter_avg,
                'extreme_heat_risk': extreme_heat_avg,
                'air_quality_risk': air_quality_avg,
                'cybersecurity_risk': cybersecurity_avg,
                'utilities_risk': utilities_avg,
                'dam_failure_risk': dam_failure_avg,
                'vector_borne_disease_risk': vector_borne_disease_avg,

                # Natural hazard components (same two-stage county mean)
                'flood_risk': flood_avg,
                'tornado_risk': tornado_avg,
                'winter_storm_risk': winter_storm_avg,
                'thunderstorm_risk': thunderstorm_avg,

                # Natural hazards breakdown for template
                'natural_hazards': {
                    'flood': flood_avg,
                    'tornado': tornado_avg,
                    'winter_storm': winter_storm_avg,
                    'thunderstorm': thunderstorm_avg,
                }
            }

            # Temporal risk data: two-stage county mean per hazard and
            # per temporal component (baseline / seasonal / trend / acute).
            temporal_risk_data = {}
            for hazard_type in TEMPORAL_HAZARDS:
                # Collect per-county means for each temporal field.
                composite_county_means = []
                component_county_means = {k: [] for k in TEMPORAL_COMPONENTS}
                for _county, hazard_map in temporal_by_county.items():
                    bucket = hazard_map.get(hazard_type)
                    if not bucket or not bucket['composite_scores']:
                        continue
                    composite_county_means.append(mean(bucket['composite_scores']))
                    for comp_key in TEMPORAL_COMPONENTS:
                        if bucket[comp_key]:
                            component_county_means[comp_key].append(
                                mean(bucket[comp_key])
                            )
                if composite_county_means:
                    temporal_risk_data[hazard_type] = {
                        'composite_score': mean(composite_county_means),
                        'temporal_components': {
                            comp_key: (
                                mean(component_county_means[comp_key])
                                if component_county_means[comp_key] else 0.0
                            )
                            for comp_key in TEMPORAL_COMPONENTS
                        },
                    }

            aggregated_risk['temporal_risk_data'] = temporal_risk_data
            
            logger.info(f"Successfully calculated aggregated risk for HERC region {herc_id}: " +
                       f"Total Risk = {aggregated_risk['total_risk_score']:.3f}")
            
            # Cache the HERC region result (evict oldest if cap reached)
            _evict_oldest(_herc_cache, _HERC_CACHE_MAX)
            aggregated_risk['_cached_at'] = time.time()
            _herc_cache[herc_id] = aggregated_risk
            
            return aggregated_risk
            
        except Exception as e:
            logger.error(f"Error calculating HERC region risk for {herc_id}: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None


def get_herc_region_risk(herc_id: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get HERC region risk data.
    
    First checks database cache, then falls back to live calculation if needed.
    
    Args:
        herc_id: ID of the HERC region
        
    Returns:
        Dictionary containing aggregated risk scores
    """
    # Try database cache first
    cached = get_cached_herc_risk(herc_id)
    if cached:
        logger.info(f"Returning database-cached HERC risk data for region {herc_id}")
        return cached
    
    # Fall back to live calculation
    logger.info(f"No cached data for HERC region {herc_id}, calculating live...")
    aggregator = HERCRiskAggregator()
    result = aggregator.calculate_herc_region_risk(herc_id)
    
    # Save to database cache for future requests
    if result:
        save_herc_risk_to_cache(herc_id, result)
    
    return result


def get_cached_herc_risk(herc_id: str, max_age_hours: int = 4) -> Optional[Dict[str, Any]]:
    """
    Get cached HERC risk data from database.
    
    Args:
        herc_id: ID of the HERC region
        max_age_hours: Maximum age of cached data in hours (default: 4)
        
    Returns:
        Cached risk data if available and fresh, None otherwise
    """
    try:
        from core import db
        from models import HERCRiskCache
        from flask import has_app_context
        
        # Only query if we have an app context
        if not has_app_context():
            logger.debug("No app context available for HERC cache query")
            return None
        
        cache_entry = db.session.query(HERCRiskCache).filter_by(
            herc_id=herc_id,
            is_valid=True
        ).first()
        
        if not cache_entry:
            logger.debug(f"No cache entry found for HERC region {herc_id}")
            return None
        
        # Check if cache is fresh enough
        age_hours = cache_entry.age_minutes / 60 if cache_entry.age_minutes else float('inf')
        if age_hours > max_age_hours:
            logger.info(f"Cache for HERC region {herc_id} is stale ({age_hours:.1f}h old)")
            return None
        
        logger.info(f"Found fresh cache for HERC region {herc_id} ({age_hours:.1f}h old)")
        risk_data = dict(cache_entry.risk_data)  # Make a copy
        risk_data['_from_db_cache'] = True
        risk_data['_cache_age_minutes'] = cache_entry.age_minutes
        return risk_data
            
    except Exception as e:
        logger.warning(f"Error reading HERC cache from database: {e}")
        return None


def save_herc_risk_to_cache(herc_id: str, risk_data: Dict[str, Any], 
                            duration_seconds: float = None) -> bool:
    """
    Save HERC risk data to database cache.
    
    Args:
        herc_id: ID of the HERC region
        risk_data: Calculated risk data to cache
        duration_seconds: How long the calculation took
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        from core import db
        from models import HERCRiskCache
        from flask import has_app_context
        
        # Only save if we have an app context
        if not has_app_context():
            logger.debug("No app context available for HERC cache save")
            return False
        
        # Clean up internal cache keys before saving
        clean_data = {k: v for k, v in risk_data.items() 
                     if not k.startswith('_')}
        
        # Check if entry exists
        cache_entry = db.session.query(HERCRiskCache).filter_by(
            herc_id=herc_id
        ).first()
        
        if cache_entry:
            # Update existing entry
            cache_entry.risk_data = clean_data
            cache_entry.calculated_at = datetime.utcnow()
            cache_entry.is_valid = True
            cache_entry.calculation_duration_seconds = duration_seconds
            cache_entry.jurisdiction_count = risk_data.get('jurisdiction_count')
            cache_entry.error_message = None
        else:
            # Create new entry
            cache_entry = HERCRiskCache(
                herc_id=herc_id,
                name=risk_data.get('name', f'HERC Region {herc_id}'),
                risk_data=clean_data,
                calculated_at=datetime.utcnow(),
                is_valid=True,
                calculation_duration_seconds=duration_seconds,
                jurisdiction_count=risk_data.get('jurisdiction_count')
            )
            db.session.add(cache_entry)
        
        db.session.commit()
        logger.info(f"Saved HERC risk data to database cache for region {herc_id}")
        return True
            
    except Exception as e:
        logger.error(f"Error saving HERC cache to database: {e}")
        db.session.rollback()
        return False


def precompute_all_herc_regions() -> Dict[str, Any]:
    """
    Pre-compute risk data for all HERC regions and save to database.
    
    This function is designed to be called by the background scheduler
    to ensure HERC dashboards load instantly.
    
    Returns:
        Dictionary with results for each region
    """
    logger.info("Starting pre-computation of all HERC regions...")
    start_time = time.time()
    
    herc_regions = get_all_herc_regions()
    results = {
        'started_at': datetime.utcnow().isoformat(),
        'regions': {},
        'success_count': 0,
        'error_count': 0
    }
    
    aggregator = HERCRiskAggregator()
    
    for region in herc_regions:
        herc_id = region.get('id')
        region_name = region.get('name', f'Region {herc_id}')
        
        try:
            region_start = time.time()
            logger.info(f"Pre-computing HERC region {herc_id}: {region_name}")
            
            # Calculate risk data (bypassing cache)
            risk_data = aggregator.calculate_herc_region_risk(herc_id)
            
            if risk_data:
                duration = time.time() - region_start
                
                # Save to database
                save_herc_risk_to_cache(herc_id, risk_data, duration)
                
                results['regions'][herc_id] = {
                    'status': 'success',
                    'name': region_name,
                    'duration_seconds': round(duration, 2),
                    'total_risk_score': risk_data.get('total_risk_score')
                }
                results['success_count'] += 1
                logger.info(f"Successfully pre-computed HERC region {herc_id} in {duration:.1f}s")
            else:
                results['regions'][herc_id] = {
                    'status': 'error',
                    'name': region_name,
                    'error': 'Calculation returned None'
                }
                results['error_count'] += 1
                
        except Exception as e:
            logger.error(f"Error pre-computing HERC region {herc_id}: {e}")
            results['regions'][herc_id] = {
                'status': 'error',
                'name': region_name,
                'error': str(e)
            }
            results['error_count'] += 1
    
    total_duration = time.time() - start_time
    results['total_duration_seconds'] = round(total_duration, 2)
    results['finished_at'] = datetime.utcnow().isoformat()
    
    logger.info(f"HERC pre-computation complete: {results['success_count']} success, " +
               f"{results['error_count']} errors in {total_duration:.1f}s")
    
    return results
