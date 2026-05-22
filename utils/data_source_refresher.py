"""
Data Source Refresher - Scheduled jobs to refresh external data at appropriate cadences

This module contains functions called by the scheduler to refresh:
- Annual: CDC SVI, FEMA NRI  
- Weekly: DHS Health Metrics, NWS Forecasts, OpenFEMA data, NOAA Storm Events
- Daily: EPA Air Quality

Each refresh function fetches data from external APIs and stores it in the database cache.
User requests read from this cache only - never hitting external APIs directly.

IMPORTANT: All refresh functions must run within Flask app context for database access.
"""

import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def _get_app():
    """Get Flask app instance for creating app context in background threads."""
    try:
        from main import app
        return app
    except ImportError:
        logger.error("Could not import Flask app from main")
        return None


def refresh_all_cdc_svi() -> Dict[str, Any]:
    """
    Refresh CDC Social Vulnerability Index data for all Wisconsin counties.
    Called annually by scheduler.

    Uses a single bulk API call to fetch all 72 counties at once from the
    CDC/ATSDR SVI 2022 ArcGIS REST API. Falls back to individual per-county
    fetches only if the bulk call fails.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.svi_data import fetch_bulk_svi_data, fetch_live_svi_data, WI_COUNTY_FIPS

        results = {
            'source_type': 'cdc_svi',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': []
        }

        start_time = time.time()
        bulk_data = fetch_bulk_svi_data()
        bulk_duration = time.time() - start_time

        if bulk_data:
            logger.info(f"Bulk SVI fetch returned {len(bulk_data)} counties in {bulk_duration:.1f}s")
            per_county_duration = bulk_duration / max(len(bulk_data), 1)

            for county_name in WI_COUNTY_FIPS.keys():
                try:
                    data = bulk_data.get(county_name)
                    used_fallback = data is None

                    if used_fallback:
                        data = {
                            "county": county_name.title(),
                            "overall": 0.5, "socioeconomic": 0.5,
                            "household_composition": 0.5, "minority_status": 0.5,
                            "housing_transportation": 0.5,
                            "data_source": "statewide_average",
                            "_fallback": True,
                            "_fallback_reason": "County not in bulk response",
                            "last_updated": datetime.utcnow().isoformat()
                        }

                    success = save_cached_data(
                        source_type='cdc_svi',
                        data=data,
                        county_name=county_name,
                        fetch_duration=per_county_duration,
                        api_source='CDC SVI 2022 ArcGIS (bulk)',
                        used_fallback=used_fallback,
                        fallback_reason=data.get('_fallback_reason') if used_fallback else None
                    )

                    if success:
                        if used_fallback:
                            results['fallback'] += 1
                        else:
                            results['success'] += 1
                    else:
                        results['failed'] += 1

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'county': county_name, 'error': str(e)})
                    logger.error(f"Error saving SVI for {county_name}: {e}")
        else:
            logger.warning("Bulk SVI fetch failed, falling back to individual county fetches")
            for county_name in WI_COUNTY_FIPS.keys():
                try:
                    county_start = time.time()
                    data = fetch_live_svi_data(county_name)
                    duration = time.time() - county_start

                    used_fallback = data.get('_fallback', False) or data.get('data_source') == 'statewide_average'
                    fallback_reason = data.get('_fallback_reason', 'Using statewide average') if used_fallback else None

                    success = save_cached_data(
                        source_type='cdc_svi',
                        data=data,
                        county_name=county_name,
                        fetch_duration=duration,
                        api_source='CDC SVI API',
                        used_fallback=used_fallback,
                        fallback_reason=fallback_reason
                    )

                    if success:
                        if used_fallback:
                            results['fallback'] += 1
                        else:
                            results['success'] += 1
                    else:
                        results['failed'] += 1

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'county': county_name, 'error': str(e)})
                    logger.error(f"Error refreshing SVI for {county_name}: {e}")

        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"CDC SVI refresh complete: {results['success']} success, {results['fallback']} fallback, {results['failed']} failed")

        return results


def refresh_all_epa_air_quality() -> Dict[str, Any]:
    """
    Refresh EPA Air Quality data for all Wisconsin counties.
    Called daily by scheduler.
    
    IMPORTANT: Uses fetch_live_air_quality_data to bypass cache and always hit external sources.
    Wraps in app context for database access from background threads.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    
    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.air_quality_data import fetch_live_air_quality_data, WI_COUNTY_COORDINATES
        
        results = {
            'source_type': 'epa_air_quality',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': []
        }
        
        logger.info("Starting EPA Air Quality data refresh for all counties (using live fetch)")
        
        for county_name in WI_COUNTY_COORDINATES.keys():
            try:
                start_time = time.time()
                # Use fetch_live_air_quality_data to bypass cache and hit external sources
                data = fetch_live_air_quality_data(county_name)
                duration = time.time() - start_time
                
                used_fallback = data.get('data_source') == 'statewide_baseline' or data.get('_fallback', False)
                fallback_reason = data.get('_fallback_reason', 'Using statewide baseline') if used_fallback else None
                
                success = save_cached_data(
                    source_type='epa_air_quality',
                    data=data,
                    county_name=county_name,
                    fetch_duration=duration,
                    api_source='EPA AirNow API',
                    used_fallback=used_fallback,
                    fallback_reason=fallback_reason
                )
                
                if success:
                    if used_fallback:
                        results['fallback'] += 1
                    else:
                        results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'county': county_name, 'error': str(e)})
                logger.error(f"Error refreshing air quality for {county_name}: {e}")
        
        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"EPA Air Quality refresh complete: {results['success']} success, {results['fallback']} fallback, {results['failed']} failed")
        
        return results


