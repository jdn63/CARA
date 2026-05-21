"""Hazmat (Industrial) risk calculator.

Computes a 0-1 residual risk score for industrial hazardous-material
exposure (TRI facilities, EPCRA Tier II reportable chemical storage,
fixed-site chemical release potential) using the standard CARA EVR
formula:

    Risk = (Exposure * Vulnerability) * (2.0 - Resilience) * HIF

This is a sibling to ``utils.hazmat_agricultural_risk`` and is wired
into the PHRAT composite at 3% (PH) / 3% (EM); the agricultural
calculator carries the other 3% on each side.

Data sources (v0 seed):
  - EPA Toxics Release Inventory (TRI) facility counts (real overrides
    in data/hazmat_scoping/county_tri_counts.json for Milwaukee and
    Dodge; tiered proxy in data/hazmat/county_classifications.json
    for the remaining 70 counties pending the Phase B EPA Envirofacts
    bulk fetch).
  - CDC SVI 2022 for vulnerability themes.
  - U.S. Census ACS for elderly_pct and population.
  - Static resilience baseline elevated for counties that host a
    permanent WEM Regional Hazmat Team or a CHEMPACK position.

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

# WEM Regional Hazmat Teams (Type I/II) are based in or near these
# counties per the Wisconsin SERB Regional Hazmat Response Teams
# directory. Hosting a team is treated as a resilience boost since
# response time is the dominant determinant of consequence in a
# fixed-site chemical release.
HAZMAT_TEAM_HOST_COUNTIES = {
    "Milwaukee", "Dane", "Brown", "Waukesha", "Outagamie",
    "La Crosse", "Eau Claire", "Marathon", "Winnebago",
}

# CHEMPACK positioned counties (federal medical countermeasure cache
# for nerve agent / cholinergic-crisis chemical events). Approximate
# positioning per ASPR public guidance; treated as a small additional
# resilience signal for the consequence side of the EVR formula.
CHEMPACK_POSITIONED_COUNTIES = {
    "Milwaukee", "Dane", "Brown", "La Crosse", "Marathon",
    "Sheboygan", "Eau Claire", "Wood",
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
    using_real_tri = isinstance(tri_facility_count, (int, float)) and tri_facility_count > 0

    if using_real_tri:
        tri_score = max(0.0, min(1.0, float(tri_facility_count) / 200.0))
        exposure = max(tier_score, tri_score)
    else:
        tri_score = None
        exposure = tier_score

    return {
        "score": exposure,
        "tier": tier,
        "tier_score": tier_score,
        "tri_facility_count": tri_facility_count if using_real_tri else None,
        "tri_score": tri_score,
        "using_real_tri": using_real_tri,
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
    if county_name in HAZMAT_TEAM_HOST_COUNTIES:
        base += 0.20
        notes.append("Hosts WEM Regional Hazmat Team")
    if county_name in CHEMPACK_POSITIONED_COUNTIES:
        base += 0.10
        notes.append("CHEMPACK positioned in or adjacent county")
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
            "hazmat_team_host": county_name in HAZMAT_TEAM_HOST_COUNTIES,
            "chempack_positioned": county_name in CHEMPACK_POSITIONED_COUNTIES,
            "data_vintage": "v0 tiered proxy + real TRI overrides where present",
        },
        "data_sources": [
            "EPA Toxics Release Inventory (TRI) facility counts (real "
            "for Milwaukee / Dodge; tiered proxy elsewhere pending Phase B "
            "Envirofacts bulk fetch)",
            "EPA EPCRA Tier II reportable chemical storage (planned)",
            "Wisconsin SERB Regional Hazmat Response Teams directory",
            "ASPR CHEMPACK positioning (public guidance)",
            "CDC Social Vulnerability Index (SVI) 2022",
            "U.S. Census Bureau ACS demographics",
        ],
    }
