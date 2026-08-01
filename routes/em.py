"""EM (Emergency Management) county dashboard routes for CARA.

Phase 2 of the discipline-tailored landing surface. PH lands on
/dashboard/<jurisdiction_id> with all 84 LHD jurisdictions in the
picker; EM lands on /em-dashboard/<county_slug> with all 72 Wisconsin
counties.

The EM county dashboard reuses the existing dashboard view in
routes/dashboard.py by resolving the county slug to its canonical
county LHD jurisdiction id and calling the dashboard function inline
with EM discipline pinned. This keeps the /em-dashboard URL meaningful
to the user while reusing 100% of the dashboard logic, weighting,
cache key, and template; the only practical differences are EM weights
applied by process_risk_data() and the streamlined biological panel
rendered when active_discipline == 'em' (see
templates/dashboard/_category_biological.html).

Tribal jurisdictions are filtered out before this layer (see
TRIBAL HIDE stopgap in utils/data_processor.py).
"""

import logging
from flask import Blueprint, redirect, url_for, g, flash

from utils.em_counties import get_county_for_slug
from utils.data_processor import get_wi_jurisdictions


logger = logging.getLogger(__name__)


def _resolve_county_jurisdiction_id(county_name):
    """Resolve a Wisconsin county name to its primary LHD jurisdiction id
    from the live jurisdictions list.

    The legacy `get_county_id()` returns a hardcoded zero-padded county
    code (e.g. Calumet -> '08') that does NOT match the real jurisdiction
    ids in `get_wi_jurisdictions()` (Calumet's primary LHD is id '10').
    Passing the hardcoded code into the dashboard view hits the broken
    ID_MAPPING shim in routes/dashboard.py and surfaces as
    "Jurisdiction with ID 108 not found" to the user.

    Returns the primary LHD id as a string, or None if no LHD covers
    the county.
    """
    if not county_name:
        return None
    target = county_name.strip().lower()
    candidates = [
        j for j in get_wi_jurisdictions()
        if (j.get('county') or '').strip().lower() == target
    ]
    if not candidates:
        return None
    # Prefer the LHD flagged primary; fall back to the first match.
    primary = next((j for j in candidates if j.get('primary')), candidates[0])
    return str(primary.get('id'))

em_bp = Blueprint('em', __name__)


def _pin_em_mode():
    """EM county views are inherently Emergency Management. Force EM for
    THIS request only via flask.g, without writing the session. That way
    the dashboard renders with EM weights, the EM banner, and the
    streamlined biological panel, but visiting an EM county view does
    not silently flip the user's session into EM mode and leak into the
    next /dashboard/<jid> request. Persistent EM mode is set only by the
    explicit nav toggle (?discipline=em), which still writes the
    session in utils.discipline.get_active_discipline().

    REQUEST SCOPE (v28.7 review fix #12): flask.g is a request-local
    proxy backed by the application context which Flask resets at the
    end of every request via app_ctx_globals_class. It is NOT shared
    across worker threads or across requests. Setting g.forced_discipline
    here cannot leak into another user's session or into the next
    request on the same worker; the next request starts with a fresh
    g. Verified manually against the Flask source (flask/ctx.py)."""
    g.forced_discipline = 'em'


@em_bp.route('/em-dashboard')
@em_bp.route('/em-dashboard/')
def em_dashboard_redirect():
    """No county specified -- send the user back to the picker."""
    logger.info("EM dashboard accessed without county slug, redirecting to index")
    return redirect(url_for('public.index'))


@em_bp.route('/em-dashboard/<county_slug>')
def em_dashboard(county_slug):
    """Render the EM-weighted dashboard for a Wisconsin county.

    Resolves the slug to a county name, then to its canonical county
    LHD jurisdiction id, pins EM mode, and delegates to the existing
    dashboard view. The view's discipline-aware cache key
    (dashboard_full_v19_em_<jid>) keeps EM and PH dashboards cached
    independently.
    """
    _pin_em_mode()

    county_name = get_county_for_slug(county_slug)
    if not county_name:
        logger.warning(f"Unknown EM county slug: {county_slug}")
        flash(
            "That Wisconsin county was not recognized. Please pick one from the list.",
            "warning",
        )
        return redirect(url_for('public.index'))

    jurisdiction_id = _resolve_county_jurisdiction_id(county_name)
    if not jurisdiction_id:
        logger.warning(
            f"EM dashboard: no primary LHD found for county={county_name}"
        )
        flash(
            "No public health agency is currently mapped to that county. "
            "Please pick another county from the list.",
            "warning",
        )
        return redirect(url_for('public.index'))
    logger.info(
        f"EM dashboard: county={county_name} slug={county_slug} -> "
        f"jurisdiction_id={jurisdiction_id} (discipline pinned to em)"
    )

    # Reuse the existing dashboard view inline. Importing at call time
    # avoids a circular import at module load.
    from routes.dashboard import dashboard as dashboard_view
    return dashboard_view(jurisdiction_id)


@em_bp.route('/em-print-summary/<county_slug>')
def em_print_summary(county_slug):
    """Printable EM county summary. Delegates to the existing print
    summary view with EM pinned and the county mapped to its canonical
    LHD jurisdiction id."""
    _pin_em_mode()

    county_name = get_county_for_slug(county_slug)
    if not county_name:
        logger.warning(f"Unknown EM county slug on print summary: {county_slug}")
        flash(
            "That Wisconsin county was not recognized. Please pick one from the list.",
            "warning",
        )
        return redirect(url_for('public.index'))

    jurisdiction_id = _resolve_county_jurisdiction_id(county_name)
    if not jurisdiction_id:
        logger.warning(
            f"EM print summary: no primary LHD found for county={county_name}"
        )
        flash(
            "No public health agency is currently mapped to that county.",
            "warning",
        )
        return redirect(url_for('public.index'))
    logger.info(
        f"EM print summary: county={county_name} -> jurisdiction_id={jurisdiction_id}"
    )

    from routes.dashboard import print_summary as print_summary_view
    return print_summary_view(jurisdiction_id)