def refresh_all_dhs_health() -> Dict[str, Any]:
    """
    Refresh DHS Health Metrics for all Wisconsin counties.
    Called weekly by scheduler.
    Wraps in app context for database access from background threads.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    
    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.dhs_data import get_dhs_health_metrics
        from utils.svi_data import WI_COUNTY_FIPS
        
        results = {
            'source_type': 'dhs_health',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': []
        }
        
        logger.info("Starting DHS Health Metrics refresh for all counties")
        
        for county_name in WI_COUNTY_FIPS.keys():
            try:
                start_time = time.time()
                data = get_dhs_health_metrics(county_name)
                duration = time.time() - start_time
                
                used_fallback = data.get('data_source') == 'statewide_average' or data.get('_fallback', False)
                fallback_reason = 'Using statewide average' if used_fallback else None
                
                success = save_cached_data(
                    source_type='dhs_health',
                    data=data,
                    county_name=county_name,
                    fetch_duration=duration,
                    api_source='Wisconsin DHS API',
                    used_fallback=used_fallback,
                    fallback_reason=fallback_reason
                )
                
                if success:
                    if used_fallback:
                        results['fallback'] += 1
                    else:
                        results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'county': county_name, 'error': str(e)})
                logger.error(f"Error refreshing DHS health for {county_name}: {e}")
        
        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"DHS Health refresh complete: {results['success']} success, {results['fallback']} fallback, {results['failed']} failed")
        
        return results


def refresh_all_nws_forecasts() -> Dict[str, Any]:
    """
    Refresh NWS Weather Forecast data for all Wisconsin counties.
    Called weekly by scheduler.
    Wraps in app context for database access from background threads.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    
    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.weather_alerts import get_active_alerts as get_weather_alerts
        from utils.svi_data import WI_COUNTY_FIPS
        
        results = {
            'source_type': 'nws_heat',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': []
        }
        
        logger.info("Starting NWS Forecast refresh for all counties")
        
        for county_name in WI_COUNTY_FIPS.keys():
            try:
                start_time = time.time()
                raw = get_weather_alerts(county_name)
                duration = time.time() - start_time

                # get_active_alerts returns a List[Dict] of active alerts; wrap
                # in a dict envelope so the cache row carries provenance and the
                # freshness reporter can use .get() on the payload.
                if isinstance(raw, list):
                    data = {
                        'active_alerts': raw,
                        'alert_count': len(raw),
                        'data_source': 'nws_api',
                        'fetched_at': datetime.utcnow().isoformat(),
                    }
                    used_fallback = False
                elif isinstance(raw, dict):
                    data = raw
                    used_fallback = data.get('data_source') == 'fallback' or data.get('_fallback', False)
                else:
                    data = {'data_source': 'unknown', 'raw_type': type(raw).__name__}
                    used_fallback = True
                fallback_reason = 'Using fallback data' if used_fallback else None

                success = save_cached_data(
                    source_type='nws_heat',
                    data=data,
                    county_name=county_name,
                    fetch_duration=duration,
                    api_source='NWS API',
                    used_fallback=used_fallback,
                    fallback_reason=fallback_reason
                )
                
                if success:
                    if used_fallback:
                        results['fallback'] += 1
                    else:
                        results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'county': county_name, 'error': str(e)})
                logger.error(f"Error refreshing NWS forecast for {county_name}: {e}")
        
        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"NWS Forecast refresh complete: {results['success']} success, {results['fallback']} fallback, {results['failed']} failed")
        
        return results


def refresh_all_fema_nri() -> Dict[str, Any]:
    """Verify the FEMA National Risk Index static dataset.

    FEMA NRI is published as a static CSV (annual release); there is no live
    REST API to refresh against. Earlier versions of this function called
    FEMARAPTConnector.get_correctional_facilities() and saved the result
    under the fema_nri cache key, which silently overwrote NRI metadata
    with unrelated correctional facility data.

    This implementation does the right thing: it locates the bundled NRI
    CSV (preferring the Wisconsin-filtered census-tract file used by the
    rest of the app), records its modification age, and saves a small
    metadata entry under the fema_nri cache key so the dashboard's data
    freshness panel reflects when the static file was last updated.

    The actual NRI data is still loaded on demand by
    utils.data_processor.load_nri_data() / utils.risk_calculation; this
    job exists to surface freshness information, not to mutate the file.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.svi_data import WI_COUNTY_FIPS

        results = {
            'source_type': 'fema_nri',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': [],
        }

        candidate_paths = [
            'data/nri/NRI_Table_CensusTracts_Wisconsin_FloodTornadoWinterOnly.csv',
            'data/nri/NRI_Table_Counties.csv',
        ]

        nri_path = next((p for p in candidate_paths if os.path.exists(p)), None)

        if not nri_path:
            logger.warning(
                "FEMA NRI static file not found in any expected location; "
                "skipping freshness update."
            )
            results['errors'].append({
                'error': 'NRI CSV not found',
                'searched_paths': candidate_paths,
            })
            results['finished_at'] = datetime.utcnow().isoformat()
            return results

        try:
            stat = os.stat(nri_path)
            file_size_bytes = stat.st_size
            file_mtime = datetime.utcfromtimestamp(stat.st_mtime)
            file_age_days = max(0, (datetime.utcnow() - file_mtime).days)
        except OSError as exc:
            logger.error(f"Unable to stat NRI file {nri_path}: {exc}")
            results['errors'].append({'error': f'stat failed: {exc}'})
            results['finished_at'] = datetime.utcnow().isoformat()
            return results

        metadata = {
            'source': 'FEMA National Risk Index (static CSV release)',
            'file_path': nri_path,
            'file_size_bytes': file_size_bytes,
            'file_modified_at': file_mtime.isoformat(),
            'file_age_days': file_age_days,
            'description': (
                'FEMA NRI ships as an annual static CSV. This entry records '
                'the bundled file metadata so freshness reporting can flag '
                'an outdated NRI release. The actual NRI values are read '
                'directly from the CSV at calculation time.'
            ),
            'verified_at': datetime.utcnow().isoformat(),
        }

        logger.info(
            "FEMA NRI static file verified: %s (%.1f MB, %d days old)",
            nri_path, file_size_bytes / (1024 * 1024), file_age_days,
        )

        for county_name in WI_COUNTY_FIPS.keys():
            try:
                ok = save_cached_data(
                    source_type='fema_nri',
                    data=metadata,
                    county_name=county_name,
                    api_source=nri_path,
                    used_fallback=False,
                )
                if ok:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'county': county_name, 'error': str(e)})

        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(
            "FEMA NRI freshness verification complete: %d success, %d failed "
            "(file age: %d days)",
            results['success'], results['failed'], file_age_days,
        )
        return results


def refresh_all_openfema_declarations() -> Dict[str, Any]:
    """
    Refresh OpenFEMA Disaster Declarations data for all Wisconsin counties.
    Called weekly by scheduler. No API key required.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    
    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.openfema_data import fetch_disaster_declarations_wi
        
        results = {
            'source_type': 'openfema_disaster_declarations',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info("Starting OpenFEMA disaster declarations refresh")
        
        try:
            data = fetch_disaster_declarations_wi()
            county_data = data.get("county_data", {})
            
            for county_name, county_info in county_data.items():
                try:
                    success = save_cached_data(
                        source_type='openfema_disaster_declarations',
                        data=county_info,
                        county_name=county_name,
                        api_source='OpenFEMA DisasterDeclarationsSummaries v2',
                        fetch_duration=data.get("fetch_duration")
                    )
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'county': county_name, 'error': str(e)})
                    
        except Exception as e:
            logger.error(f"Error fetching disaster declarations: {e}")
            results['errors'].append({'error': str(e)})
        
        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"OpenFEMA declarations refresh: {results['success']} success, {results['failed']} failed")
        return results


