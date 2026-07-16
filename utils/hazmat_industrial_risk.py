"""Hazmat (Industrial) risk calculator.

Computes a 0-1 residual risk score for industrial hazardous-material
exposure (TRI facilities, EPCRA Tier II reportable chemical storage,
fixed-site chemical release potential) using the standard CARA EVR
formula:

    Risk = (Exposure * Vulnerability) * (2.0 - Resilience) * HIF

This is a sibling to ``utils.hazmat_agricultural_risk`` and is wired
into the PHRAT composite at 3% (PH) / 3% (EM); the agricultural
calculator carries the other 3% on each side.

Data sources:
  - EPA Toxics Release Inventory (TRI) facility counts, real data for
    all 72 counties in data/hazmat_scoping/county_tri_counts.json (this
    replaced the former Milwaukee/Dodge-only overrides and the tiered
    proxy).
  - PHMSA Pipeline Safety Flagged Incident Files, real trailing 20-year
    per-county incident counts in
    data/hazmat_scoping/wi_county_pipeline_incidents.json. Applied as a
    capped additive exposure term (max +0.15, /25 saturation); a zero
    count is a real measurement, not a data gap.
  - Documented barrier: EPA RMP facility counts are not incorporated
    because the RMP dataset is not publicly queryable at per-county
    granularity (Envirofacts RMP is access-restricted).
  - CDC SVI 2022 for vulnerability themes.
  - U.S. Census ACS for elderly_pct and population.
  - Static resilience baseline elevated only for La Crosse County, the
    single county whose regional hazmat team placement is fixed in
    Wisconsin statute (Wis. Stat. 323.13). No CHEMPACK signal is used:
    CHEMPACK cache locations are confidential by federal law
    (42 U.S.C. 247d-6b) and cannot be sourced from any authoritative
    public record.

The calculator is cache-only safe: it does not perform any live HTTP.
All inputs are read from local JSON or from already-cached SVI / Census
helpers that themselves obey the cache-only request-path invariant.
"""
import json
import logging
import os
from typing import Any, Dict, Optional

from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_CLASSIFICATIONS_CACHE: Optional[Dict[str, Any]] = None
_TRI_COUNTS_CACHE: Optional[Dict[str, Any]] = None

# Wisconsin's Regional Hazardous Materials Response System is established
# under Wis. Stat. 323.13(2)(a), which authorizes no more than nine
# regional (Level A) response teams and specifically mandates that one be
# located in La Crosse County. La Crosse is therefore the only county
# whose regional-team placement is fixed in statute. The full current
# roster of host counties is not published in a single authoritative
# public source, so no other county is assigned a team-based resilience
# signal -- this deliberately avoids asserting unverified host locations.
# A faster local Level A response lowers the consequence side of a
# fixed-site chemical release, which is why the statutory team earns a
# resilience boost.
STATUTORY_REGIONAL_HAZMAT_TEAM_COUNTIES = {
    "La Crosse",
}


def _load_classifications() -> Dict[str, Any]:
    global _CLASSIFICATIONS_CACHE
    if _CLASSIFICATIONS_CACHE is not None:
        return _CLASSIFICATIONS_CACHE
    path = "data/hazmat/county_classifications.json"
    try:
        if os.path.exists(path):
            with open(path) as f:
                _CLASSIFICATIONS_CACHE = json.load(f)
        else:
            _CLASSIFICATIONS_CACHE = {}
    except Exception as e:
        logger.warning(f"hazmat_industrial: failed to load classifications: {e}")
        _CLASSIFICATIONS_CACHE = {}
    return _CLASSIFICATIONS_CACHE


_PIPELINE_CACHE: Optional[Dict[str, Any]] = None


def _load_pipeline_incidents() -> Dict[str, Any]:
    global _PIPELINE_CACHE
    if _PIPELINE_CACHE is not None:
        return _PIPELINE_CACHE
    path = "data/hazmat_scoping/wi_county_pipeline_incidents.json"
    try:
        if os.path.exists(path):
            with open(path) as f:
                _PIPELINE_CACHE = (json.load(f) or {}).get("counties", {})
        else:
            _PIPELINE_CACHE = {}
    except Exception as e:
        logger.warning(f"hazmat_industrial: failed to load pipeline incidents: {e}")
        _PIPELINE_CACHE = {}
    return _PIPELINE_CACHE


