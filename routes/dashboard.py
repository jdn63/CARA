"""
Dashboard routes for CARA application.

These routes handle the main dashboard functionality:
- Jurisdiction-specific risk dashboards
- Print summaries and action plans
- Historical data for jurisdictions
"""

import logging
import time
import tempfile
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, send_file, flash, jsonify
from utils.data_processor import process_risk_data, get_historical_risk_data
from utils.predictive_analysis import RiskPredictor
from utils.metadata_config import EXCLUDED_RISK_FIELDS
from utils.risk_alignment import compute_display_scores
from utils.discipline import get_active_discipline, discipline_label

# Set up logger for this module
logger = logging.getLogger(__name__)

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Special ID mapping for known problematic IDs
ID_MAPPING = {
    '01': '101',
    '02': '102', 
    '03': '103',
    '04': '104',
    '05': '105',
    '06': '106',
    '07': '107',
    '08': '108',
    '09': '109',
}

def sanitize_risk_data(risk_data):
    """
    Process risk data to ensure proper handling of metadata fields and numerical values.
    """
    # Make a copy to avoid modifying the original
    if risk_data is None:
        return {}
    
    # Skip metadata fields when converting to float
    natural_hazards = risk_data.get('natural_hazards', {})
    
    for hazard in list(natural_hazards.keys()):
        # Skip metadata fields that shouldn't be treated as risk values
        if hazard in EXCLUDED_RISK_FIELDS:
            continue
            
        try:
            risk_data['natural_hazards'][hazard] = float(risk_data['natural_hazards'][hazard])
        except (ValueError, TypeError):
            risk_data['natural_hazards'][hazard] = 0.0
            logger.warning(f"Invalid hazard risk value for {hazard}, defaulting to 0.0")
    
    # Ensure total_risk_score is a float and rounded to 2 decimal places
    try:
        risk_data['total_risk_score'] = round(float(risk_data['total_risk_score']), 2)
    except (ValueError, TypeError, KeyError):
        risk_data['total_risk_score'] = 0.5
        logger.warning(f"Invalid total_risk_score, defaulting to 0.5")
    
    # Ensure health_risk field exists
    if 'health_risk' not in risk_data:
        # Try to extract from health_metrics 
        if 'health_metrics' in risk_data and isinstance(risk_data['health_metrics'], dict):
            if 'risk_score' in risk_data['health_metrics']:
                risk_data['health_risk'] = risk_data['health_metrics']['risk_score']
            elif 'metrics' in risk_data['health_metrics']:
                # Calculate average if individual metrics are available
                health_metrics = risk_data['health_metrics']['metrics']
                if health_metrics and isinstance(health_metrics, dict):
                    # Filter out None values and convert to float
                    valid_values = [float(v) for v in health_metrics.values() if v is not None and isinstance(v, (int, float))]
                    if valid_values:
                        risk_data['health_risk'] = sum(valid_values) / len(valid_values)
                    else:
                        risk_data['health_risk'] = 0.0
                else:
                    risk_data['health_risk'] = 0.0
            else:
                risk_data['health_risk'] = 0.0
        else:
            risk_data['health_risk'] = 0.0
    
    return risk_data


