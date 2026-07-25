"""Hazmat (Agricultural) risk calculator.

Computes a 0-1 residual risk score for agricultural hazardous-material
exposure (anhydrous ammonia release, pesticide drift, agricultural
chemical fires, manure-pit hydrogen sulfide) using the standard CARA
EVR formula:

    Risk = (Exposure * Vulnerability) * (1.5 - Resilience) * HIF

Sibling to ``utils.hazmat_industrial_risk``; both are wired into the
PHRAT composite at 3% on the PH and EM sides for a combined 6%
Hazardous Materials weight.

Data sources:
  - USDA NASS Census of Agriculture 2022 (QuickStats API, static seed
    in data/hazmat_scoping/wi_county_ag_chemical.json): real per-county
    chemical expense, fertilizer expense, harvested cropland acres, and
    milk-cow inventory for all 72 counties, combined into a 0-1
    ag_chemical_intensity score. Census disclosure-suppressed values
    are stored as null and the score weights renormalize over the
    available fields; nothing is fabricated. This replaced the former
    v0 tiered proxy.
  - CDC SVI 2022 housing/transportation theme (drift exposure proxy
    for rural housing near treated cropland).
  - U.S. Census ACS rural-isolation factor.
  - Known barrier: the WI DATCP Agricultural Chemical Cleanup Program
    (ACCP) annual summary is a PDF report without a queryable
    per-county dataset, so ACCP incident history is not yet a signal.

The calculator is cache-only safe: it does not perform any live HTTP.
"""
import json
import logging
import os
from typing import Any, Dict, Optional

from utils.risk_calculation import (calculate_residual_risk,
                                    get_community_resilience,
                                    get_health_impact_factor)
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_AG_CHEMICAL_CACHE: Optional[Dict[str, Any]] = None

# NOTE: UW-Madison Extension operates in all 72 Wisconsin counties, so
# Extension presence provides no county-level differentiation and is not
# used as a resilience signal. A previous version credited a subset of
# counties with an "Extension ag-safety footprint" bonus; that list could
# not be verified against any published Extension program roster and was
# removed (2026-07 data-source integrity audit).


def _load_ag_chemical() -> Dict[str, Any]:
    global _AG_CHEMICAL_CACHE
    if _AG_CHEMICAL_CACHE is not None:
        return _AG_CHEMICAL_CACHE
    path = "data/hazmat_scoping/wi_county_ag_chemical.json"
    try:
        if os.path.exists(path):
            with open(path) as f:
                _AG_CHEMICAL_CACHE = json.load(f)
        else:
            _AG_CHEMICAL_CACHE = {}
    except Exception as e:
        logger.warning(f"hazmat_agricultural: failed to load ag chemical seed: {e}")
        _AG_CHEMICAL_CACHE = {}
    return _AG_CHEMICAL_CACHE


# Minimum exposure floor: even counties with negligible census-recorded
# agriculture have ambient agricultural-chemical exposure (transport
# corridors, retail/co-op storage), so exposure never reads exactly zero.
_EXPOSURE_FLOOR = 0.05


def _exposure_score(county_name: str) -> Dict[str, Any]:
    seed = _load_ag_chemical()
    entry = (seed.get("counties") or {}).get(county_name)
    if entry is None:
        logger.warning(
            f"hazmat_agricultural: no ag chemical record for {county_name}; "
            "using floor exposure"
        )
        return {
            "score": _EXPOSURE_FLOOR,
            "ag_chemical_intensity": None,
            "data_status": "missing",
            "using_real_ag_census": False,
        }
    intensity = float(entry.get("ag_chemical_intensity") or 0.0)
    score = max(_EXPOSURE_FLOOR, min(1.0, intensity))
    return {
        "score": score,
        "ag_chemical_intensity": intensity,
        "data_status": entry.get("data_status", "unknown"),
        "using_real_ag_census": True,
        "chemical_expense_usd": entry.get("chemical_expense_usd"),
        "fertilizer_expense_usd": entry.get("fertilizer_expense_usd"),
        "cropland_harvested_acres": entry.get("cropland_harvested_acres"),
        "milk_cows_head": entry.get("milk_cows_head"),
    }


