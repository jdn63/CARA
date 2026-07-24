"""
Extreme Heat domain risk assessment - Wisconsin DHS Heat Vulnerability Index.

This module previously implemented a CARA-specific EVR
(exposure-vulnerability-resilience) transform that combined CDC EPHT
heat-day counts, NOAA wet-bulb projections, CDC SVI themes, and the
census elderly share. As of v29 the Extreme Heat domain relies solely
on the Wisconsin DHS Heat Vulnerability Index (HVI), a vetted block-
group composite published by the Wisconsin Department of Health
Services Bureau of Environmental and Occupational Health.

HVI methodology (https://www.dhs.wisconsin.gov/climate/hvi.htm):

- Composite z-score combining four sub-indices computed at the Census
  block-group level:

    Environmental    land surface temperature, impervious surface,
                     tree canopy
    Health           heat-sensitive condition prevalence, ED visit
                     patterns
    Population       age, social isolation
    Socioeconomic    poverty, language barriers, housing cost burden

- CARA aggregates 4,472 Wisconsin block groups to a 72-county table
  via an unweighted mean of block-group z-scores per county, then
  min-max normalizes to a 0-to-1 vulnerability_score and bins to the
  DHS quintile categories (Low, Moderate Low, Moderate, Moderate High,
  High). See utils/wi_dhs_hvi.py for the fetch and aggregation code.

The Extreme Heat domain score for each Wisconsin jurisdiction is the
HVI vulnerability_score (0-1) for the county containing that
jurisdiction. No additional climate-trajectory projections, EPHT
heat-day counts, NCEI heuristics, or CARA-specific transforms are
layered on top: HVI is already a comprehensive externally vetted
composite. SVI socioeconomic exposure is included via the HVI
socioeconomic sub-index, so the downstream composite path in
utils/data_processor.py does NOT apply an additional SVI multiplier
to extreme heat (see the "Heat SVI single-pass invariant" section in
ARCHITECTURE.md).
"""

import logging
from typing import Any, Dict, Optional

from utils.risk_calculation import get_community_resilience
from utils.wi_dhs_hvi import get_hvi_data

logger = logging.getLogger(__name__)

HVI_METHODOLOGY_URL = "https://www.dhs.wisconsin.gov/climate/hvi.htm"
HVI_SOURCE_LABEL = (
    "Wisconsin DHS Heat Vulnerability Index (block-group composite "
    "aggregated to county)"
)


def _risk_level(score: Optional[float]) -> str:
    if score is None:
        return "Unavailable"
    if score >= 0.85:
        return "Critical"
    if score >= 0.70:
        return "Very High"
    if score >= 0.55:
        return "High"
    if score >= 0.40:
        return "Moderate"
    return "Low"


def _unavailable(county_name: str, reason: str) -> Dict[str, Any]:
    """Explicit-unavailable payload (no synthetic substitution)."""
    return {
        "county_name": county_name,
        "overall_risk": None,
        "risk_level": "Unavailable",
        "horizon": "present_day",
        "exposure": {"final_exposure": None},
        "vulnerability": {"final_vulnerability": None},
        "resilience": {"final_resilience": None},
        "wet_bulb_risk": {"final_wet_bulb_risk": None},
        "climate_trend_factor": {"final_trend_factor": None},
        "trajectory_2050": None,
        "metrics": {
            "hvi_score": None,
            "hvi_category": None,
            "annual_heat_days": None,
            "heat_advisories": None,
            "elderly_percentage": None,
            "ed_visits": None,
            "heat_days_source": None,
            "heat_days_year": None,
        },
        "data_quality": {
            "available": False,
            "reason": reason,
            "classification": "unavailable",
        },
        "methodology": "Wisconsin DHS Heat Vulnerability Index (data unavailable)",
        "methodology_url": HVI_METHODOLOGY_URL,
        "data_sources": [],
        "key_concerns": [],
        "error": reason,
    }


def _z_to_unit(z: Any) -> Optional[float]:
    """Map a z-score into [0, 1] via a linear [-2, +2] window."""
    if z is None:
        return None
    try:
        zf = float(z)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, (zf + 2.0) / 4.0))