def refresh_all_openfema_nfip() -> Dict[str, Any]:
    """
    Refresh OpenFEMA NFIP Claims data for all Wisconsin counties.
    Called weekly by scheduler. No API key required.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    
    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.openfema_data import fetch_nfip_claims_wi
        
        results = {
            'source_type': 'openfema_nfip_claims',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info("Starting OpenFEMA NFIP claims refresh")
        
        try:
            data = fetch_nfip_claims_wi()
            county_data = data.get("county_data", {})
            
            for county_name, county_info in county_data.items():
                try:
                    success = save_cached_data(
                        source_type='openfema_nfip_claims',
                        data=county_info,
                        county_name=county_name,
                        api_source='OpenFEMA FimaNfipClaims v2 (ratedFloodZone)',
                        fetch_duration=data.get("fetch_duration")
                    )
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'county': county_name, 'error': str(e)})
                    
        except Exception as e:
            logger.error(f"Error fetching NFIP claims: {e}")
            results['errors'].append({'error': str(e)})
        
        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"OpenFEMA NFIP refresh: {results['success']} success, {results['failed']} failed")
        return results


def refresh_all_openfema_hma() -> Dict[str, Any]:
    """
    Refresh OpenFEMA Hazard Mitigation Projects data for all Wisconsin counties.
    Called weekly by scheduler. No API key required.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    
    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.openfema_data import fetch_hma_projects_wi
        
        results = {
            'source_type': 'openfema_hma_projects',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info("Starting OpenFEMA HMA projects refresh")
        
        try:
            data = fetch_hma_projects_wi()
            county_data = data.get("county_data", {})
            
            for county_name, county_info in county_data.items():
                try:
                    success = save_cached_data(
                        source_type='openfema_hma_projects',
                        data=county_info,
                        county_name=county_name,
                        api_source='OpenFEMA HazardMitigationAssistanceProjects v4',
                        fetch_duration=data.get("fetch_duration")
                    )
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'county': county_name, 'error': str(e)})
                    
        except Exception as e:
            logger.error(f"Error fetching HMA projects: {e}")
            results['errors'].append({'error': str(e)})
        
        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"OpenFEMA HMA refresh: {results['success']} success, {results['failed']} failed")
        return results