@dashboard_bp.route('/dashboard/<jurisdiction_id>')
def dashboard(jurisdiction_id):
    """Main dashboard for jurisdiction risk assessment"""
    try:
        # TRIBAL HIDE: Block direct URL access to Tribal dashboards while
        # Tribal data sovereignty protocols are finalized. To restore Tribal
        # access, remove this block (the comment and the if/flash/redirect).
        # See .local/tribal_access_reversal.md for full reversal instructions.
        if str(jurisdiction_id).startswith('T'):
            flash(
                "Tribal jurisdiction dashboards are temporarily unavailable "
                "while we finalize data access protocols with our Tribal partners.",
                "info"
            )
            return redirect(url_for('public.index'))

        # Check if this ID is in our special mapping
        if jurisdiction_id in ID_MAPPING:
            mapped_id = ID_MAPPING[jurisdiction_id]
            logger.info(f"Using special ID mapping: {jurisdiction_id} -> {mapped_id}")
            jurisdiction_id = mapped_id
            
        from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

        # Discipline-aware cache key (v6, 2026-05-20). Phase 1 introduces the
        # global PH/EM toggle; the cached payload differs by discipline
        # because process_risk_data() applies different weights, so the
        # key MUST include discipline. Bumped to v7 when the EM composite
        # gained the infectious_disease 5% wiring, and to v8 when the
        # hazmat_industrial resilience signals changed (CHEMPACK removal,
        # statute-only team list) so pre-fix cached composites are
        # invalidated cleanly at deploy.
        discipline = get_active_discipline()
        full_cache_key = f"dashboard_full_v12_{discipline}_{jurisdiction_id}"
        cached_context = get_from_persistent_cache(full_cache_key, max_age_days=1)

        if cached_context:
            logger.info(f"Using fully cached dashboard context for jurisdiction {jurisdiction_id} (discipline={discipline})")
            return render_template('dashboard.html',
                                 risk_data=cached_context['risk_data'],
                                 alerts=cached_context['alerts'],
                                 current_conditions=cached_context['current_conditions'],
                                 predictions=cached_context['predictions'],
                                 temporal_risk_data=cached_context['temporal_risk_data'],
                                 active_discipline=discipline,
                                 discipline_label=discipline_label(discipline),
                                 now=datetime.now())

        logger.info(f"Generating fresh dashboard data for jurisdiction {jurisdiction_id} (discipline={discipline})")
        risk_data = process_risk_data(jurisdiction_id, discipline=discipline)
        risk_data = sanitize_risk_data(risk_data)
        
        if not risk_data:
            logger.error(f"No risk data available for jurisdiction ID: {jurisdiction_id}")
            return render_template('error.html', 
                           message="No risk data available for the selected jurisdiction.")
        
        alerts = []
        current_conditions = None
        
        try:
            predictor = RiskPredictor()
            predictions = predictor.generate_predictions(jurisdiction_id, risk_data)
            logger.info(f"Retrieved predictive analysis for jurisdiction ID: {jurisdiction_id}")
        except Exception as e:
            logger.error(f"Error retrieving predictive analysis: {str(e)}")
            predictions = {
                'future_risks': {
                    'natural_hazards_risk': 0.0,
                    'health_risk': 0.0,
                    'active_shooter_risk': 0.0
                },
                'trend_strength': {'overall': 'stable'},
                'time_series': []
            }
        
        from utils.temporal_risk import TemporalRiskComponent
        from utils.request_context import cache_only_context

        natural_hazard_types = {
            'flood': risk_data.get('flood_risk', 0.3),
            'tornado': risk_data.get('tornado_risk', 0.25), 
            'winter_storm': risk_data.get('winter_storm_risk', 0.2),
            'extreme_heat': risk_data.get('extreme_heat_risk', 0.15),
            'thunderstorm': risk_data.get('thunderstorm_risk', 0.1)
        }
        
        health_score = risk_data.get('health_risk', 0.3)
        active_shooter_score = risk_data.get('active_shooter_risk', 0.2)
        
        temporal_risk_data = {}

        # Cache-only request-path guarantee: every TemporalRiskComponent
        # call must run inside cache_only_context() so that the
        # infectious-disease acute path (_check_disease_outbreaks ->
        # NSSP/disease_surveillance fetchers) cannot trigger live HTTP on
        # a cold cache. process_risk_data() above already exited its own
        # cache_only_context; we re-enter for this block.
        with cache_only_context():
            for hazard_type, base_score in natural_hazard_types.items():
                try:
                    county_name = risk_data.get('county', risk_data.get('county_name', 'Unknown County'))
                    temporal_component = TemporalRiskComponent(hazard_type, jurisdiction_id, county_name)
                    temporal_component.calculate_components()
                    temporal_risk_data[hazard_type] = {
                        'composite_score': round(temporal_component.get_composite_score(), 3),
                        'temporal_components': {
                            'baseline': round(temporal_component.baseline, 3),
                            'seasonal': round(temporal_component.seasonal, 3),
                            'trend': round(temporal_component.trend, 3),
                            'acute': round(temporal_component.acute, 3),
                            'trend_metadata': getattr(temporal_component, '_trend_metadata', None)
                        }
                    }
                except Exception as e:
                    logger.error(f"Error generating temporal component for {hazard_type}: {str(e)}")
                    temporal_risk_data[hazard_type] = {
                        'composite_score': round(base_score, 3),
                        'estimated_split': True,
                        'temporal_components': {
                            'baseline': round(base_score * 0.85, 3),
                            'seasonal': round(base_score * 0.10, 3),
                            'trend': round(base_score * 0.05, 3),
                            'acute': 0.0
                        }
                    }

            try:
                county_name = risk_data.get('county', risk_data.get('county_name', 'Unknown County'))
                health_temporal = TemporalRiskComponent('infectious_disease', jurisdiction_id, county_name)
                health_temporal.calculate_components()
                temporal_risk_data['infectious_disease'] = {
                    'composite_score': round(health_temporal.get_composite_score(), 3),
                    'temporal_components': {
                        'baseline': round(health_temporal.baseline, 3),
                        'seasonal': round(health_temporal.seasonal, 3),
                        'trend': round(health_temporal.trend, 3),
                        'acute': round(health_temporal.acute, 3),
                        'trend_metadata': getattr(health_temporal, '_trend_metadata', None)
                    }
                }
                active_shooter_temporal = TemporalRiskComponent('active_shooter', jurisdiction_id, county_name)
                active_shooter_temporal.calculate_components()
                temporal_risk_data['active_shooter'] = {
                    'composite_score': round(active_shooter_temporal.get_composite_score(), 3),
                    'temporal_components': {
                        'baseline': round(active_shooter_temporal.baseline, 3),
                        'seasonal': round(active_shooter_temporal.seasonal, 3),
                        'trend': round(active_shooter_temporal.trend, 3),
                        'acute': round(active_shooter_temporal.acute, 3),
                        'trend_metadata': getattr(active_shooter_temporal, '_trend_metadata', None)
                    }
                }
            except Exception as e:
                logger.error(f"Error generating health/active shooter temporal components: {str(e)}")
                temporal_risk_data['infectious_disease'] = {
                    'composite_score': round(health_score, 3),
                    'estimated_split': True,
                    'temporal_components': {'baseline': round(health_score * 0.85, 3), 'seasonal': round(health_score * 0.10, 3), 'trend': 0.0, 'acute': round(health_score * 0.05, 3), 'trend_metadata': None}
                }
                temporal_risk_data['active_shooter'] = {
                    'composite_score': round(active_shooter_score, 3),
                    'estimated_split': True,
                    'temporal_components': {'baseline': round(active_shooter_score * 0.85, 3), 'seasonal': round(active_shooter_score * 0.10, 3), 'trend': round(active_shooter_score * 0.05, 3), 'acute': 0.0}
                }
        
        logger.info(f"Generated temporal risk data for {len(temporal_risk_data)} risk types")

        # Enrich each entry with sparkline + plain-language posture payload
        # consumed by templates/dashboard/_bsta_temporal.html. Pure-Python,
        # no external fetches -- safe inside the cache-only request path.
        try:
            from utils.bsta_visualization import build_bsta_visualization
            build_bsta_visualization(temporal_risk_data)
        except Exception as viz_err:
            logger.warning(f"BSTA visualization enrichment failed: {viz_err}")

        set_in_persistent_cache(full_cache_key, {
            'risk_data': risk_data,
            'alerts': alerts,
            'current_conditions': current_conditions,
            'predictions': predictions,
            'temporal_risk_data': temporal_risk_data
        })
        
        return render_template('dashboard.html',
                             risk_data=risk_data,
                             alerts=alerts,
                             current_conditions=current_conditions,
                             predictions=predictions,
                             temporal_risk_data=temporal_risk_data,
                             active_discipline=discipline,
                             discipline_label=discipline_label(discipline),
                             now=datetime.now())
        
    except Exception as e:
        import traceback, sys
        tb = traceback.format_exc()
        logger.error(
            f"Error loading dashboard for jurisdiction {jurisdiction_id}: {str(e)}\n{tb}"
        )
        print(f"[DASHBOARD ERROR] {jurisdiction_id}: {e}\n{tb}", file=sys.stderr, flush=True)
        return render_template('error.html',
                           error=f"An error occurred while loading the dashboard for {jurisdiction_id}: {e}")


