"""
Data Refresh Scheduler Module

This module implements a configurable scheduler for refreshing various data sources at appropriate intervals:
- Daily: Weather patterns and forecasts
- Weekly: Disease surveillance data from health departments
- Monthly: Seasonal forecasts and vaccination rates
- Quarterly: Social Vulnerability Index and crime statistics
- Annually: Census demographic data and climate projections
"""

import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional, Callable

# Get module logger (centralized config in core.py)
logger = logging.getLogger(__name__)

# Path to scheduler configuration
SCHEDULER_CONFIG_PATH = "./data/config/scheduler_config.json"

# Global scheduler state
_scheduler_running = False
_scheduler_thread = None
_scheduler_status = {}
_scheduler_jobs = {}
_refresh_timestamps = {}
_refresh_in_progress = {}

def _build_default_scheduler_config() -> Dict[str, Any]:
    """Build the default scheduler config from the canonical source
    registry. This is the single source of truth: adding a new entry
    to utils.source_registry.CANONICAL_SOURCES will (after the next
    install or a manual delete of scheduler_config.json) cause the
    scheduler to pick it up automatically.

    A small set of non-source jobs (currently only the herc_risk_cache
    pre-computation) live outside the registry because they are not
    external feeds; they are added explicitly here.
    """
    from utils.source_registry import CANONICAL_SOURCES

    data_sources: Dict[str, Any] = {}
    for canonical_id, spec in CANONICAL_SOURCES.items():
        data_sources[canonical_id] = {
            "description": spec.description,
            "refresh_interval_hours": spec.refresh_interval_hours,
            "module": spec.module,
            "function": spec.function,
        }

    # Non-source background job: pre-compute aggregated HERC region risk.
    data_sources["herc_risk_cache"] = {
        "description": "HERC region pre-computed risk data",
        "refresh_interval_hours": 4,
        "module": "utils.herc_risk_aggregator",
        "function": "precompute_all_herc_regions",
    }

    return {"data_sources": data_sources}