def calculate_enhanced_extreme_heat_risk(
    county_name: str,
    jurisdiction_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute the Extreme Heat domain risk for a Wisconsin county.

    The overall_risk is the WI DHS Heat Vulnerability Index
    vulnerability_score (0-1) for the county containing the
    jurisdiction. See the module docstring for the HVI methodology.

    The return shape preserves the public contract consumed by
    utils.data_processor (overall_risk, risk_level, exposure /
    vulnerability / resilience sub-blocks, metrics dict, data_sources)
    so dashboards continue to render without template changes. The
    EVR-style sub-blocks are populated from HVI sub-indices for
    transparency but are NOT composited again - the headline score is
    the HVI vulnerability_score itself.
    """
    record = get_hvi_data(county_name)
    if not record:
        logger.warning(
            "DHS HVI cache miss for %s (jurisdiction %s); extreme heat "
            "domain marked unavailable. Run refresh_all_wi_dhs_hvi() to "
            "populate.",
            county_name, jurisdiction_id,
        )
        return _unavailable(
            county_name,
            "DHS HVI cache has not been populated for this county yet.",
        )

    raw_score = record.get("vulnerability_score")
    if raw_score is None:
        return _unavailable(
            county_name,
            "DHS HVI record present but vulnerability_score missing.",
        )

    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        return _unavailable(
            county_name,
            f"DHS HVI vulnerability_score not numeric: {raw_score!r}",
        )

    score = max(0.0, min(1.0, score))
    category = record.get("category") or _risk_level(score)

    # Informational sub-block mapping from HVI sub-indices. Used by
    # the dashboard's "show work" panel only - the headline score is
    # the HVI vulnerability_score, not a re-composite of these.
    env_z = record.get("enviro_zscore_mean")
    health_z = record.get("health_zscore_mean")
    pop_z = record.get("pop_zscore_mean")
    socio_z = record.get("socio_zscore_mean")

    exposure_unit = _z_to_unit(env_z)
    health_unit = _z_to_unit(health_z)
    pop_unit = _z_to_unit(pop_z)
    socio_unit = _z_to_unit(socio_z)

    vuln_components = [v for v in (health_unit, pop_unit) if v is not None]
    if vuln_components:
        vulnerability_unit = sum(vuln_components) / len(vuln_components)
    else:
        vulnerability_unit = score
    # Display-only resilience: FEMA NRI Community Resilience (HVRI BRIC),
    # matching the resilience source used by the EVR domains. Previously
    # this was 1.0 minus the HVI socioeconomic sub-index, which relabeled
    # the same socioeconomic signal already inside the headline HVI score
    # as "resilience" (external review finding, resolved). This value is
    # informational only; the headline score remains the DHS HVI
    # vulnerability_score and is NOT re-composited.
    resilience_unit = get_community_resilience(county_name)

    rank = record.get("statewide_rank")
    total = record.get("statewide_county_count")

    key_concerns: list = []
    if score >= 0.70:
        key_concerns.append(
            "County ranks in the upper tier of statewide heat vulnerability"
        )
    if category in ("High", "Moderate High"):
        key_concerns.append(f"DHS HVI quintile: {category}")

    return {
        "county_name": county_name,
        "jurisdiction_id": jurisdiction_id,
        "overall_risk": round(score, 3),
        "risk_level": _risk_level(score),
        "horizon": "present_day",
        "exposure": {
            "final_exposure": exposure_unit,
            "source": "HVI environmental sub-index (z-score scaled to [0,1])",
        },
        "vulnerability": {
            "final_vulnerability": (
                round(vulnerability_unit, 3)
                if vulnerability_unit is not None else None
            ),
            "source": "HVI health and population sub-indices (mean)",
        },
        "resilience": {
            "final_resilience": round(resilience_unit, 3),
            "source": "FEMA NRI Community Resilience (HVRI BRIC), informational only",
        },
        "wet_bulb_risk": {"final_wet_bulb_risk": None},
        "climate_trend_factor": {"final_trend_factor": None},
        "trajectory_2050": None,
        "metrics": {
            "hvi_score": round(score, 3),
            "hvi_category": category,
            "hvi_zscore_mean": record.get("hvi_zscore_mean"),
            "enviro_zscore_mean": env_z,
            "health_zscore_mean": health_z,
            "pop_zscore_mean": pop_z,
            "socio_zscore_mean": socio_z,
            "statewide_rank": rank,
            "statewide_county_count": total,
            "block_group_count": record.get("block_group_count"),
            "last_updated": record.get("last_updated"),
            # Legacy keys preserved for template compatibility. The
            # underlying observations (extreme-heat days, heat-related
            # ED visits) are folded into the HVI composite, so we do
            # not surface a separate per-county number here.
            "annual_heat_days": None,
            "heat_advisories": None,
            "elderly_percentage": None,
            "ed_visits": None,
            "heat_days_source": (
                "Folded into WI DHS HVI composite (environmental + "
                "health sub-indices)"
            ),
            "heat_days_year": None,
        },
        "key_concerns": key_concerns,
        "methodology": (
            "Wisconsin DHS Heat Vulnerability Index (block-group "
            "composite aggregated to county)"
        ),
        "methodology_url": HVI_METHODOLOGY_URL,
        "data_sources": [HVI_SOURCE_LABEL],
        "data_quality": {
            "available": True,
            "classification": "live",
        },
    }
