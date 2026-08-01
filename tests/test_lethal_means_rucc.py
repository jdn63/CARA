"""Guard tests for the Access to Lethal Means county adjustment.

The county adjustment must be driven by the bundled USDA ERS Rural-Urban
Continuum Codes (2023) snapshot (data/usda_rucc/wi_rucc_2023.json), and the
component must not emit invented metrics (estimated ownership rate, storage
practices index) that look like measurements but are arithmetic derivations.
"""

import pytest

from utils.active_shooter_risk import ActiveShooterRiskModel, _load_wi_rucc
from utils.svi_data import WI_COUNTY_FIPS


@pytest.fixture(scope="module")
def model():
    return ActiveShooterRiskModel()


def test_every_roster_county_has_a_rucc_record():
    lookup = _load_wi_rucc()
    missing = [c for c in WI_COUNTY_FIPS if c.lower() not in lookup]
    assert missing == []
    assert len(lookup) == 72
    assert all(1 <= rec["rucc_2023"] <= 9 for rec in lookup.values())


def test_no_invented_metrics_in_lethal_means(model):
    score, metrics = model.get_access_to_lethal_means("Milwaukee")
    assert "estimated_ownership_rate" not in metrics
    assert "storage_practices_index" not in metrics
    assert metrics["rucc_2023"] == 1
    assert any(
        "USDA ERS Rural-Urban Continuum Codes 2023" in s
        for s in metrics["data_sources"]
    )
    assert metrics["data_quality"] == "medium"


@pytest.mark.parametrize(
    "county,expected_rucc,expected_score",
    [
        ("Milwaukee", 1, 0.50),  # metro, large: 0.65 - 0.15
        ("Dane", 2, 0.60),       # metro, small/mid: 0.65 - 0.05
        ("Lincoln", 6, 0.70),    # nonmetro town: 0.65 + 0.05
        ("Forest", 9, 0.80),     # rural: 0.65 + 0.15
    ],
)
def test_rucc_class_drives_adjustment(model, county, expected_rucc, expected_score):
    score, metrics = model.get_access_to_lethal_means(county)
    assert metrics["rucc_2023"] == expected_rucc
    assert score == pytest.approx(expected_score, abs=1e-9)


def test_unknown_county_fails_loudly_not_silently(model):
    score, metrics = model.get_access_to_lethal_means("Notacounty")
    assert metrics["data_quality"] == "low"
    assert "RUCC lookup failed" in metrics["county_classification"]
    assert score == pytest.approx(0.65)


def test_rendered_pages_cite_usda_rucc():
    """Citation drift guard: the visible source strings must name the RUCC input."""
    from main import app

    client = app.test_client()
    for path in ("/dashboard/50", "/active-shooter-methodology"):
        html = client.get(path).get_data(as_text=True)
        assert "Rural-Urban Continuum" in html, path