def refresh_all_noaa_storm_events() -> Dict[str, Any]:
    """
    Refresh NOAA Storm Events data for all Wisconsin counties.
    Downloads bulk CSV from NCEI, filters Wisconsin, aggregates by county.
    Called weekly by scheduler. No API key required.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    
    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.noaa_storm_events import fetch_all_storm_events_wi
        
        results = {
            'source_type': 'noaa_storm_events',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info("Starting NOAA Storm Events refresh")
        
        try:
            data = fetch_all_storm_events_wi()
            county_data = data.get("county_data", {})
            
            years_covered = data.get("years_covered", "")
            for county_name, county_info in county_data.items():
                try:
                    county_info["years_covered"] = years_covered
                    success = save_cached_data(
                        source_type='noaa_storm_events',
                        data=county_info,
                        county_name=county_name,
                        api_source='NOAA NCEI Storm Events Database',
                        fetch_duration=data.get("fetch_duration")
                    )
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'county': county_name, 'error': str(e)})
                    
        except Exception as e:
            logger.error(f"Error fetching NOAA storm events: {e}")
            results['errors'].append({'error': str(e)})
        
        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"NOAA Storm Events refresh: {results['success']} success, {results['failed']} failed")
        return results


def refresh_all_nid_dam_inventory() -> Dict[str, Any]:
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.data_cache_manager import save_cached_data
        from utils.nid_data import fetch_wisconsin_dam_inventory

        results = {
            'source_type': 'nid_dam_inventory',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'errors': []
        }

        logger.info("Starting NID dam inventory refresh for Wisconsin")

        try:
            data = fetch_wisconsin_dam_inventory()

            if 'error' in data:
                logger.warning(f"NID fetch returned error: {data['error']}")
                results['errors'].append({'error': data['error']})
                results['finished_at'] = datetime.utcnow().isoformat()
                return results

            county_data = data.get('county_data', {})
            statewide_meta = {
                'total_dams_fetched': data.get('total_dams_fetched', 0),
                'max_county_dam_count': data.get('max_county_dam_count', 25),
                'fetch_time': data.get('fetch_time'),
                'api_source': data.get('api_source')
            }

            for county_name, county_info in county_data.items():
                try:
                    county_info['statewide_meta'] = statewide_meta
                    success = save_cached_data(
                        source_type='nid_dam_inventory',
                        data=county_info,
                        county_name=county_name,
                        api_source='USACE NID ArcGIS FeatureServer',
                        fetch_duration=data.get('fetch_duration')
                    )
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'county': county_name, 'error': str(e)})

        except Exception as e:
            logger.error(f"Error fetching NID dam inventory: {e}")
            results['errors'].append({'error': str(e)})

        results['finished_at'] = datetime.utcnow().isoformat()
        logger.info(f"NID dam inventory refresh: {results['success']} success, {results['failed']} failed")
        return results


def refresh_all_wi_dhs_hvi() -> Dict[str, Any]:
    """
    Refresh the Wisconsin DHS Heat Vulnerability Index cache.

    Paginates the DHS HVI ArcGIS MapServer layer once (4,472 Census
    block groups), aggregates to a 72-county table via unweighted mean
    of block-group z-scores, writes the persistent cache and a
    human-readable JSON snapshot.  HVI updates on a multi-year cadence
    so this job is registered quarterly by data_refresh_scheduler.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.wi_dhs_hvi import fetch_bulk_hvi_data, populate_cache_from_bulk
        from utils.data_cache_manager import set_cached_data

        results = {
            'source_type': 'wi_dhs_hvi',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'errors': [],
        }

        try:
            start = time.time()
            table = fetch_bulk_hvi_data()
            duration = time.time() - start

            if not table:
                results['failed'] = 1
                results['errors'].append({'error': 'Bulk HVI fetch returned empty'})
                logger.error("WI DHS HVI refresh failed: empty bulk result")
            else:
                written = populate_cache_from_bulk(table)
                results['success'] = written
                results['failed'] = max(0, len(table) - written)
                set_cached_data(
                    source_type='hvi',
                    data={
                        'county_count': written,
                        'block_group_count': sum(
                            int(r.get('block_group_count') or 0) for r in table.values()
                        ),
                        'refreshed_at': datetime.utcnow().isoformat(),
                    },
                    fetch_duration=duration,
                    api_source='wi_dhs_hvi_arcgis_mapserver',
                )
                logger.info(
                    f"WI DHS HVI refresh: {written} counties cached in {duration:.1f}s"
                )
        except Exception as e:
            results['failed'] = 1
            results['errors'].append({'error': str(e)})
            logger.error(f"WI DHS HVI refresh exception: {e}")

        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def refresh_all_nssp_respiratory() -> Dict[str, Any]:
    """
    Refresh the CDC NSSP Wisconsin respiratory surveillance cache.

    NSSP publishes statewide percent-of-ED-visits for Influenza,
    COVID-19, and RSV weekly (Fridays). The data is statewide-only,
    so a single fetch warms the cache for all 72 counties; we record
    the result as a single source entry with county_name=None.

    Called weekly by the scheduler so the dashboard does not have to
    wait on a cold-cache live fetch on the first user request after
    each Friday refresh.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.wisconsin_dhs_scraper import refresh_dhs_surveillance_data
        from utils.data_cache_manager import set_cached_data

        results: Dict[str, Any] = {
            'source_type': 'nssp_respiratory',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': [],
        }

        try:
            start = time.time()
            ok = refresh_dhs_surveillance_data()
            duration = time.time() - start

            if ok:
                results['success'] = 1
                set_cached_data(
                    source_type='nssp',
                    data={'refreshed_at': datetime.utcnow().isoformat()},
                    fetch_duration=duration,
                    api_source='cdc_nssp_essence',
                )
                logger.info(
                    f"NSSP respiratory refresh: cache warmed in {duration:.1f}s"
                )
            else:
                results['fallback'] = 1
                set_cached_data(
                    source_type='nssp',
                    data={'refreshed_at': datetime.utcnow().isoformat()},
                    fetch_duration=duration,
                    api_source='cdc_nssp_essence',
                    used_fallback=True,
                    fallback_reason="NSSP refresh used fallback path",
                )
                logger.warning(
                    "NSSP respiratory refresh: completed but data_source != 'nssp_ed_visits' "
                    "(fallback path used). Cache was still updated."
                )
        except Exception as exc:
            results['failed'] = 1
            results['errors'].append({'error': str(exc)})
            logger.error(f"NSSP respiratory refresh exception: {exc}")

        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def refresh_all_cdc_nndss_communicable() -> Dict[str, Any]:
    """
    Refresh the CDC NNDSS Wisconsin communicable disease cache.

    NNDSS publishes weekly state-level case counts for reportable
    diseases (measles, meningococcal, etc.) on Tuesdays
    for the prior MMWR week. The data is statewide-only, so a single
    fetch warms the cache for all 72 counties; we record the result
    as a single source entry with county_name=None.

    Drives the active_measles_outbreak flag in utils/disease_surveillance.py.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.nndss_communicable import fetch_nndss_wi_communicable
        from utils.persistent_cache import clear_cache_by_prefix
        from utils.data_cache_manager import set_cached_data

        results: Dict[str, Any] = {
            'source_type': 'cdc_nndss_communicable',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': [],
        }

        try:
            start = time.time()
            # Force a fresh fetch by clearing the persistent cache first.
            clear_cache_by_prefix('nndss_wi_communicable')
            data = fetch_nndss_wi_communicable()
            duration = time.time() - start

            if data.get('data_source') == 'cdc_nndss':
                results['success'] = 1
                flags = data.get('outbreak_flags', {})
                set_cached_data(
                    source_type='nndss',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_nndss',
                )
                logger.info(
                    f"NNDSS communicable refresh: cache warmed in {duration:.1f}s, "
                    f"report={data.get('report_date')}, flags={flags}"
                )
            else:
                results['fallback'] = 1
                set_cached_data(
                    source_type='nndss',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_nndss',
                    used_fallback=True,
                    fallback_reason="NNDSS communicable fetch returned non-canonical source",
                )
                logger.warning(
                    "NNDSS communicable refresh: completed but data_source != "
                    "'cdc_nndss' (fallback path used)."
                )
        except Exception as exc:
            results['failed'] = 1
            results['errors'].append({'error': str(exc)})
            logger.error(f"NNDSS communicable refresh exception: {exc}")

        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def refresh_all_cdc_nhsn_hospital() -> Dict[str, Any]:
    """
    Refresh the CDC NHSN Wisconsin hospital capacity cache.

    NHSN HRD publishes weekly state-level hospital ICU beds, ICU
    occupancy, and confirmed COVID/flu/RSV hospitalizations and ICU
    patients on Wednesdays for the prior week. The data is
    statewide-only, so a single fetch warms the cache for all 72
    counties; we record the result as a single source entry with
    county_name=None.

    Replaces the previously aspirational wha_hospital_capacity entry.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.nhsn_hospital import fetch_nhsn_wi_hospital
        from utils.persistent_cache import clear_cache_by_prefix
        from utils.data_cache_manager import set_cached_data

        results: Dict[str, Any] = {
            'source_type': 'cdc_nhsn_hospital',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0,
            'failed': 0,
            'fallback': 0,
            'errors': [],
        }

        try:
            start = time.time()
            clear_cache_by_prefix('nhsn_wi_hospital')
            data = fetch_nhsn_wi_hospital()
            duration = time.time() - start

            if data.get('data_source') == 'cdc_nhsn_hrd':
                results['success'] = 1
                cw = data.get('current_week', {})
                set_cached_data(
                    source_type='nhsn',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_nhsn_hrd',
                )
                logger.info(
                    f"NHSN hospital refresh: cache warmed in {duration:.1f}s, "
                    f"week={data.get('report_date')}, "
                    f"ICU={cw.get('icu_occupancy_pct')}, "
                    f"resp_admissions={cw.get('total_respiratory_new_admissions')}"
                )
            else:
                results['fallback'] = 1
                set_cached_data(
                    source_type='nhsn',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_nhsn_hrd',
                    used_fallback=True,
                    fallback_reason="NHSN hospital fetch returned non-canonical source",
                )
                logger.warning(
                    "NHSN hospital refresh: completed but data_source != "
                    "'cdc_nhsn_hrd' (fallback path used)."
                )
        except Exception as exc:
            results['failed'] = 1
            results['errors'].append({'error': str(exc)})
            logger.error(f"NHSN hospital refresh exception: {exc}")

        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def refresh_all_h5n1() -> Dict[str, Any]:
    """
    Refresh USDA APHIS H5N1 HPAI livestock/poultry detection cache for WI.

    Pulls the latest CSV exports, filters to Wisconsin, derives the tier
    (none / national_only / state / local), and writes the result to the
    persistent cache. See utils/h5n1_surveillance.py for tier definitions
    and the source URLs.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.h5n1_surveillance import fetch_h5n1_surveillance
        from utils.persistent_cache import clear_cache_by_prefix
        from utils.data_cache_manager import set_cached_data

        results: Dict[str, Any] = {
            'source_type': 'h5n1',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0, 'failed': 0, 'fallback': 0, 'errors': [],
        }
        try:
            start = time.time()
            clear_cache_by_prefix('h5n1_surveillance')
            data = fetch_h5n1_surveillance()
            duration = time.time() - start
            if data.get('source') == 'usda_aphis':
                results['success'] = 1
                set_cached_data(
                    source_type='h5n1',
                    data=data,
                    fetch_duration=duration,
                    api_source='usda_aphis',
                )
                logger.info(
                    f"H5N1 refresh: cache warmed in {duration:.1f}s, "
                    f"tier={data.get('tier')}, "
                    f"wi_livestock={data.get('wi_livestock_detections_90d')}, "
                    f"wi_poultry={data.get('wi_poultry_detections_90d')}"
                )
            else:
                results['fallback'] = 1
                set_cached_data(
                    source_type='h5n1',
                    data=data,
                    fetch_duration=duration,
                    api_source='usda_aphis',
                    used_fallback=True,
                    fallback_reason="H5N1 fetch returned non-canonical source",
                )
                logger.warning("H5N1 refresh: completed but source != 'usda_aphis' (fallback path)")
        except Exception as exc:
            results['failed'] = 1
            results['errors'].append({'error': str(exc)})
            logger.error(f"H5N1 refresh exception: {exc}")
        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def refresh_all_mpox() -> Dict[str, Any]:
    """
    Refresh CDC mpox state-level case-count cache for Wisconsin.

    Pulls the CDC mpox Socrata dataset, derives WI 4-week count, and
    classifies the tier (baseline / elevated / cluster). See
    utils/mpox_surveillance.py for tier thresholds.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.mpox_surveillance import fetch_mpox_surveillance
        from utils.persistent_cache import clear_cache_by_prefix
        from utils.data_cache_manager import set_cached_data

        results: Dict[str, Any] = {
            'source_type': 'mpox',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0, 'failed': 0, 'fallback': 0, 'errors': [],
        }
        try:
            start = time.time()
            clear_cache_by_prefix('mpox_surveillance')
            data = fetch_mpox_surveillance()
            duration = time.time() - start
            if data.get('source') == 'cdc_mpox':
                results['success'] = 1
                set_cached_data(
                    source_type='mpox',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_mpox',
                )
                logger.info(
                    f"Mpox refresh: cache warmed in {duration:.1f}s, "
                    f"tier={data.get('tier')}, "
                    f"wi_4wk={data.get('wi_recent_4wk_cases')}"
                )
            else:
                results['fallback'] = 1
                set_cached_data(
                    source_type='mpox',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_mpox',
                    used_fallback=True,
                    fallback_reason="Mpox fetch returned non-canonical source",
                )
                logger.warning("Mpox refresh: completed but source != 'cdc_mpox' (fallback path)")
        except Exception as exc:
            results['failed'] = 1
            results['errors'].append({'error': str(exc)})
            logger.error(f"Mpox refresh exception: {exc}")
        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def refresh_all_nndss_enteric() -> Dict[str, Any]:
    """
    Refresh CDC NNDSS Wisconsin enteric + legionellosis cache.

    Pulls the latest weekly NNDSS rows for the tracked enteric agents
    (Salmonellosis, STEC, Shigellosis, Campylobacteriosis,
    Cryptosporidiosis, Giardiasis) plus Legionellosis. Drives the
    enteric composite flag and the legionella flag in
    utils/disease_surveillance.py. See utils/nndss_enteric.py for the
    agent list and threshold logic.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}

    with app.app_context():
        from utils.nndss_enteric import fetch_nndss_enteric_wi
        from utils.persistent_cache import clear_cache_by_prefix
        from utils.data_cache_manager import set_cached_data

        results: Dict[str, Any] = {
            'source_type': 'nndss_enteric',
            'started_at': datetime.utcnow().isoformat(),
            'success': 0, 'failed': 0, 'fallback': 0, 'errors': [],
        }
        try:
            start = time.time()
            clear_cache_by_prefix('nndss_enteric_wi')
            data = fetch_nndss_enteric_wi()
            duration = time.time() - start
            if data.get('data_source') == 'cdc_nndss_enteric':
                results['success'] = 1
                agents = data.get('enteric_agents', {})
                leg = data.get('legionella', {})
                set_cached_data(
                    source_type='nndss_enteric',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_nndss_enteric',
                )
                logger.info(
                    f"NNDSS enteric refresh: cache warmed in {duration:.1f}s, "
                    f"report={data.get('report_date')}, "
                    f"agents={len(agents)}, "
                    f"legionella_4wk={leg.get('recent_4wk_cases')}"
                )
            else:
                results['fallback'] = 1
                set_cached_data(
                    source_type='nndss_enteric',
                    data=data,
                    fetch_duration=duration,
                    api_source='cdc_nndss_enteric',
                    used_fallback=True,
                    fallback_reason="NNDSS enteric fetch returned non-canonical source",
                )
                logger.warning(
                    "NNDSS enteric refresh: completed but data_source != 'cdc_nndss_enteric'"
                )
        except Exception as exc:
            results['failed'] = 1
            results['errors'].append({'error': str(exc)})
            logger.error(f"NNDSS enteric refresh exception: {exc}")
        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def run_all_refreshes() -> Dict[str, Any]:
    """
    Run all data source refreshes. Used for initial cache population.
    Each individual refresh function handles its own app context.
    """
    logger.info("Starting full data cache refresh")
    
    results = {
        'started_at': datetime.utcnow().isoformat(),
        'sources': {}
    }
    
    results['sources']['cdc_svi'] = refresh_all_cdc_svi()
    results['sources']['epa_air_quality'] = refresh_all_epa_air_quality()
    results['sources']['dhs_health'] = refresh_all_dhs_health()
    results['sources']['nws_forecast'] = refresh_all_nws_forecasts()
    results['sources']['fema_nri'] = refresh_all_fema_nri()
    results['sources']['openfema_declarations'] = refresh_all_openfema_declarations()
    results['sources']['openfema_nfip'] = refresh_all_openfema_nfip()
    results['sources']['openfema_hma'] = refresh_all_openfema_hma()
    results['sources']['noaa_storm_events'] = refresh_all_noaa_storm_events()
    results['sources']['nid_dam_inventory'] = refresh_all_nid_dam_inventory()
    results['sources']['wi_dhs_hvi'] = refresh_all_wi_dhs_hvi()
    results['sources']['nssp_respiratory'] = refresh_all_nssp_respiratory()
    results['sources']['cdc_nndss_communicable'] = refresh_all_cdc_nndss_communicable()
    results['sources']['cdc_nhsn_hospital'] = refresh_all_cdc_nhsn_hospital()
    results['sources']['h5n1'] = refresh_all_h5n1()
    results['sources']['mpox'] = refresh_all_mpox()
    results['sources']['nndss_enteric'] = refresh_all_nndss_enteric()

    results['finished_at'] = datetime.utcnow().isoformat()
    
    logger.info("Full data cache refresh complete")
    return results