def _load_tri_counts() -> Dict[str, Any]:
    global _TRI_COUNTS_CACHE
    if _TRI_COUNTS_CACHE is not None:
        return _TRI_COUNTS_CACHE
    path = "data/hazmat_scoping/county_tri_counts.json"
    try:
        if os.path.exists(path):
            with open(path) as f:
                _TRI_COUNTS_CACHE = json.load(f)
        else:
            _TRI_COUNTS_CACHE = {}
    except Exception as e:
        logger.warning(f"hazmat_industrial: failed to load TRI counts: {e}")
        _TRI_COUNTS_CACHE = {}
    return _TRI_COUNTS_CACHE


def _exposure_score(county_name: str) -> Dict[str, Any]:
    """Compute the exposure component and return the breakdown so the
    dashboard can show its work.
    """
    classifications = _load_classifications()
    meta = classifications.get("_meta", {})
    tier_scores = meta.get("tier_scores", {
        "very_high": 0.85, "high": 0.65, "moderate": 0.45, "low": 0.25,
    })
    county_entry = (classifications.get("counties") or {}).get(county_name) or {}
    tier = county_entry.get("industrial_tier", "low")
    tier_score = tier_scores.get(tier, 0.25)

    tri_counts = _load_tri_counts().get(county_name) or {}
    tri_facility_count = tri_counts.get("tri_facilities")
    # A numeric count is real measured data, including a true zero
    # (the seed is built from the full Envirofacts TRI_FACILITY pull,
    # so absence of facilities is a measurement, not a gap).
    using_real_tri = isinstance(tri_facility_count, (int, float))

    if using_real_tri:
        tri_score = max(0.0, min(1.0, float(tri_facility_count) / 200.0))
        exposure = max(tier_score, tri_score)
    else:
        tri_score = None
        exposure = tier_score

    # Pipeline incident history (PHMSA flagged incident files, trailing
    # 20 years). Fixed-site TRI counts do not capture linear pipeline
    # hazard, so a county with a real incident record gets an additive
    # bump on top of the TRI/tier exposure. A zero count is a real
    # measurement (full WI extract), not a data gap. The bump is capped
    # at +0.15 so pipeline history nudges but never dominates exposure;
    # ~25 incidents saturate the term (Douglas County, the Superior
    # refinery/pipeline hub, is the state outlier at 35).
    pipeline_entry = _load_pipeline_incidents().get(county_name) or {}
    pipeline_incidents = pipeline_entry.get("pipeline_incidents_20yr")
    using_real_pipeline = isinstance(pipeline_incidents, (int, float))
    if using_real_pipeline:
        pipeline_score = max(0.0, min(1.0, float(pipeline_incidents) / 25.0))
        exposure = min(1.0, exposure + 0.15 * pipeline_score)
    else:
        pipeline_score = None

    return {
        "score": exposure,
        "tier": tier,
        "tier_score": tier_score,
        "tri_facility_count": tri_facility_count if using_real_tri else None,
        "tri_score": tri_score,
        "using_real_tri": using_real_tri,
        "pipeline_incidents_20yr": pipeline_incidents if using_real_pipeline else None,
        "pipeline_score": pipeline_score,
        "using_real_pipeline": using_real_pipeline,
    }


def _vulnerability_score(county_name: str, discipline: str) -> Dict[str, Any]:
    svi = get_svi_data(county_name) or {}
    socioeconomic = float(svi.get("socioeconomic", 0.5) or 0.5)
    housing_transport = float(svi.get("housing_transportation", 0.5) or 0.5)
    minority = float(svi.get("minority_status", 0.5) or 0.5)
    household = float(svi.get("household_composition", 0.5) or 0.5)

    try:
        from utils.census_data_loader import wisconsin_census
        elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name) or 17.0
        population = wisconsin_census.get_county_population(county_name) or 60000
    except Exception:
        elderly_pct, population = 17.0, 60000

    elderly_factor = min(1.0, max(0.05, (elderly_pct - 10.0) / 25.0))
    pop_density_factor = min(1.0, population / 300000.0)  # urbanization proxy

    if discipline == "em":
        # Infrastructure-leaning: housing/transport corridor exposure and
        # population density dominate consequence size for a fixed-site
        # release plume.
        vulnerability = (
            housing_transport * 0.35
            + pop_density_factor * 0.25
            + socioeconomic * 0.15
            + minority * 0.10
            + household * 0.10
            + elderly_factor * 0.05
        )
    else:
        # Public Health-leaning: emphasizes population sensitivity and
        # access-to-care barriers (socioeconomic + minority status).
        vulnerability = (
            socioeconomic * 0.25
            + housing_transport * 0.20
            + elderly_factor * 0.15
            + household * 0.15
            + minority * 0.15
            + pop_density_factor * 0.10
        )

    return {
        "score": min(1.0, vulnerability),
        "socioeconomic_svi": socioeconomic,
        "housing_transportation_svi": housing_transport,
        "minority_status_svi": minority,
        "household_composition_svi": household,
        "elderly_factor": elderly_factor,
        "pop_density_factor": pop_density_factor,
        "elderly_pct": elderly_pct,
        "population": population,
    }


