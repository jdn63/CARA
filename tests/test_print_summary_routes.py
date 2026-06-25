"""Route smoke tests for the four printable Summary pages.

These guard against the class of regression that silently turned the
printable Summary into an error page for every jurisdiction: a stale
variable reference (`domain_action_plans`) raised inside the view, the
view caught the exception, and `error.html` was rendered with HTTP 200.
Manual spot-checks were the only thing that caught it.

Each test asserts the route:
  - returns HTTP 200,
  - renders the real summary template (not error.html),
  - shows exactly 5 risk cards when scores exist,
  - shows the "Draft pending expert review" banner, and
  - has the correct closing call-to-action for its audience:
      * Public Health jurisdiction + EM county  -> Action Plan link present
      * HERC region + WEM region                -> Dashboard-only (no Action Plan)

Valid IDs used:
  - jurisdiction id "1" (Adams County Health & Human Services)
  - EM county slug "adams"
  - HERC region id "1"
  - WEM region slug "southeast" (WEM ids are slugs, not numbers)

To run: pytest tests/test_print_summary_routes.py -v
"""

from __future__ import annotations

# Markers in the rendered HTML.
# error.html renders this danger header; its absence proves we got the
# real summary instead of the swallowed-exception error page.
_ERROR_MARKER = '<h2 class="mb-0">Error</h2>'
# Each top-risk card renders this badge fragment exactly once.
_CARD_MARKER = "Risk &middot;"
_DRAFT_BANNER = "Draft pending expert review"
# The closing CTA Action Plan link (jurisdiction / EM audiences only).
_ACTION_PLAN_MARKER = "/action-plan/"
_DASHBOARD_MARKER = "View Data Dashboard"


def _body(client, url):
    resp = client.get(url)
    return resp, resp.get_data(as_text=True)


def _assert_real_summary(resp, body, url):
    assert resp.status_code == 200, f"{url} returned {resp.status_code}, expected 200"
    assert _ERROR_MARKER not in body, (
        f"{url} rendered the error page instead of the real summary. "
        f"A swallowed exception in the view (e.g. a stale variable "
        f"reference) is the usual cause."
    )


def _assert_five_cards(body, url):
    count = body.count(_CARD_MARKER)
    assert count == 5, f"{url} rendered {count} risk cards, expected exactly 5"


def _assert_draft_banner(body, url):
    assert _DRAFT_BANNER in body, f"{url} is missing the draft-pending-review banner"


class TestJurisdictionPrintSummary:
    """/print-summary/<id> -- Public Health jurisdiction audience."""

    URL = "/print-summary/1"

    def test_renders_real_summary(self, client):
        resp, body = _body(client, self.URL)
        _assert_real_summary(resp, body, self.URL)

    def test_five_risk_cards(self, client):
        _, body = _body(client, self.URL)
        _assert_five_cards(body, self.URL)

    def test_draft_banner_present(self, client):
        _, body = _body(client, self.URL)
        _assert_draft_banner(body, self.URL)

    def test_cta_includes_action_plan(self, client):
        _, body = _body(client, self.URL)
        assert _ACTION_PLAN_MARKER in body, (
            f"{self.URL} (jurisdiction) should offer the Action Plan link"
        )
        assert _DASHBOARD_MARKER in body


class TestEmCountyPrintSummary:
    """/em-print-summary/<county_slug> -- Emergency Management county audience."""

    URL = "/em-print-summary/adams"

    def test_renders_real_summary(self, client):
        resp, body = _body(client, self.URL)
        _assert_real_summary(resp, body, self.URL)

    def test_five_risk_cards(self, client):
        _, body = _body(client, self.URL)
        _assert_five_cards(body, self.URL)

    def test_draft_banner_present(self, client):
        _, body = _body(client, self.URL)
        _assert_draft_banner(body, self.URL)

    def test_cta_includes_action_plan(self, client):
        _, body = _body(client, self.URL)
        assert _ACTION_PLAN_MARKER in body, (
            f"{self.URL} (EM county) should offer the Action Plan link"
        )
        assert _DASHBOARD_MARKER in body


class TestHercRegionPrintSummary:
    """/herc-print-summary/<id> -- HERC region audience (Dashboard-only CTA)."""

    URL = "/herc-print-summary/1"

    def test_renders_real_summary(self, client):
        resp, body = _body(client, self.URL)
        _assert_real_summary(resp, body, self.URL)

    def test_five_risk_cards(self, client):
        _, body = _body(client, self.URL)
        _assert_five_cards(body, self.URL)

    def test_draft_banner_present(self, client):
        _, body = _body(client, self.URL)
        _assert_draft_banner(body, self.URL)

    def test_cta_is_dashboard_only(self, client):
        _, body = _body(client, self.URL)
        assert _DASHBOARD_MARKER in body
        assert _ACTION_PLAN_MARKER not in body, (
            f"{self.URL} (HERC region) must NOT offer an Action Plan link"
        )


class TestWemRegionPrintSummary:
    """/wem-print-summary/<slug> -- WEM region audience (Dashboard-only CTA).

    WEM region ids are slugs (e.g. "southeast", "northwest"), not numbers.
    """

    URL = "/wem-print-summary/southeast"

    def test_renders_real_summary(self, client):
        resp, body = _body(client, self.URL)
        _assert_real_summary(resp, body, self.URL)

    def test_five_risk_cards(self, client):
        _, body = _body(client, self.URL)
        _assert_five_cards(body, self.URL)

    def test_draft_banner_present(self, client):
        _, body = _body(client, self.URL)
        _assert_draft_banner(body, self.URL)

    def test_cta_is_dashboard_only(self, client):
        _, body = _body(client, self.URL)
        assert _DASHBOARD_MARKER in body
        assert _ACTION_PLAN_MARKER not in body, (
            f"{self.URL} (WEM region) must NOT offer an Action Plan link"
        )