def refresh_action_plan_source_verifier() -> Dict[str, Any]:
    """
    Quarterly re-verification of every URL cited in
    `data/action_plans/_sources.yaml`.

    This is not an external-data fetcher: it runs the standalone
    `scripts/verify_action_plan_sources.py` logic out-of-band so that
    broken citations or content drift surface within at most a quarter
    instead of relying on a human to spot-check. It respects the
    cache-only request-path invariant documented in ARCHITECTURE.md by
    never being invoked from a user request - only the scheduler calls
    this function.

    Behavior:
    - Always fetches every cited URL and writes a status snapshot to
      `data/action_plans/_verifier_status.json` so the dashboard (or an
      operator) can surface the most recent round.
    - On a fully clean run (every URL HTTP 200, no content drift) the
      scheduler bumps each source's `verified:` date and appends a
      summary section to `_research_log.md`, mirroring the
      `--bump --log` invocation a human would run.
    - On any failure or drift, the verified dates are NOT bumped (so the
      stale-citation signal in the dashboard does not silently advance),
      the research log is still appended so the SME work group has a
      written trail, and the status file records the failed/drifted URLs
      so a dashboard banner can pick them up.

    Returns a scheduler-compatible results dict. `failed > 0` with
    `success == 0` and `fallback == 0` causes the scheduler to mark this
    job as errored (see refresh_data_source() in
    utils.data_refresh_scheduler), which is the alert path: the next
    scheduler-status read will show the error and the last_error string.
    """
    import importlib.util
    import json as _json

    started_at = datetime.utcnow().isoformat()

    results: Dict[str, Any] = {
        'source_type': 'action_plan_source_verifier',
        'started_at': started_at,
        'success': 0,
        'failed': 0,
        'fallback': 0,
        'errors': [],
    }

    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'scripts',
        'verify_action_plan_sources.py',
    )
    if not os.path.exists(script_path):
        msg = f"Verifier script not found at {script_path}"
        logger.error(msg)
        results['error'] = msg
        results['failed'] = 1
        return results

    try:
        spec = importlib.util.spec_from_file_location(
            'verify_action_plan_sources', script_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec from {script_path}")
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
    except Exception as e:
        msg = f"Failed to load verifier script: {type(e).__name__}: {e}"
        logger.error(msg)
        results['error'] = msg
        results['failed'] = 1
        return results

    try:
        raw = verifier.load_sources()
        sources = (raw or {}).get('sources') or {}
        if not sources:
            msg = "No sources found in _sources.yaml"
            logger.error(msg)
            results['error'] = msg
            results['failed'] = 1
            return results

        logger.info(
            "Action-plan source verifier: checking %d cited URL(s)",
            len(sources),
        )
        verify_results = verifier.verify_all(sources)

        ok = [r for r in verify_results if r.get('ok')]
        failed = [r for r in verify_results if not r.get('ok')]
        drifted = [r for r in verify_results if r.get('drift')]

        from datetime import date as _date
        today = _date.today().isoformat()

        clean_round = not failed and not drifted

        if clean_round:
            try:
                bumped = verifier.bump_verified_dates(verify_results, today)
                verifier.update_hash_store(verify_results)
                logger.info(
                    "Action-plan source verifier: clean round; bumped "
                    "verified date to %s for %d source(s)",
                    today, bumped,
                )
            except Exception as e:
                logger.warning(
                    "Verifier bump step failed: %s: %s",
                    type(e).__name__, e,
                )
        else:
            logger.warning(
                "Action-plan source verifier: %d failed, %d drifted; "
                "skipping verified-date bump until SME review",
                len(failed), len(drifted),
            )

        try:
            verifier.append_research_log(verify_results, today)
        except Exception as e:
            logger.warning(
                "Verifier research-log append failed: %s: %s",
                type(e).__name__, e,
            )

        status_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'action_plans', '_verifier_status.json',
        )
        status_payload = {
            'last_run_at': datetime.utcnow().isoformat(),
            'last_run_date': today,
            'total_sources': len(verify_results),
            'ok_count': len(ok),
            'failed_count': len(failed),
            'drift_count': len(drifted),
            'clean_round': clean_round,
            'failed': [
                {
                    'id': r.get('id'),
                    'url': r.get('url'),
                    'status': r.get('status'),
                    'error': r.get('error'),
                }
                for r in failed
            ],
            'drifted': [
                {'id': r.get('id'), 'url': r.get('url')}
                for r in drifted
            ],
            'verified_dates_bumped': clean_round,
        }
        try:
            os.makedirs(os.path.dirname(status_path), exist_ok=True)
            with open(status_path, 'w', encoding='utf-8') as f:
                _json.dump(status_payload, f, indent=2, sort_keys=True)
                f.write("\n")
        except Exception as e:
            logger.warning(
                "Failed to write verifier status file %s: %s: %s",
                status_path, type(e).__name__, e,
            )

        results['success'] = len(ok)
        results['failed'] = len(failed)
        results['drift'] = len(drifted)
        results['total'] = len(verify_results)
        results['clean_round'] = clean_round
        for r in failed:
            err = r.get('error') or f"HTTP {r.get('status')}"
            results['errors'].append(f"{r.get('id')}: {err} ({r.get('url')})")
        for r in drifted:
            results['errors'].append(
                f"{r.get('id')}: content drift since previous round "
                f"({r.get('url')})"
            )
        results['finished_at'] = datetime.utcnow().isoformat()
        return results

    except Exception as e:
        msg = f"Verifier run failed: {type(e).__name__}: {e}"
        logger.exception(msg)
        results['error'] = msg
        results['failed'] = max(results.get('failed', 0), 1)
        results['finished_at'] = datetime.utcnow().isoformat()
        return results