def _migrate_legacy_source_ids(config: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Rewrite legacy source IDs in an on-disk scheduler config to
    their canonical equivalents. Returns the (possibly mutated) config
    and a list of human-readable migration notes for logging.

    Legacy stub entries whose underlying module never existed (the
    'weather_patterns', 'seasonal_forecasts', 'vaccination_rates',
    'crime_statistics', 'census_data', 'climate_projections' jobs
    introduced years ago and never wired to real fetchers) are
    dropped here: they cannot be canonicalized, the modules they
    reference are not in the repository, and keeping them in the
    config caused the scheduler to log import errors every cycle.
    """
    from utils.source_registry import CANONICAL_SOURCES, canonicalize

    DEAD_STUBS = {
        "weather_patterns", "seasonal_forecasts", "vaccination_rates",
        "crime_statistics", "census_data", "climate_projections",
    }

    sources = config.get("data_sources", {})
    notes: List[str] = []
    migrated: Dict[str, Any] = {}

    for legacy_key, spec in sources.items():
        if legacy_key in DEAD_STUBS:
            notes.append(f"dropped dead stub '{legacy_key}' (module never existed)")
            continue

        canonical = canonicalize(legacy_key)
        if canonical is None and legacy_key == "herc_risk_cache":
            # Non-source job, kept as-is.
            migrated[legacy_key] = spec
            continue
        if canonical is None and legacy_key == "disease_surveillance":
            # Umbrella job that fanned out to three separate CDC feeds.
            # Split it into the three canonical entries so each has its
            # own schedule and the dashboard can age them independently.
            for nid in ("nssp", "nndss", "nhsn"):
                rspec = CANONICAL_SOURCES[nid]
                migrated[nid] = {
                    "description": rspec.description,
                    "refresh_interval_hours": rspec.refresh_interval_hours,
                    "module": rspec.module,
                    "function": rspec.function,
                }
            notes.append("split 'disease_surveillance' into nssp/nndss/nhsn")
            continue
        if canonical is None:
            # Unknown key: keep it so the operator can investigate, but
            # the startup assertion will flag it loudly.
            migrated[legacy_key] = spec
            notes.append(f"kept unknown source '{legacy_key}' (not in registry)")
            continue

        if canonical != legacy_key:
            notes.append(f"renamed '{legacy_key}' -> '{canonical}'")

        # When the canonical key is in the registry, rewrite module/
        # function/description to match the registry too so a code
        # update to the refresh function lands without requiring a
        # manual JSON edit. Preserve the operator's refresh_interval_hours
        # if it differs from the default (operator tuning is sacred).
        rspec = CANONICAL_SOURCES[canonical]
        merged = {
            "description": rspec.description,
            "refresh_interval_hours": spec.get(
                "refresh_interval_hours", rspec.refresh_interval_hours
            ),
            "module": rspec.module,
            "function": rspec.function,
        }
        migrated[canonical] = merged

    config["data_sources"] = migrated
    return config, notes


def load_scheduler_config() -> Dict[str, Any]:
    """
    Load scheduler configuration from JSON file.

    Behavior:
    - If the JSON file does not exist, write the default config built
      from utils.source_registry.CANONICAL_SOURCES.
    - If it exists, load it and run _migrate_legacy_source_ids() to
      rewrite any pre-canonicalization keys (cdc_svi -> svi etc.) and
      drop dead stub entries. The mutated config is persisted back so
      the on-disk file converges to canonical IDs.
    - Backfill any registry sources missing from the on-disk config
      (a new entry added in code should not require a manual edit).
    """
    os.makedirs(os.path.dirname(SCHEDULER_CONFIG_PATH), exist_ok=True)

    if not os.path.exists(SCHEDULER_CONFIG_PATH):
        default_config = _build_default_scheduler_config()
        with open(SCHEDULER_CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=2)
        logger.info(f"Created default scheduler configuration at {SCHEDULER_CONFIG_PATH}")
        return default_config

    try:
        with open(SCHEDULER_CONFIG_PATH, "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading scheduler configuration: {str(e)}")
        return {"data_sources": {}}

    config, migration_notes = _migrate_legacy_source_ids(config)

    # Backfill: any canonical source the registry knows about but the
    # on-disk config does not yet list (new install vs. older install
    # whose JSON was written before the source existed).
    defaults = _build_default_scheduler_config()["data_sources"]
    sources = config.setdefault("data_sources", {})
    added: List[str] = []
    for key, spec in defaults.items():
        if key not in sources:
            sources[key] = spec
            added.append(key)

    if migration_notes or added:
        try:
            with open(SCHEDULER_CONFIG_PATH, "w") as f:
                json.dump(config, f, indent=2)
            if migration_notes:
                logger.info(
                    "Migrated scheduler config to canonical source IDs: %s",
                    "; ".join(migration_notes),
                )
            if added:
                logger.info(
                    "Backfilled scheduler config with missing source(s): %s",
                    ", ".join(added),
                )
        except Exception as we:
            logger.warning("Failed to persist scheduler config migration: %s", we)

    logger.info(f"Loaded scheduler configuration from {SCHEDULER_CONFIG_PATH}")
    return config

def load_scheduler_status():
    """
    Load scheduler status from global variables or initialize with defaults
    """
    global _scheduler_status, _refresh_timestamps, _refresh_in_progress
    
    # Load configuration
    config = load_scheduler_config()
    
    # Initialize status for each data source
    for source_id, source_config in config.get("data_sources", {}).items():
        if source_id not in _scheduler_status:
            _scheduler_status[source_id] = {
                "last_refresh": None,
                "next_refresh": None,
                "status": "pending",
                "last_error": None,
                "refresh_count": 0,
                "error_count": 0
            }
            
        if source_id not in _refresh_timestamps:
            _refresh_timestamps[source_id] = None
            
        if source_id not in _refresh_in_progress:
            _refresh_in_progress[source_id] = False
            
    logger.info(f"Loaded scheduler status for {len(_scheduler_status)} data sources")

def get_scheduler_status() -> Dict[str, Any]:
    """
    Get the current status of the scheduler
    
    Returns:
        Dictionary with scheduler status
    """
    global _scheduler_running, _scheduler_status
    
    # Load configuration
    config = load_scheduler_config()
    
    # Build status response
    sources_status = []
    for source_id, source_config in config.get("data_sources", {}).items():
        status = _scheduler_status.get(source_id, {})
        
        sources_status.append({
            "id": source_id,
            "description": source_config.get("description", "Unknown data source"),
            "refresh_interval_hours": source_config.get("refresh_interval_hours", 24),
            "last_refresh": status.get("last_refresh"),
            "next_refresh": status.get("next_refresh"),
            "status": status.get("status", "pending"),
            "last_error": status.get("last_error"),
            "refresh_count": status.get("refresh_count", 0),
            "error_count": status.get("error_count", 0),
            "in_progress": _refresh_in_progress.get(source_id, False)
        })
    
    return {
        "running": _scheduler_running,
        "sources": sources_status
    }

def start_scheduler(run_in_background: bool = True) -> bool:
    """
    Start the data refresh scheduler
    
    Args:
        run_in_background: If True, run the scheduler in a background thread
        
    Returns:
        True if the scheduler was started, False if it was already running
    """
    global _scheduler_running, _scheduler_thread
    
    if _scheduler_running:
        logger.info("Scheduler is already running")
        return False
    
    # Load scheduler status
    load_scheduler_status()
    
    # Start the scheduler
    _scheduler_running = True
    
    if run_in_background:
        # Start in a background thread
        _scheduler_thread = threading.Thread(target=scheduler_loop)
        _scheduler_thread.daemon = True
        _scheduler_thread.start()
        logger.info("Started data refresh scheduler in background")
    else:
        # Start in the current thread
        scheduler_loop()
    
    return True

def stop_scheduler() -> bool:
    """
    Stop the data refresh scheduler
    
    Returns:
        True if the scheduler was stopped, False if it wasn't running
    """
    global _scheduler_running
    
    if not _scheduler_running:
        logger.info("Scheduler is not running")
        return False
    
    # Stop the scheduler
    _scheduler_running = False
    logger.info("Stopping data refresh scheduler")
    
    return True

def refresh_now(source: str) -> bool:
    """
    Trigger an immediate refresh of a data source
    
    Args:
        source: The name of the data source to refresh
        
    Returns:
        True if the refresh was started, False if the source wasn't found
    """
    # Load configuration
    config = load_scheduler_config()
    
    # Check if source exists
    if source not in config.get("data_sources", {}):
        logger.error(f"Data source '{source}' not found")
        return False
    
    # Refresh the data source
    success, message = refresh_data_source(source)
    
    if success:
        logger.info(f"Started refresh for {source}")
    else:
        logger.error(f"Error refreshing {source}: {message}")
    
    return success

def refresh_data_source(source: str) -> Tuple[bool, str]:
    """
    Refresh a data source
    
    Args:
        source: The name of the data source to refresh
        
    Returns:
        Tuple of (success, message)
    """
    global _scheduler_status, _refresh_timestamps, _refresh_in_progress
    
    # Load configuration
    config = load_scheduler_config()
    
    # Check if source exists
    if source not in config.get("data_sources", {}):
        return False, f"Data source '{source}' not found"
    
    # Check if already in progress
    if _refresh_in_progress.get(source, False):
        return False, f"Refresh already in progress for '{source}'"
    
    # Get source configuration
    source_config = config["data_sources"][source]
    
    # Mark refresh as in progress
    _refresh_in_progress[source] = True
    
    try:
        # Update status
        if source not in _scheduler_status:
            _scheduler_status[source] = {
                "last_refresh": None,
                "next_refresh": None,
                "status": "pending",
                "last_error": None,
                "refresh_count": 0,
                "error_count": 0
            }
        
        # Get module and function
        module_name = source_config.get("module")
        function_name = source_config.get("function")
        
        if not module_name or not function_name:
            _refresh_in_progress[source] = False
            _scheduler_status[source]["status"] = "error"
            _scheduler_status[source]["last_error"] = "Module or function name not specified"
            _scheduler_status[source]["error_count"] += 1
            return False, "Module or function name not specified"
        
        # Import the module dynamically
        try:
            # Special case for disease surveillance module
            if source == "disease_surveillance":
                from utils.disease_surveillance import clear_disease_cache
                clear_disease_cache()
                success = True
                
            # Special case for SVI data module
            elif source == "svi_data":
                from utils.svi_data import clear_svi_cache
                clear_svi_cache()
                success = True
                
            # Default case: try to import the specified module and function
            else:
                module = __import__(module_name, fromlist=[''])
                function = getattr(module, function_name)
                raw_result = function()

                # Interpret the result. Refresh functions historically
                # returned bool, but the data_source_refresher family
                # returns a results dict (always truthy) that can hide
                # internal failures behind a truthy reference. Treat a
                # dict explicitly: failure if it carries a top-level
                # 'error' key or if every county/source attempt failed
                # (failed > 0 AND success == 0 AND fallback == 0).
                failure_reason: Optional[str] = None
                if isinstance(raw_result, dict):
                    if raw_result.get('error'):
                        failure_reason = str(raw_result['error'])
                    else:
                        success_count = int(raw_result.get('success', 0) or 0)
                        failed_count = int(raw_result.get('failed', 0) or 0)
                        fallback_count = int(raw_result.get('fallback', 0) or 0)
                        if failed_count > 0 and success_count == 0 and fallback_count == 0:
                            failure_reason = (
                                f"All {failed_count} refresh attempts failed; "
                                f"see results['errors'] for details"
                            )
                    success = failure_reason is None
                else:
                    success = bool(raw_result)
                    if not success:
                        failure_reason = "Function returned False"

            # Update status on success
            if success:
                now = datetime.now()
                refresh_interval = timedelta(hours=source_config.get("refresh_interval_hours", 24))
                next_refresh = now + refresh_interval
                
                _scheduler_status[source]["last_refresh"] = now.isoformat()
                _scheduler_status[source]["next_refresh"] = next_refresh.isoformat()
                _scheduler_status[source]["status"] = "success"
                _scheduler_status[source]["last_error"] = None
                _scheduler_status[source]["refresh_count"] += 1
                _refresh_timestamps[source] = now
                
                _refresh_in_progress[source] = False
                return True, "Refresh completed successfully"
            else:
                # Update status on failure
                _scheduler_status[source]["status"] = "error"
                _scheduler_status[source]["last_error"] = failure_reason or "Refresh failed"
                _scheduler_status[source]["error_count"] += 1

                _refresh_in_progress[source] = False
                return False, failure_reason or "Refresh failed"
                
        except Exception as e:
            # Update status on exception
            _scheduler_status[source]["status"] = "error"
            _scheduler_status[source]["last_error"] = str(e)
            _scheduler_status[source]["error_count"] += 1
            
            _refresh_in_progress[source] = False
            return False, str(e)
            
    except Exception as e:
        # Update status on outer exception
        if source in _scheduler_status:
            _scheduler_status[source]["status"] = "error"
            _scheduler_status[source]["last_error"] = str(e)
            _scheduler_status[source]["error_count"] += 1
        
        _refresh_in_progress[source] = False
        return False, str(e)

def scheduler_loop():
    """
    Main scheduler loop
    """
    global _scheduler_running, _scheduler_status, _refresh_timestamps
    
    logger.info("Starting scheduler loop")
    
    # Initialize status
    load_scheduler_status()
    
    while _scheduler_running:
        try:
            # Load configuration
            config = load_scheduler_config()
            
            # Get current time
            now = datetime.now()
            logger.info(f"Checking all data sources for refresh at {now.isoformat()}")
            
            # Check each data source
            for source_id, source_config in config.get("data_sources", {}).items():
                # Skip if refresh is already in progress
                if _refresh_in_progress.get(source_id, False):
                    continue
                
                # Get last refresh timestamp
                last_refresh = _refresh_timestamps.get(source_id)
                
                # Calculate next refresh time
                refresh_interval = timedelta(hours=source_config.get("refresh_interval_hours", 24))
                
                # Check if refresh is needed
                if last_refresh is None or now - last_refresh >= refresh_interval:
                    logger.info(f"Refreshing data source: {source_id}")
                    
                    # Refresh in a separate thread.
                    # Bind source_id as a default arg to avoid the classic
                    # late-binding closure bug: if the loop variable changes
                    # before the thread runs, the lambda would otherwise see
                    # the most recent value of source_id rather than the one
                    # active when the thread was created.
                    thread = threading.Thread(
                        target=refresh_data_source,
                        args=(source_id,),
                    )
                    thread.daemon = True
                    thread.start()
                    
            # Sleep for a while
            time.sleep(300)  # Check every 5 minutes
            
        except (ValueError, KeyError, TypeError, OSError, RuntimeError) as e:
            error_type = type(e).__name__
            logger.error(f"Error in scheduler loop ({error_type}): {str(e)}")
            time.sleep(60)  # Wait a bit longer on error
        except Exception as e:
            # Catch-all for unexpected errors to prevent scheduler crash
            logger.critical(f"Unexpected error in scheduler loop: {type(e).__name__}: {str(e)}")
            time.sleep(300)  # Wait longer for unexpected errors
    
    logger.info("Scheduler loop stopped")

def initialize():
    """Initialize the data refresh scheduler module"""
    # Load configuration
    load_scheduler_config()
    
    # Load status
    load_scheduler_status()
    
    logger.info("Data refresh scheduler initialized")