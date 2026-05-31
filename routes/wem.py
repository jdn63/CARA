"""
WEM (Wisconsin Emergency Management) region routes for CARA.

Mirrors routes/herc.py but for the 6 WEM regions, using EM discipline
weights. Phase 1 reuses the regional dashboard template by passing a
region_kind context variable so labels and links adapt without forking.
"""

import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, session

from utils.wem_data import get_all_wem_regions, get_wem_statistics
from utils.wem_risk_aggregator import get_wem_region_risk


def _pin_em_mode():
    """WEM views are inherently Emergency Management. Pin the session so
    the nav toggle and EM banner reflect the true mode even when the
    user lands on a WEM URL directly (no ?discipline=em query param).
    Without this, scores would be EM-computed while the chrome would
    misleadingly say Public Health."""
    try:
        session['discipline'] = 'em'
    except Exception:
        pass

logger = logging.getLogger(__name__)

wem_bp = Blueprint('wem', __name__)


def _current_season() -> str:
    m = datetime.now().month
    if m in (12, 1, 2):
        return 'Winter'
    if m in (3, 4, 5):
        return 'Spring'
    if m in (6, 7, 8):
        return 'Summer'
    return 'Fall'


@wem_bp.route('/wem-dashboard')
@wem_bp.route('/wem-dashboard/')
@wem_bp.route('/wem-region')
@wem_bp.route('/wem-region/')
def wem_dashboard_redirect():
    logger.info("WEM dashboard accessed without region ID, redirecting to index")
    return redirect(url_for('public.index'))


# /wem-region/<id> is the original planned URL contract from the
# session plan (Task #7). /wem-dashboard/<id> mirrors the existing
# /herc-dashboard/<id> shape and is what links inside the app point
# to. Both names route to the same view so external links and docs
# referencing /wem-region continue to work.
@wem_bp.route('/wem-dashboard/<wem_id>')
@wem_bp.route('/wem-region/<wem_id>')
def wem_dashboard(wem_id):
    """Render WEM region dashboard using EM-weighted aggregated risk."""
    try:
        _pin_em_mode()
        logger.info(f"Loading WEM dashboard for region {wem_id} (discipline pinned to em)")

        region_info = get_wem_statistics(wem_id)
        if not region_info:
            logger.error(f"No WEM data for region ID: {wem_id}")
            return render_template(
                'error.html',
                message="No WEM data available for the requested region."
            )

        risk_data = get_wem_region_risk(wem_id)
        if not risk_data:
            logger.error(f"Failed to calculate EM risk for WEM region {wem_id}")
            return render_template(
                'error.html',
                message="Unable to calculate risk data for the requested WEM region."
            )

        risk_data.update({
            'location': region_info.get('name', f'WEM Region {wem_id}'),
            'jurisdiction_id': wem_id,
            'county_name': region_info.get('name', f'WEM Region {wem_id}'),
            'statistics': region_info.get('statistics', {}),
        })

        temporal_risk_data = risk_data.get('temporal_risk_data', {})
        all_wem_regions = get_all_wem_regions()

        # Phase 1: reuse herc_dashboard.html via context variables that
        # parametrize the header labels and URLs. Avoids forking the
        # 669-line regional dashboard template wholesale.
        return render_template(
            'herc_dashboard.html',
            risk_data=risk_data,
            region_kind='WEM',
            discipline_label='Emergency Management',
            print_url_prefix='/wem-print-summary',
            export_url=None,  # No KP HVA export for WEM in Phase 1
            show_hpp_section=False,  # Hospital Preparedness section is HERC-only
            herc_regions=all_wem_regions,
            current_herc_id=wem_id,
            temporal_risk_data=temporal_risk_data,
            current_season=_current_season(),
            now=datetime.now(),
            # Force EM chrome regardless of the (now-pinned) session value
            # so the navbar toggle and EM banner are truthful on this page.
            active_discipline='em',
        )

    except Exception as e:
        logger.error(f"Error loading WEM dashboard for {wem_id}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return render_template(
            'error.html',
            message="An error occurred while loading the WEM dashboard. Please try again."
        )


@wem_bp.route('/wem-print-summary/<wem_id>')
def wem_print_summary(wem_id):
    """Printable summary for a WEM region."""
    try:
        _pin_em_mode()
        region_info = get_wem_statistics(wem_id)
        if not region_info:
            return render_template(
                'error.html',
                message="No WEM data available for the requested region."
            )

        risk_data = get_wem_region_risk(wem_id)
        if not risk_data:
            return render_template(
                'error.html',
                message="Unable to calculate risk data for the requested WEM region."
            )

        risk_data.update({
            'location': region_info.get('name', f'WEM Region {wem_id}'),
            'statistics': region_info.get('statistics', {}),
        })

        # Phase 1: WEM print summary reuses the HERC print template via the
        # region_kind variable. herc_id alias on risk_data preserves links.
        return render_template(
            'herc_print_summary.html',
            risk_data=risk_data,
            current_date=datetime.now().strftime("%B %d, %Y"),
            region_kind='WEM',
            discipline_label='Emergency Management',
            active_discipline='em',
            dashboard_url_prefix='/wem-dashboard',
        )
    except Exception as e:
        logger.error(f"Error generating WEM print summary for {wem_id}: {e}")
        return render_template(
            'error.html',
            message="An error occurred while generating the print summary."
        )