def refresh_all_county_health_rankings() -> Dict[str, Any]:
    """
    Pre-warm the County Health Rankings persistent cache.

    Clears the current CHR cache entry and re-fetches the County Health
    Rankings CSV for all Wisconsin counties via countyhealthrankings.org.
    Called by the scheduler on the annual track. The underlying
    _fetch_chr_wi_data() function writes the result back to the persistent
    cache so subsequent dashboard requests read from cache only.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    with app.app_context():
        try:
            from utils.health_metrics_data import (
                _fetch_chr_wi_data,
                CHR_CACHE_KEY,
            )
            from utils.persistent_cache import clear_cache_by_prefix
            from utils.data_cache_manager import set_cached_data

            clear_cache_by_prefix(CHR_CACHE_KEY)
            import time as _time
            _t0 = _time.time()
            data = _fetch_chr_wi_data()
            _dur = _time.time() - _t0
            county_count = len(data)
            if county_count > 0:
                set_cached_data(
                    source_type='chr',
                    data={'county_count': county_count, 'refreshed_at': datetime.utcnow().isoformat()},
                    fetch_duration=_dur,
                    api_source='countyhealthrankings.org',
                )
                logger.info("CHR refresh: %d WI counties loaded", county_count)
                return {'success': county_count, 'failed': 0, 'fallback': 0, 'errors': []}
            return {
                'success': 0, 'failed': 1, 'fallback': 0,
                'errors': [{'county': 'bulk', 'error': 'CHR fetch returned no county data'}],
            }
        except Exception as exc:
            logger.exception("CHR refresh raised unexpectedly: %s", exc)
            return {
                'source_type': 'county_health_rankings',
                'error': f"{type(exc).__name__}: {exc}",
                'success': 0,
                'failed': 1,
            }


def refresh_all_cdc_places_copd() -> Dict[str, Any]:
    """
    Pre-warm the CDC PLACES COPD persistent cache.

    Clears the current COPD cache entry and re-fetches crude COPD prevalence
    for all Wisconsin counties via the CDC PLACES Socrata API. Called by the
    scheduler on the annual track. The underlying _fetch_places_copd_wi()
    function writes the result back to the persistent cache.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    with app.app_context():
        try:
            from utils.health_metrics_data import (
                _fetch_places_copd_wi,
                PLACES_COPD_CACHE_KEY,
            )
            from utils.persistent_cache import clear_cache_by_prefix
            from utils.data_cache_manager import set_cached_data

            clear_cache_by_prefix(PLACES_COPD_CACHE_KEY)
            import time as _time
            _t0 = _time.time()
            data = _fetch_places_copd_wi()
            _dur = _time.time() - _t0
            county_count = len(data)
            if county_count > 0:
                set_cached_data(
                    source_type='places_copd',
                    data={'county_count': county_count, 'refreshed_at': datetime.utcnow().isoformat()},
                    fetch_duration=_dur,
                    api_source='cdc_places_socrata',
                )
                logger.info(
                    "CDC PLACES COPD refresh: %d WI counties loaded", county_count
                )
                return {'success': county_count, 'failed': 0, 'fallback': 0, 'errors': []}
            return {
                'success': 0, 'failed': 1, 'fallback': 0,
                'errors': [
                    {'county': 'bulk', 'error': 'PLACES COPD fetch returned no county data'}
                ],
            }
        except Exception as exc:
            logger.exception("PLACES COPD refresh raised unexpectedly: %s", exc)
            return {
                'source_type': 'cdc_places_copd',
                'error': f"{type(exc).__name__}: {exc}",
                'success': 0,
                'failed': 1,
            }


