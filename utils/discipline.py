"""Discipline resolution for CARA.

Single source of truth for whether the current request is in Public
Health (default) or Emergency Management mode. Used by routes to pick
the right weights for process_risk_data() and by templates to adapt
labels via the active_discipline / discipline_label context variables
injected in core.py.

Resolution order on each request:
  1. g.forced_discipline set by a route that is inherently one discipline
     (e.g. /em-dashboard/<slug>, /em-print-summary/<slug>). Request-scoped
     only; never persisted to the session, so visiting an EM county view
     does not silently flip the next /dashboard/<jid> hit into EM mode.
  2. ?discipline=em or ?discipline=public_health in the URL. Wins over
     session and is persisted to the session so subsequent navigation
     keeps the choice (this is the global nav toggle path).
  3. session['discipline'] from a prior request (set by path 2).
  4. DEFAULT = 'public_health'.

Anything outside VALID is ignored (treated as if absent).
"""

from flask import session, request, has_request_context, g

VALID = {'public_health', 'em'}
DEFAULT = 'public_health'


def get_active_discipline() -> str:
    if not has_request_context():
        return DEFAULT
    try:
        forced = getattr(g, 'forced_discipline', None)
        if forced in VALID:
            return forced
        q = request.args.get('discipline')
        if q in VALID:
            try:
                session['discipline'] = q
            except Exception:
                pass
            return q
        sd = session.get('discipline')
        if sd in VALID:
            return sd
    except Exception:
        pass
    return DEFAULT


def discipline_label(discipline: str = None) -> str:
    d = discipline or get_active_discipline()
    return 'Emergency Management' if d == 'em' else 'Public Health'


def discipline_short_label(discipline: str = None) -> str:
    d = discipline or get_active_discipline()
    return 'EM' if d == 'em' else 'PH'
