"""Integrity tests for the real-data upgrades that replaced proxy models.

Locks in two source replacements:

  1. Forest cover in the vector-borne disease baseline is real FIA
     (Forest Inventory and Analysis) design-based area estimation for all
     72 counties, not the v1 curated seed estimates.
  2. Hazmat-industrial exposure incorporates real PHMSA pipeline incident
     history (trailing 20 years) for all 72 counties, where a zero count
     is a real measurement (full Wisconsin extract), not a data gap.
"""

import json

from main import app


def test_forest_cover_is_real_fia_all_counties():
    with app.app_context():
        base = json.load(
            open("data/disease/wisconsin_vector_borne_baseline.json")
        )
    cb = base["county_baselines"]
    assert len(cb) == 72
    for county, entry in cb.items():
        assert entry.get("forest_cover_source") == "FIA_EVALID_552501", county
        pct = entry.get("forest_cover_pct")
        assert isinstance(pct, (int, float))
        assert 0 <= pct <= 100
    prov = base["metadata"].get("forest_cover_provenance", {})
    assert prov.get("evalid") == "552501"
    assert prov.get("coverage") == "72 of 72 counties"


def test_pipeline_seed_covers_all_counties_with_real_zeros():
    seed = json.load(
        open("data/hazmat_scoping/wi_county_pipeline_incidents.json")
    )
    counties = seed["counties"]
    assert len(counties) == 72
    # Zeros must be present as real measurements, not omitted.
    zero_counties = [
        c
        for c, v in counties.items()
        if v["pipeline_incidents_20yr"] == 0
    ]
    assert len(zero_counties) > 0
    total = sum(v["pipeline_incidents_20yr"] for v in counties.values())
    assert total == seed["_meta"]["statewide_total"]
    # Douglas County (Superior refinery/pipeline hub) is the state outlier.
    assert counties["Douglas"]["pipeline_incidents_20yr"] >= 20


def test_hazmat_exposure_uses_real_pipeline_signal():
    with app.app_context():
        from utils.hazmat_industrial_risk import (
            calculate_hazmat_industrial_risk,
        )
        douglas = calculate_hazmat_industrial_risk("Douglas", "public_health")
        vilas = calculate_hazmat_industrial_risk("Vilas", "public_health")
    for result in (douglas, vilas):
        ef = result["exposure_factors"]
        assert ef["using_real_pipeline"] is True
        assert isinstance(ef["pipeline_incidents_20yr"], (int, float))
    # A real zero-incident county still reports a real measurement.
    assert vilas["exposure_factors"]["pipeline_incidents_20yr"] == 0
    # The pipeline bump raises the incident-heavy county's exposure above
    # the incident-free county's.
    assert (
        douglas["exposure_factors"]["pipeline_score"]
        > vilas["exposure_factors"]["pipeline_score"]
    )


def test_ag_chemical_seed_covers_all_counties_honestly():
    seed = json.load(
        open("data/hazmat_scoping/wi_county_ag_chemical.json")
    )
    counties = seed["counties"]
    assert len(counties) == 72
    for county, entry in counties.items():
        assert entry["data_status"] in (
            "complete", "partial_suppressed", "no_census_record"
        ), county
        intensity = entry["ag_chemical_intensity"]
        assert 0.0 <= intensity <= 1.0, county
    # Menominee has no census farm records; must be an honest zero.
    assert counties["Menominee"]["data_status"] == "no_census_record"
    assert counties["Menominee"]["ag_chemical_intensity"] == 0.0
    # Heavy-agriculture counties must rank near the top.
    assert counties["Dane"]["ag_chemical_intensity"] > 0.9


def test_hazmat_agricultural_uses_real_census():
    with app.app_context():
        from utils.hazmat_agricultural_risk import (
            calculate_hazmat_agricultural_risk,
        )
        dane = calculate_hazmat_agricultural_risk("Dane", "public_health")
        menominee = calculate_hazmat_agricultural_risk(
            "Menominee", "public_health"
        )
    assert dane["exposure_factors"]["using_real_ag_census"] is True
    assert dane["components"]["exposure"] > 0.9
    # Floor exposure, never a fabricated tier.
    assert menominee["components"]["exposure"] == 0.05
    assert "agricultural_tier" not in dane["metrics"]


def test_dashboard_no_stale_ag_tier_wording():
    from flask import render_template
    import re
    with app.test_client() as c:
        html = c.get("/dashboard/16").data.decode()
    assert "Agricultural chemical intensity" in html
    assert "dairy + row-crop intensity tier" not in html
    assert "tiered proxy elsewhere" not in html
    assert ">Agricultural tier<" not in html