def refresh_all_cdc_places_mhlth() -> Dict[str, Any]:
    """
    Pre-warm the CDC PLACES mental-distress persistent cache.

    Clears the current MHLTH cache entry and re-fetches frequent mental
    distress prevalence for all Wisconsin counties via the CDC PLACES Socrata
    API. Called by the scheduler on the annual track. The underlying
    _fetch_places_mhlth_wi() function writes the result back to the persistent
    cache.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    with app.app_context():
        try:
            from utils.health_metrics_data import (
                _fetch_places_mhlth_wi,
                PLACES_MHLTH_CACHE_KEY,
            )
            from utils.persistent_cache import clear_cache_by_prefix
            from utils.data_cache_manager import set_cached_data

            clear_cache_by_prefix(PLACES_MHLTH_CACHE_KEY)
            import time as _time
            _t0 = _time.time()
            data = _fetch_places_mhlth_wi()
            _dur = _time.time() - _t0
            county_count = len(data)
            if county_count > 0:
                set_cached_data(
                    source_type='places_mhlth',
                    data={'county_count': county_count, 'refreshed_at': datetime.utcnow().isoformat()},
                    fetch_duration=_dur,
                    api_source='cdc_places_socrata',
                )
                logger.info(
                    "CDC PLACES MHLTH refresh: %d WI counties loaded", county_count
                )
                return {'success': county_count, 'failed': 0, 'fallback': 0, 'errors': []}
            return {
                'success': 0, 'failed': 1, 'fallback': 0,
                'errors': [
                    {'county': 'bulk', 'error': 'PLACES MHLTH fetch returned no county data'}
                ],
            }
        except Exception as exc:
            logger.exception("PLACES MHLTH refresh raised unexpectedly: %s", exc)
            return {
                'source_type': 'cdc_places_mhlth',
                'error': f"{type(exc).__name__}: {exc}",
                'success': 0,
                'failed': 1,
            }


def refresh_all_wi_dhs_mmr() -> Dict[str, Any]:
    """
    Pre-warm the WI DHS MMR immunization persistent cache.

    Clears the current MMR county cache entry and re-fetches MMR (1)
    vaccination rates for 24-month-old children by county via the WI DHS
    immunization CSV. Called by the scheduler on the monthly track (~720h).
    The underlying _fetch_mmr_county_data() function writes the result back
    to the persistent cache.
    """
    app = _get_app()
    if not app:
        return {'error': 'No Flask app available', 'success': 0, 'failed': 0}
    with app.app_context():
        try:
            from utils.dhs_data import _fetch_mmr_county_data, MMR_COUNTY_CACHE_KEY
            from utils.persistent_cache import clear_cache_by_prefix
            from utils.data_cache_manager import set_cached_data

            clear_cache_by_prefix(MMR_COUNTY_CACHE_KEY)
            import time as _time
            _t0 = _time.time()
            data = _fetch_mmr_county_data()
            _dur = _time.time() - _t0
            county_count = len(data)
            if county_count > 0:
                set_cached_data(
                    source_type='mmr',
                    data={'county_count': county_count, 'refreshed_at': datetime.utcnow().isoformat()},
                    fetch_duration=_dur,
                    api_source='wi_dhs_immunization_csv',
                )
                logger.info("WI DHS MMR refresh: %d counties loaded", county_count)
                return {'success': county_count, 'failed': 0, 'fallback': 0, 'errors': []}
            return {
                'success': 0, 'failed': 1, 'fallback': 0,
                'errors': [{'county': 'bulk', 'error': 'MMR fetch returned no county data'}],
            }
        except Exception as exc:
            logger.exception("WI DHS MMR refresh raised unexpectedly: %s", exc)
            return {
                'source_type': 'wi_dhs_mmr',
                'error': f"{type(exc).__name__}: {exc}",
                'success': 0,
                'failed': 1,
            }


