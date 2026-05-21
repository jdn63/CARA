"""Hazmat (Agricultural) risk calculator.

Computes a 0-1 residual risk score for agricultural hazardous-material
exposure (anhydrous ammonia release, pesticide drift, agricultural
chemical fires, manure-pit hydrogen sulfide) using the standard CARA
EVR formula:

    Risk = (Exposure * Vulnerability) * (2.0 - Resilience) * HIF

Sibling to ``utils.hazmat_industrial_risk``; both are wired into the
PHRAT composite at 3% on the PH and EM sides for a combined 6%
Hazardous Materials weight.

Data sources (v0 seed):
  - USDA NASS Census of Agriculture county dairy + row-crop intensity
    (tiered proxy in data/hazmat/county_classifications.json pending
    the Phase B Census of Ag pesticide expenditure ingestion).
  - WI DATCP Agricultural Chemical Cleanup Program (ACCP) annual
    summary (proxied via the agricultural tier today).
  - CDC SVI 2022 housing/transportation theme (drift exposure proxy
    for rural housing near treated cropland).
  - U.S. Census ACS rural-isolation factor.

The calculator is cache-only safe: it does not perform any live HTTP.
"""
import json
import logging
import os
from typing import Any, Dict, Optional

from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_CLASSIFICATIONS_CACHE: Optional[Dict[str, Any]] = None

# Counties with a well-established Worker Protection Standard /
# anhydrous ammonia retailer extension presence (UW-Madison Extension
# Agricultural Health and Safety program county footprint). Used as a
# resilience signal -- not a perfect proxy, but it captures county-level
# investment in farmworker training and pesticide-drift mitigation.
EXTENSION_AG_SAFETY_HEAVY = {
    "Dane", "Marathon", "Outagamie", "Brown", "Fond du Lac", "Sheboygan",
    "Manitowoc", "Grant", "Lafayette", "Iowa", "Green", "Rock",
    "Walworth", "Jefferson", "Columbia", "Dodge", "Sauk",
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
        logger.warning(f"hazmat_agricultural: failed to load classifications: {e}")
        _CLASSIFICATIONS_CACHE = {}
    return _CLASSIFICATIONS_CACHE


def _exposure_score(county_name: str) -> Dict[str, Any]:
    classifications = _load_classifications()
    meta = classifications.get("_meta", {})
    tier_scores = meta.get("tier_scores", {
        "very_high": 0.85, "high": 0.65, "moderate": 0.45, "low": 0.25,
    })
    county_entry = (classifications.get("counties") or {}).get(county_name) or {}
    tier = county_entry.get("agricultural_tier", "low")
    tier_score = tier_scores.get(tier, 0.25)
    return {"score": tier_score, "tier": tier, "tier_score": tier_score}


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
    svi = get_svi_data(county_name) or {}
    socio_inverse = 1.0 - float(svi.get("socioeconomic", 0.5) or 0.5)
    base = 0.40 + socio_inverse * 0.15
    notes = []
    if county_name in EXTENSION_AG_SAFETY_HEAVY:
        base += 0.15
        notes.append("UW-Madison Extension ag-safety program county footprint")
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
            "agricultural_tier": exposure["tier"],
            "tier_score": exposure["tier_score"],
        },
        "vulnerability_breakdown": {
            k: v for k, v in vulnerability.items() if k != "score"
        },
        "resilience_factors": {
            "score": resilience["score"],
            "notes": resilience["notes"],
        },
        "metrics": {
            "agricultural_tier": exposure["tier"],
            "extension_ag_safety_heavy": county_name in EXTENSION_AG_SAFETY_HEAVY,
            "data_vintage": "v0 tiered proxy pending USDA Census of Ag and WI DATCP ACCP ingestion",
        },
        "data_sources": [
            "USDA NASS Census of Agriculture (Wisconsin county dairy + row-crop intensity)",
            "WI DATCP Agricultural Chemical Cleanup Program (ACCP) annual summary",
            "CDC NIOSH Agricultural Safety & Health program",
            "EPA Worker Protection Standard (WPS)",
            "CDC Social Vulnerability Index (SVI) 2022",
            "U.S. Census Bureau ACS rural-population indicators",
        ],
    }