@dashboard_bp.route('/em-comparison-export')
def em_comparison_export():
    """Generate downloadable Excel comparing PH vs EM risk scores for all jurisdictions"""
    try:
        from utils.em_comparison_export import generate_em_comparison_export, load_precomputed_scores, precompute_comparison_scores

        scores = load_precomputed_scores()
        if not scores:
            logger.info("No pre-computed EM comparison scores found, computing synchronously")
            precompute_comparison_scores()
            scores = load_precomputed_scores()
            if not scores:
                return render_template('error.html',
                                   message="Unable to generate comparison data. Please try again.")

        logger.info("Generating EM comparison Excel from pre-computed scores")
        excel_path = generate_em_comparison_export()
        download_filename = f"CARA_PH_vs_EM_Comparison_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Error generating EM comparison export: {str(e)}")
        logger.exception("Full traceback:")
        return render_template('error.html',
                           message="An error occurred while generating the comparison export. Please try again.")


@dashboard_bp.route('/print-summary/<jurisdiction_id>')
def print_summary(jurisdiction_id):
    """Generate printable risk summary for a jurisdiction"""
    try:
        # Check if this ID is in our special mapping
        if jurisdiction_id in ID_MAPPING:
            mapped_id = ID_MAPPING[jurisdiction_id]
            logger.info(f"Using special ID mapping for print summary: {jurisdiction_id} -> {mapped_id}")
            jurisdiction_id = mapped_id
            
        # Get risk data for the selected jurisdiction
        discipline = get_active_discipline()
        logger.info(f"Generating print summary for jurisdiction {jurisdiction_id} (discipline={discipline})")
        risk_data = process_risk_data(jurisdiction_id, discipline=discipline)
        risk_data = sanitize_risk_data(risk_data)
        
        if not risk_data:
            logger.error(f"No risk data available for print summary: {jurisdiction_id}")
            return render_template('error.html', 
                           message="No risk data available for the selected jurisdiction.")
        
        # Add current date for print summary
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Compute canonical display scores, then build the simplified
        # plain-language top-risk cards the Summary page now renders.
        display_scores = compute_display_scores(risk_data)
        from utils.summary_content import (
            build_top_risk_cards, get_summary_page_meta,
        )
        summary_cards = build_top_risk_cards(
            display_scores, discipline, limit=5, risk_data=risk_data,
        )
        page_meta = get_summary_page_meta(discipline)

        # Build the Back-to-Dashboard link. In EM mode, if the
        # jurisdiction maps to a Wisconsin county (i.e. is reachable via
        # /em-dashboard/<slug>), prefer the slug URL so the user lands
        # back on the EM county view they came from instead of the
        # underlying LHD URL.
        back_url = f"/dashboard/{risk_data.get('jurisdiction_id', jurisdiction_id)}"
        if discipline == 'em':
            from utils.em_counties import get_slug_for_jurisdiction_id
            slug = get_slug_for_jurisdiction_id(
                risk_data.get('jurisdiction_id', jurisdiction_id)
            )
            if slug:
                back_url = f"/em-dashboard/{slug}"

        return render_template('print_summary.html', 
                             risk_data=risk_data,
                             summary_cards=summary_cards,
                             page_meta=page_meta,
                             current_date=current_date,
                             active_discipline=discipline,
                             discipline_label=discipline_label(discipline),
                             back_url=back_url)
        
    except Exception as e:
        logger.error(f"Error generating print summary for jurisdiction {jurisdiction_id}: {str(e)}")
        return render_template('error.html', 
                           message="An error occurred while generating the print summary. Please try again.")


