"""Read-only derivation of jurisdiction- and region-specific Summary signals.

The Summary page pairs each top-risk hazard with authored plain-language copy
(`utils/summary_content.py` + `data/summary_content/summary_content.yaml`).
That copy is generic per domain. This module adds the locally specific layer:
short, factual phrases derived from the SAME computed risk fields the rest of
the app already produces, so a card can say WHY this particular jurisdiction or
region ranks where it does and WHICH local populations the data flags as most
exposed.

Hard rules:
- Read-only. Nothing here changes any score, weight, or threshold. It only
  reads fields already present on the `risk_data` dict from
  `utils.data_processor.process_risk_data()` (jurisdiction) or the HERC/WEM
  aggregators (region).
- No network calls, so it is safe on the cache-only request path.
- Honesty first. Only genuinely local signals are used. Fields that are
  constant defaults across counties (e.g. placeholder vulnerability factors)
  or that do not survive regional aggregation are deliberately skipped, so the
  page never dresses up generic prose as if it were local data. When a domain
  has no real local signal (e.g. the proxy-modeled utilities score), the
  derived lists come back empty and the card falls back to authored copy alone.
- Defensive. Every lookup tolerates missing keys, None, booleans, and the
  "Varies across N counties" placeholder the regional aggregator writes into
  non-uniform string fields. Nothing here raises into the request.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Population-signal thresholds. These gate WHICH authored population groups get
# highlighted as locally elevated; they never change a score. Percentages are
# 0-100; SVI factors are 0-1 (higher = more vulnerable).
_ELDERLY_PCT = 18.0
_MOBILE_HOME_PCT = 8.0
_MOBILE_HOME_FACTOR = 0.5
_SVI_ELEVATED = 0.6
_FOREST_PCT = 35.0
_OUTDOOR_PCT = 10.0


def _is_varies(value: Any) -> bool:
    return isinstance(value, str) and "Varies across" in value


def _num(rd: Dict[str, Any], *path: str) -> Optional[float]:
    """Return a numeric leaf at the nested path, or None.

    Booleans, strings (including the "Varies across N counties" placeholder),
    and missing keys all resolve to None so callers never branch on junk.
    """
    cur: Any = rd
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    if isinstance(cur, bool):
        return None
    if isinstance(cur, (int, float)):
        return float(cur)
    return None


def _text(rd: Dict[str, Any], *path: str) -> Optional[str]:
    """Return a non-empty, non-placeholder string leaf, or None."""
    cur: Any = rd
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    if not isinstance(cur, str):
        return None
    cur = cur.strip()
    if not cur or _is_varies(cur):
        return None
    return cur


def _i(value: float) -> str:
    """Thousands-separated integer string."""
    return f"{int(round(value)):,}"


def _tier(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value.replace("_", " ").strip()


# Domains whose population exposure is read from shared natural-hazard
# vulnerability fields (event-driven hazards with SVI breakdowns).
_NAT_HAZARD = (
    "flood", "tornado", "winter_storm", "thunderstorm",
    "straight_line_wind", "dam_failure",
)


def _driver_builders():
    """Return the per-domain driver builders.

    Each builder takes the full risk_data dict and returns a list of short
    factual driver phrases (already filtered for presence/relevance).
    """

    def period(rd, dom):
        p = _text(rd, f"{dom}_metrics", "data_period")
        return f" since {p}" if p else ""

    def flood(rd):
        out = []
        ev = _num(rd, "flood_metrics", "historical_flood_events")
        if ev and ev > 0:
            out.append(f"{_i(ev)} recorded flood events{period(rd, 'flood')}")
        cl = _num(rd, "flood_metrics", "nfip_claims_total")
        if cl and cl > 0:
            out.append(f"{_i(cl)} flood-insurance claims on record")
        decl = _num(rd, "flood_metrics", "federal_flood_declarations")
        if decl and decl > 0:
            out.append(f"{_i(decl)} federal flood disaster declarations")
        return out

    def tornado(rd):
        out = []
        ev = _num(rd, "tornado_metrics", "historical_tornado_events")
        if ev and ev > 0:
            out.append(f"{_i(ev)} recorded tornadoes{period(rd, 'tornado')}")
        ef = _num(rd, "tornado_metrics", "average_ef_rating")
        if ef and ef >= 2:
            out.append(f"averaging about EF{int(round(ef))} in strength")
        decl = _num(rd, "tornado_metrics", "federal_tornado_declarations")
        if decl and decl > 0:
            out.append(f"{_i(decl)} federal tornado disaster declarations")
        return out

    def winter_storm(rd):
        out = []
        ev = _num(rd, "winter_storm_metrics", "historical_winter_events")
        if ev and ev > 0:
            out.append(
                f"{_i(ev)} recorded severe winter events"
                f"{period(rd, 'winter_storm')}"
            )
        decl = _num(rd, "winter_storm_metrics", "federal_winter_declarations")
        if decl and decl > 0:
            out.append(f"{_i(decl)} federal winter-storm declarations")
        return out

    def thunderstorm(rd):
        out = []
        ev = _num(rd, "thunderstorm_metrics", "historical_thunderstorm_events")
        if ev and ev > 0:
            out.append(
                f"{_i(ev)} recorded severe thunderstorm events"
                f"{period(rd, 'thunderstorm')}"
            )
        return out

    def straight_line_wind(rd):
        out = []
        ev = _num(rd, "straight_line_wind_metrics", "historical_wind_events")
        if ev and ev > 0:
            out.append(
                f"{_i(ev)} recorded damaging wind events"
                f"{period(rd, 'straight_line_wind')}"
            )
        pos = _text(rd, "straight_line_wind_metrics", "derecho_corridor_position")
        if pos:
            word = pos.split("(")[0].strip().lower()
            if word in ("moderate", "high"):
                out.append(
                    f"located in a {word}-exposure straight-line-wind "
                    "(derecho) corridor"
                )
        return out

    def dam_failure(rd):
        out = []
        td = _num(rd, "dam_failure_metrics", "total_dams")
        hh = _num(rd, "dam_failure_metrics", "high_hazard_dams")
        if td and td > 0:
            if hh and hh > 0:
                out.append(f"{_i(td)} dams nearby, {_i(hh)} rated high-hazard")
            else:
                out.append(f"{_i(td)} dams nearby")
        par = _num(rd, "dam_failure_metrics", "modeled_population_at_risk")
        if par and par > 0:
            out.append(f"about {_i(par)} residents modeled in downstream paths")
        return out

    def extreme_heat(rd):
        out = []
        rl = _text(rd, "extreme_heat_metrics", "risk_level")
        if rl and rl.lower() not in ("low", "minimal"):
            out.append(f"Heat Vulnerability Index rated {rl}")
        return out

    def air_quality(rd):
        out = []
        wv = _num(rd, "air_quality_components", "risk_factors",
                  "wildfire_vulnerability")
        if wv is not None and wv >= 0.35:
            word = "high" if wv >= 0.55 else "moderate"
            out.append(f"wildfire-smoke vulnerability rated {word}")
        trend = _text(rd, "air_quality_components", "risk_factors",
                      "historical_trend")
        if trend and trend.lower() in ("worsening", "declining"):
            out.append(f"air-quality trend {trend.lower()}")
        return out

    def vector_borne_disease(rd):
        out = []
        lr = _num(rd, "vbd_metrics", "lyme_incidence_rate")
        if lr and lr > 0:
            out.append(f"{int(round(lr))} Lyme cases per 100,000 (recent)")
        tier = _tier(_text(rd, "vbd_metrics", "lyme_disease_tier"))
        if tier and tier.lower() not in ("low", "minimal", "none"):
            out.append(f"Lyme risk tier rated {tier}")
        fc = _num(rd, "vbd_metrics", "forest_cover_pct")
        if fc and fc >= _FOREST_PCT:
            out.append(f"{int(round(fc))}% forest cover")
        return out

    def health(rd):
        out = []
        overall = _text(rd, "health_metrics", "activity_levels", "overall")
        if overall:
            out.append(
                f"statewide respiratory illness activity is {overall.lower()}"
            )
        mmr = _num(rd, "health_metrics", "vaccination_risk_assessment",
                   "herd_immunity_gaps", "mmr_gap")
        if mmr and mmr >= 5:
            out.append(
                f"statewide MMR coverage gap of about {int(round(mmr))} points"
            )
        flags = rd.get("nndss_data", {})
        flags = flags.get("outbreak_flags", {}) if isinstance(flags, dict) else {}
        if isinstance(flags, dict):
            active = [k for k, v in flags.items() if v is True]
            if active:
                pretty = active[0].replace("_", " ")
                out.append(f"active statewide surveillance flag: {pretty}")
        return out

    def active_shooter(rd):
        out = []
        syv = _num(rd, "active_shooter_components", "school_youth_vulnerability")
        if syv is not None and syv >= 0.6:
            out.append("elevated school- and youth-related vulnerability indicators")
        return out

    def hazmat_industrial(rd):
        out = []
        tri = _num(rd, "hazmat_industrial_exposure_factors", "tri_facility_count")
        if tri and tri > 0:
            out.append(f"{_i(tri)} EPA-tracked industrial chemical facilities")
        tier = _tier(_text(rd, "hazmat_industrial_metrics", "industrial_tier"))
        if tier and tier.lower() in ("moderate", "high", "very high"):
            out.append(f"industrial activity tier rated {tier}")
        return out

    def hazmat_agricultural(rd):
        out = []
        intensity = _num(
            rd, "hazmat_agricultural_metrics", "ag_chemical_intensity"
        )
        if intensity is not None and intensity >= 0.45:
            out.append(
                "agricultural chemical use intensity of "
                f"{intensity:.2f} on a 0-1 statewide scale "
                "(USDA Census of Agriculture)"
            )
        return out

    return {
        "flood": flood,
        "tornado": tornado,
        "winter_storm": winter_storm,
        "thunderstorm": thunderstorm,
        "straight_line_wind": straight_line_wind,
        "dam_failure": dam_failure,
        "extreme_heat": extreme_heat,
        "air_quality": air_quality,
        "vector_borne_disease": vector_borne_disease,
        "health": health,
        "active_shooter": active_shooter,
        "hazmat_industrial": hazmat_industrial,
        "hazmat_agricultural": hazmat_agricultural,
    }


_DRIVERS = _driver_builders()


def _derive_populations(domain: str, rd: Dict[str, Any]) -> List[str]:
    """Return locally elevated population groups for a domain, or []."""
    out: List[str] = []

    if domain in _NAT_HAZARD:
        elderly = _num(rd, f"{domain}_metrics", "elderly_vulnerability_pct")
        if elderly is not None and elderly >= _ELDERLY_PCT:
            out.append("Older adults (local share above the state average)")

        mh_pct = _num(rd, f"{domain}_metrics", "mobile_home_vulnerability_pct")
        mh_factor = _num(rd, f"{domain}_vulnerability_breakdown", "mobile_home_factor")
        if (mh_pct is not None and mh_pct >= _MOBILE_HOME_PCT) or (
            mh_factor is not None and mh_factor >= _MOBILE_HOME_FACTOR
        ):
            out.append("Residents of manufactured or mobile homes (locally common)")

        ses = _num(rd, f"{domain}_vulnerability_breakdown", "socioeconomic_svi")
        if ses is not None and ses >= _SVI_ELEVATED:
            out.append("Households with limited financial resources")

        transit = _num(rd, f"{domain}_vulnerability_breakdown",
                       "housing_transportation_svi")
        if transit is not None and transit >= _SVI_ELEVATED:
            out.append("People without reliable transportation")

    elif domain == "vector_borne_disease":
        fc = _num(rd, "vbd_metrics", "forest_cover_pct")
        if fc is not None and fc >= _FOREST_PCT:
            out.append("People who live or work near wooded areas")
        outdoor = _num(rd, "vbd_metrics", "outdoor_workforce_pct")
        if outdoor is not None and outdoor >= _OUTDOOR_PCT:
            out.append("Outdoor workers (locally large share)")
        elderly = _num(rd, "vbd_metrics", "elderly_vulnerability_pct")
        if elderly is not None and elderly >= _ELDERLY_PCT:
            out.append("Older adults (local share above the state average)")

    # Cap so a card stays scannable.
    return out[:3]


def derive_local_signals(domain: str, risk_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Return locally specific drivers and population highlights for a domain.

    Args:
        domain: canonical domain key (e.g. 'flood', 'health').
        risk_data: the jurisdiction or aggregated region risk_data dict.

    Returns:
        {"drivers": [...], "populations": [...]}; both lists may be empty when
        no genuinely local signal is present (e.g. proxy-modeled domains, or a
        region where a field did not survive aggregation).
    """
    if not isinstance(risk_data, dict) or not domain:
        return {"drivers": [], "populations": []}

    drivers: List[str] = []
    builder = _DRIVERS.get(domain)
    if builder is not None:
        try:
            drivers = [d for d in builder(risk_data) if d][:3]
        except Exception as e:  # never raise into the request
            logger.warning(f"summary driver derivation failed for {domain}: {e}")
            drivers = []

    try:
        populations = _derive_populations(domain, risk_data)
    except Exception as e:
        logger.warning(f"summary population derivation failed for {domain}: {e}")
        populations = []

    return {"drivers": drivers, "populations": populations}
