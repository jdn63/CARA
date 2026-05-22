"""
API routes for CARA application.

These routes handle REST API endpoints:
- Historical and predictive analysis data
- HERC and WEM region data  
- Geographic boundaries
- Admin functionality (scheduler, data refresh)
"""

import logging
from datetime import datetime
from flask import Blueprint
from utils.data_processor import get_historical_risk_data
from utils.predictive_analysis import RiskPredictor
from utils.herc_data import get_herc_statistics, get_all_herc_regions
from utils.wem_data import get_wem_statistics, get_all_wem_regions
from utils import geo_data
from utils.data_refresh_scheduler import (
    get_scheduler_status,
    refresh_now,
    start_scheduler,
    stop_scheduler,
    initialize as initialize_scheduler,
)
from utils.security_manager import require_api_key
from utils.api_responses import api_success, api_error, api_not_found, api_server_error

# Set up logger for this module
logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/historical-data/<jurisdiction_id>')
@require_api_key('readonly')  # Requires API key
def get_historical_risk_data_api(jurisdiction_id):
    """Get historical risk data for predictions (API endpoint)"""
    try:
        # Get historical data from the utility
        start_year = 2020  # Default start year
        end_year = 2024    # Default end year
        
        data = get_historical_risk_data(jurisdiction_id, start_year, end_year)
        
        # Log API access
        logger.info(f"API access: Historical data requested for jurisdiction {jurisdiction_id}")
        
        return api_success({
            'jurisdiction_id': jurisdiction_id,
            'data': data,
            'years_requested': f"{start_year}-{end_year}",
            'data_points': len(data)
        }, "Historical data retrieved successfully")
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/predictive-analysis/<jurisdiction_id>')
@require_api_key('readonly')  # Requires API key  
def get_predictive_analysis_api(jurisdiction_id):
    """Get predictive analysis for jurisdiction (API endpoint)"""
    try:
        # Get current risk data first
        from utils.data_processor import process_risk_data
        from routes.dashboard import sanitize_risk_data
        
        current_risk_data = process_risk_data(jurisdiction_id)
        current_risk_data = sanitize_risk_data(current_risk_data)
        
        # Generate predictions
        predictor = RiskPredictor()
        analysis = predictor.generate_predictions(jurisdiction_id, current_risk_data)
        
        logger.info(f"API access: Predictive analysis requested for jurisdiction {jurisdiction_id}")
        
        return api_success({
            'jurisdiction_id': jurisdiction_id,
            'analysis': analysis,
            'prediction_type': 'multi_domain_risk_forecast'
        }, "Predictive analysis generated successfully")
    except Exception as e:
        logger.error(f"Error generating predictive analysis: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/herc-region/<region_id>')
@require_api_key('readonly')
def get_herc_region_data_api(region_id):
    """Get HERC region data (API endpoint)"""
    try:
        herc_data = get_herc_statistics(region_id)
        
        if not herc_data:
            return api_not_found("HERC region")
            
        logger.info(f"API access: HERC region data requested for region {region_id}")
        
        return api_success(herc_data, "HERC region data retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting HERC region data: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/herc-regions')
@require_api_key('readonly')
def get_all_herc_regions_api():
    """Get all HERC regions data (API endpoint)"""
    try:
        herc_regions = get_all_herc_regions()
        
        logger.info("API access: All HERC regions data requested")
        
        return api_success(herc_regions, "All HERC regions retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting HERC regions: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/wem-region/<region_id>')
@require_api_key('readonly')
def get_wem_region_data_api(region_id):
    """Get WEM region data (API endpoint)"""
    try:
        wem_data = get_wem_statistics(region_id)
        
        if not wem_data:
            return api_not_found("WEM region")
            
        logger.info(f"API access: WEM region data requested for region {region_id}")
        
        return api_success(wem_data, "WEM region data retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting WEM region data: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/wem-regions')
@require_api_key('readonly')
def get_all_wem_regions_api():
    """Get all WEM regions data (API endpoint)"""
    try:
        wem_regions = get_all_wem_regions()
        
        logger.info("API access: All WEM regions data requested")
        
        return api_success(wem_regions, "All WEM regions retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting WEM regions: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/herc-boundaries')
@require_api_key('readonly')
def get_herc_boundaries_api():
    """Get HERC region boundaries (API endpoint)"""
    try:
        # Get HERC boundary data from geo_data utility
        boundaries = geo_data.get_herc_region_boundaries()
        
        logger.info("API access: HERC boundaries data requested")
        
        return api_success(boundaries, "HERC boundaries retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting HERC boundaries: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/wem-boundaries')
@require_api_key('readonly')
def get_wem_boundaries_api():
    """Get WEM region boundaries (API endpoint)"""
    try:
        # Get WEM boundary data from geo_data utility
        boundaries = geo_data.get_wem_region_boundaries()
        
        logger.info("API access: WEM boundaries data requested")
        
        return api_success(boundaries, "WEM boundaries retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting WEM boundaries: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/scheduler-status')
@require_api_key('admin')  # Requires admin access
def get_scheduler_status_api():
    """Get data refresh scheduler status (admin only)"""
    try:
        status = get_scheduler_status()
        
        logger.info("API access: Scheduler status requested (admin)")
        
        return api_success(status, "Scheduler status retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        return api_server_error(str(e))


@api_bp.route('/invalidate-herc-cache', methods=['POST'])
@require_api_key('admin')
def invalidate_herc_cache_api():
    """Mark all HERC DB cache entries as invalid, forcing recalculation on next request.
    Call this after deploying methodology changes that affect HERC risk scores."""
    try:
        from core import db
        from models import HERCRiskCache

        count = db.session.query(HERCRiskCache).update({'is_valid': False})
        db.session.commit()

        # Also clear in-memory caches
        from utils.herc_risk_aggregator import _herc_cache, _jurisdiction_cache
        _herc_cache.clear()
        _jurisdiction_cache.clear()

        logger.info(f"HERC cache invalidated: {count} DB entries marked invalid (admin request)")
        return api_success({
            'db_entries_invalidated': count,
            'in_memory_cleared': True,
            'timestamp': datetime.now().isoformat()
        }, f"HERC cache cleared. {count} region(s) will recalculate on next dashboard load.")
    except Exception as e:
        logger.error(f"Error invalidating HERC cache: {str(e)}")
        return api_server_error(str(e))


def _external_scheduler_mode() -> bool:
    """B1: in external mode the dedicated cara-scheduler Render worker
    owns the scheduler. The web service must not start its own copy --
    doing so would reintroduce the same race the worker was created to
    fix. Admin endpoints below short-circuit when this is true.
    """
    import os as _os
    return _os.environ.get("SCHEDULER_MODE", "embedded").lower() == "external"


@api_bp.route('/scheduler-start', methods=['POST'])
@require_api_key('admin')
def scheduler_start_api():
    """Manually start the data refresh scheduler (admin only).

    Use this when the scheduler did not auto-start at boot (for example after
    a cold deploy on Render where the background-init thread crashed silently
    or never spawned). Safe to call repeatedly: start_scheduler() returns
    False if it is already running.
    """
    if _external_scheduler_mode():
        # Refuse cleanly: the scheduler is owned by the dedicated
        # cara-scheduler worker service. Spawning one here would
        # re-create the duplicate-refresh race we just eliminated.
        logger.warning(
            "scheduler-start refused: SCHEDULER_MODE=external "
            "(managed by cara-scheduler worker service)"
        )
        return api_success({
            'started_now': False,
            'managed_by': 'cara-scheduler worker service',
            'hint': 'Inspect or restart the worker on the Render dashboard.',
        }, "Scheduler is managed by the cara-scheduler worker; web cannot start it."), 409

    try:
        try:
            initialize_scheduler()
        except Exception as init_exc:
            logger.error(f"scheduler initialize() raised: {init_exc}", exc_info=True)
            return api_server_error(f"initialize failed: {init_exc}")

        started = start_scheduler(run_in_background=True)
        status = get_scheduler_status()

        logger.info(f"API access: Scheduler manual start requested (admin). started={started}, running={status.get('running')}")

        return api_success({
            'started_now': started,
            'already_running': not started,
            'running': status.get('running', False),
            'source_count': len(status.get('sources', [])),
            'timestamp': datetime.now().isoformat()
        }, "Scheduler start requested")
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}", exc_info=True)
        return api_server_error(str(e))


@api_bp.route('/scheduler-stop', methods=['POST'])
@require_api_key('admin')
def scheduler_stop_api():
    """Manually stop the data refresh scheduler (admin only)."""
    if _external_scheduler_mode():
        logger.warning(
            "scheduler-stop refused: SCHEDULER_MODE=external "
            "(managed by cara-scheduler worker service)"
        )
        return api_success({
            'stopped_now': False,
            'managed_by': 'cara-scheduler worker service',
            'hint': 'Stop the worker on the Render dashboard if needed.',
        }, "Scheduler is managed by the cara-scheduler worker; web cannot stop it."), 409

    try:
        stopped = stop_scheduler()
        status = get_scheduler_status()

        logger.info(f"API access: Scheduler manual stop requested (admin). stopped={stopped}, running={status.get('running')}")

        return api_success({
            'stopped_now': stopped,
            'was_already_stopped': not stopped,
            'running': status.get('running', False),
            'timestamp': datetime.now().isoformat()
        }, "Scheduler stop requested")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}", exc_info=True)
        return api_server_error(str(e))


@api_bp.route('/refresh-data/<source>')
@require_api_key('admin')  # Requires admin access for data refresh
def refresh_data_source_api(source):
    """Trigger data refresh for specific source (admin only)"""
    try:
        result = refresh_now(source)
        
        logger.info(f"API access: Data refresh triggered for {source} (admin)")
        
        return api_success({
            'source': source,
            'refresh_result': result,
            'timestamp': datetime.now().isoformat()
        }, "Data refresh completed successfully")
    except Exception as e:
        logger.error(f"Error refreshing data source {source}: {str(e)}")
        return api_server_error(str(e))