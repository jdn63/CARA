"""Regression tests for the hazmat_industrial resilience signals.

These lock in two accuracy fixes:

  1. CHEMPACK is never used to score a county. Cache locations are
     confidential by federal law (42 U.S.C. 247d-6b), so no CHEMPACK
     signal may reappear in the calculator output.
  2. The statutory regional hazmat-team resilience boost applies ONLY to
     La Crosse County (Wis. Stat. 323.13(2)(a)), because no authoritative
     public roster of the other host counties exists.
"""

from main import app


def _calc(county):
    with app.app_context():
        from utils.hazmat_industrial_risk import (
            calculate_hazmat_industrial_risk,
        )
        return calculate_hazmat_industrial_risk(county, "public_health")


def test_no_chempack_signal_in_output():
    result = _calc("Milwaukee")
    assert "chempack_positioned" not in result["metrics"]
    for value in result["metrics"].values():
        assert "chempack" not in str(value).lower()


def test_la_crosse_has_statutory_team_boost():
    result = _calc("La Crosse")
    assert result["metrics"]["statutory_regional_hazmat_team"] is True
    assert result["components"]["resilience"] > 0.5


def test_other_counties_have_no_team_boost():
    for county in ("Milwaukee", "Dane", "Adams", "Waukesha", "Brown"):
        result = _calc(county)
        assert result["metrics"]["statutory_regional_hazmat_team"] is False