def _vulnerability_score(county_name: str, discipline: str) -> Dict[str, Any]:
    svi = get_svi_data(county_name) or {}
    socioeconomic = float(svi.get("socioeconomic", 0.5) or 0.5)
    housing_transport = float(svi.get("housing_transportation", 0.5) or 0.5)
    minority = float(svi.get("minority_status", 0.5) or 0.5)
    household = float(svi.get("household_composition", 0.5) or 0.5)

    try:
        from utils.census_data_loader import wisconsin_census
        population = wisconsin_census.get_county_population(county_name) or 60000
    except Exception:
        population = 60000
    # Rural isolation = higher consequence (longer response time, more
    # exposed farmworker households, fewer drift-buffer ordinances).
    rural_factor = min(1.0, max(0.0, 1.0 - (population / 300000.0)))

    if discipline == "em":
        vulnerability = (
            rural_factor * 0.30
            + housing_transport * 0.25
            + minority * 0.20  # migrant farmworker household proxy
            + socioeconomic * 0.15
            + household * 0.10
        )
    else:
        vulnerability = (
            minority * 0.25       # farmworker / migrant household proxy
            + socioeconomic * 0.20
            + rural_factor * 0.20
            + housing_transport * 0.15
            + household * 0.10
            + (1.0 - float(svi.get("overall", 0.5) or 0.5)) * 0.10
        )

    return {
        "score": min(1.0, max(0.0, vulnerability)),
        "socioeconomic_svi": socioeconomic,
        "housing_transportation_svi": housing_transport,
        "minority_status_svi": minority,
        "household_composition_svi": household,
        "rural_factor": rural_factor,
        "population": population,
    }


def _resilience_score(county_name: str) -> Dict[str, Any]:
    # Resilience: FEMA NRI Community Resilience (HVRI BRIC), replacing the
    # former inverse-SVI base that double-counted the socioeconomic SVI
    # theme already present in the Vulnerability term (external review
    # finding, resolved). See get_community_resilience docstring.
    base = get_community_resilience(county_name)
    notes = []
    base = max(0.10, min(0.90, base))
    return {"score": base, "notes": notes}


def calculate_hazmat_agricultural_risk(
    county_name: str, discipline: str = "public_health"
) -> Dict[str, Any]:
    """Return the hazmat-agricultural EVR risk for the given county."""
    exposure = _exposure_score(county_name)
    vulnerability = _vulnerability_score(county_name, discipline)
    resilience = _resilience_score(county_name)

    try:
        hif = get_health_impact_factor(county_name, "hazmat_agricultural")
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
            k: v for k, v in exposure.items() if k != "score"
        },
        "vulnerability_breakdown": {
            k: v for k, v in vulnerability.items() if k != "score"
        },
        "resilience_factors": {
            "score": resilience["score"],
            "notes": resilience["notes"],
        },
        "metrics": {
            "ag_chemical_intensity": exposure.get("ag_chemical_intensity"),
            "ag_census_data_status": exposure.get("data_status"),
            "data_vintage": "USDA NASS Census of Agriculture 2022 (real county data, all 72 counties)",
        },
        "data_sources": [
            "USDA NASS Census of Agriculture 2022 (chemical and fertilizer expense, harvested cropland, milk-cow inventory)",
            "CDC NIOSH Agricultural Safety & Health program",
            "EPA Worker Protection Standard (WPS)",
            "CDC Social Vulnerability Index (SVI) 2022",
            "FEMA NRI Community Resilience (HVRI BRIC index)",
            "U.S. Census Bureau ACS rural-population indicators",
        ],
    }