@dashboard_bp.route('/action-plan/<jurisdiction_id>')
def action_plan(jurisdiction_id):
    """Generate action plan for jurisdiction"""
    try:
        # Check if this ID is in our special mapping
        if jurisdiction_id in ID_MAPPING:
            mapped_id = ID_MAPPING[jurisdiction_id]
            logger.info(f"Using special ID mapping for action plan: {jurisdiction_id} -> {mapped_id}")
            jurisdiction_id = mapped_id
            
        # Get risk data for the selected jurisdiction. NOTE: Action plan
        # CONTENT remains Public-Health-tailored until Phase 2; EM mode
        # only reweights the scores driving the prioritization. The EM
        # banner in base.html surfaces this caveat to the user.
        discipline = get_active_discipline()
        logger.info(f"Generating action plan for jurisdiction {jurisdiction_id} (discipline={discipline})")
        risk_data = process_risk_data(jurisdiction_id, discipline=discipline)
        risk_data = sanitize_risk_data(risk_data)
        
        if not risk_data:
            logger.error(f"No risk data available for action plan: {jurisdiction_id}")
            return render_template('error.html', 
                           message="No risk data available for the selected jurisdiction.")
        
        # Compute canonical display scores for consistent alignment
        top_risks = compute_display_scores(risk_data)
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Discipline-aware action plan content layer. v28.3 piloted on
        # extreme_heat; Task #9 extended the pattern to all remaining
        # domains. Each domain has its own data/action_plans/<domain>.yaml
        # with PH + EM activities and source citations.
        from utils.action_plan_content import get_domain_action_plan
        _ap_domains = (
            'extreme_heat', 'flood', 'tornado', 'winter_storm',
            'thunderstorm', 'straight_line_wind',
            'dam_failure', 'vector_borne_disease',
            'air_quality', 'active_shooter', 'cybersecurity', 'health',
            'hazmat_industrial', 'hazmat_agricultural',
        )
        domain_action_plans = {
            d: get_domain_action_plan(d, discipline) for d in _ap_domains
        }

        return render_template('action_plan.html', 
                             risk_data=risk_data,
                             top_risks=top_risks,
                             excluded_fields=EXCLUDED_RISK_FIELDS,
                             current_date=current_date,
                             active_discipline=discipline,
                             discipline_label=discipline_label(discipline),
                             domain_action_plans=domain_action_plans,
                             action_plan_feedback_email='jdn63@georgetown.edu')
        
    except Exception as e:
        logger.error(f"Error generating action plan for jurisdiction {jurisdiction_id}: {str(e)}")
        return render_template('error.html', 
                           message="An error occurred while generating the action plan. Please try again.")