def _resilience_score(county_name: str) -> Dict[str, Any]:
    svi = get_svi_data(county_name) or {}
    socio_inverse = 1.0 - float(svi.get("socioeconomic", 0.5) or 0.5)

    base = 0.40 + socio_inverse * 0.15
    notes = []
    if county_name in STATUTORY_REGIONAL_HAZMAT_TEAM_COUNTIES:
        base += 0.20
        notes.append("Statutorily-designated regional hazmat team (Wis. Stat. 323.13)")
    base = max(0.10, min(0.90, base))
    return {"score": base, "notes": notes}


def calculate_hazmat_industrial_risk(
    county_name: str, discipline: str = "public_health"
) -> Dict[str, Any]:
    """Return the hazmat-industrial EVR risk for the given county."""
    exposure = _exposure_score(county_name)
    vulnerability = _vulnerability_score(county_name, discipline)
    resilience = _resilience_score(county_name)

    try:
        hif = get_health_impact_factor(county_name, "hazmat_industrial")
    except Exception:
        hif = 1.0

    residual = calculate_residual_risk(
        exposure=exposure["score"],
        vulnerability=vulnerability["score"],
        resilience=resilience["score"],
        health_impact_factor=hif,
    )

    return {
        "overall": residual,
        "components": {
            "exposure": exposure["score"],
            "vulnerability": vulnerability["score"],
            "resilience": resilience["score"],
            "health_impact": hif,
        },
        "exposure_factors": {
            "industrial_tier": exposure["tier"],
            "tier_score": exposure["tier_score"],
            "tri_facility_count": exposure["tri_facility_count"],
            "tri_score": exposure["tri_score"],
            "using_real_tri": exposure["using_real_tri"],
            "pipeline_incidents_20yr": exposure["pipeline_incidents_20yr"],
            "pipeline_score": exposure["pipeline_score"],
            "using_real_pipeline": exposure["using_real_pipeline"],
        },
        "vulnerability_breakdown": {
            k: v for k, v in vulnerability.items() if k != "score"
        },
        "resilience_factors": {
            "score": resilience["score"],
            "notes": resilience["notes"],
        },
        "metrics": {
            "industrial_tier": exposure["tier"],
            "tri_facility_count": exposure["tri_facility_count"],
            "statutory_regional_hazmat_team": county_name in STATUTORY_REGIONAL_HAZMAT_TEAM_COUNTIES,
            "pipeline_incidents_20yr": exposure["pipeline_incidents_20yr"],
            "data_vintage": "real TRI facility counts (all 72 counties) + real PHMSA pipeline incident history (20yr); tier proxy retained only as a floor",
        },
        "data_sources": [
            "EPA Toxics Release Inventory (TRI) facility counts (real, "
            "all 72 counties, full Envirofacts TRI_FACILITY extract)",
            "PHMSA Pipeline Safety Flagged Incident Files (gas distribution, "
            "gas transmission/gathering, hazardous liquid; per-county WI "
            "incident counts, trailing 20 years)",
            "EPA EPCRA Tier II reportable chemical storage (planned)",
            "Wisconsin Regional Hazmat Response System, Wis. Stat. 323.13 "
            "(La Crosse County team statutorily mandated; full host roster "
            "not authoritatively published)",
            "CDC Social Vulnerability Index (SVI) 2022",
            "U.S. Census Bureau ACS demographics",
        ],
    }