@dashboard_bp.route('/kp-hva-export/<jurisdiction_id>')
def kp_hva_export(jurisdiction_id):
    """Generate Kaiser Permanente HVA Excel export for a jurisdiction"""
    try:
        if jurisdiction_id in ID_MAPPING:
            mapped_id = ID_MAPPING[jurisdiction_id]
            logger.info(f"Using special ID mapping for KP HVA export: {jurisdiction_id} -> {mapped_id}")
            jurisdiction_id = mapped_id

        import os
        from utils.kp_hva_export import generate_kp_hva_jurisdiction_export

        logger.info(f"Generating KP HVA export for jurisdiction {jurisdiction_id}")

        risk_data = process_risk_data(jurisdiction_id)
        risk_data = sanitize_risk_data(risk_data)

        if not risk_data:
            logger.error(f"No risk data available for KP HVA export: {jurisdiction_id}")
            return render_template('error.html',
                           message="No risk data available for the selected jurisdiction.")

        excel_file_path = generate_kp_hva_jurisdiction_export(risk_data)

        if not excel_file_path or not os.path.exists(excel_file_path):
            logger.error(f"Failed to generate KP HVA file for jurisdiction {jurisdiction_id}")
            return render_template('error.html',
                           message="Failed to generate Kaiser Permanente HVA export file.")

        jurisdiction_name = risk_data.get('location', f'Jurisdiction_{jurisdiction_id}')
        safe_name = jurisdiction_name.replace(' ', '_').replace('/', '-')
        download_filename = f"KP_HVA_{safe_name}_{datetime.now().strftime('%Y-%m-%d')}.xlsm"

        return send_file(
            excel_file_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/vnd.ms-excel.sheet.macroEnabled.12'
        )

    except Exception as e:
        import traceback
        logger.error(f"Error generating KP HVA export for jurisdiction {jurisdiction_id}: {str(e)}\n{traceback.format_exc()}")
        return render_template('error.html',
                           message="An error occurred while generating the Kaiser Permanente HVA export. Please try again.")


@dashboard_bp.route('/current-snapshot/<jurisdiction_id>')
@dashboard_bp.route('/historical-data/<jurisdiction_id>')
def get_historical_data(jurisdiction_id):
    """Get current risk data snapshot for a jurisdiction.
    
    Returns a single-point snapshot of current risk scores, not historical time-series.
    The /historical-data path is preserved for backward compatibility but /current-snapshot
    is the canonical name.
    """
    try:
        if jurisdiction_id in ID_MAPPING:
            mapped_id = ID_MAPPING[jurisdiction_id]
            logger.info(f"Using special ID mapping for historical data: {jurisdiction_id} -> {mapped_id}")
            jurisdiction_id = mapped_id

        try:
            risk_data = process_risk_data(jurisdiction_id)
            risk_data = sanitize_risk_data(risk_data)
        except Exception as e:
            logger.error(f"Error loading risk data for {jurisdiction_id}: {str(e)}")
            return jsonify({
                'error': 'Risk data unavailable for this jurisdiction.'
            }), 503

        from datetime import datetime
        current_year = datetime.now().year

        # Real computed scores, unclamped and unfabricated. Missing
        # domains are reported as null, never invented.
        data_point = {
            'year': current_year,
            'total_risk_score': risk_data.get('total_risk_score'),
            'natural_hazards_risk': risk_data.get('natural_hazards_risk'),
            'health_risk': risk_data.get('health_risk'),
            'active_shooter_risk': risk_data.get('active_shooter_risk'),
        }

        return [data_point]
    except Exception as e:
        logger.error(f"Error getting risk data: {str(e)}")
        return render_template('error.html', 
                           message="An error occurred while loading risk data. Please try again.")