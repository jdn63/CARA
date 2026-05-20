"""
Strategic Preparedness Baseline for Infectious Disease Risk (Option 1)

Background
----------
The current infectious-disease scoring path is dominated by acute,
case-driven signals (NSSP ED visit percent, NNDSS weekly counts,
outbreak flags). When Wisconsin has a quiet surveillance week, the
score can drift below what a strategic planner intuitively expects:
"no flu cases in May does not mean low risk for next winter, and it
absolutely does not mean low risk for a measles importation into a
county with 78 percent MMR coverage."

This module produces a per-disease and aggregate "Strategic
Preparedness Baseline" that captures the *consequence side* of risk
independent of current activity. It is a Probability-times-Consequence
floor: if the county is vulnerable and the disease is high-consequence,
the displayed risk should never drop below this floor even on a
zero-case week.

The baseline is applied via max(current_acute, baseline) inside
utils/disease_surveillance.get_disease_metrics(). The acute path
remains unchanged; the baseline only ever raises the displayed score,
never lowers it.

Design notes
------------
- Pure function over already-cached inputs (SVI, MMR, primary-care
  density, COPD prevalence). No HTTP. Safe to call from the request
  path. If a helper returns None or raises, fall back to a neutral
  county value rather than crashing.
- Per-disease severity profiles live in
  config/risk_weights.yaml -> disease_severity_profiles. Every entry
  carries a literature citation and source URL.
- The aggregate baseline is a severity-weighted mean of per-disease
  baselines. This reflects the *portfolio* preparedness burden rather
  than letting any single rare-but-severe disease (e.g., H5N1)
  unilaterally dominate the floor.
- Upgrade path to Option 2: the per-disease scores are returned
  explicitly so a future "Two-Component Display" can render Current
  Activity vs Strategic Preparedness side by side without rewriting
  this module.

Formula
-------
For each disease:

    severity_index = (cfr_norm * 0.40
                      + hospitalization_norm * 0.30
                      + transmissibility_norm * 0.30
                     ) * vulnerable_population_multiplier

    county_vulnerability = mean(SVI, mmr_gap, copd_norm, (1 - pcp_norm))
                          # all four scaled to 0-1; missing inputs
                          # are replaced with a neutral 0.5 value

    response_capacity = mean(pcp_norm, (1 - SVI))
                          # 0 = no surge capacity, 1 = strong capacity

    raw_baseline = severity_index
                   * county_vulnerability
                   * (1.0 - 0.5 * response_capacity)

    per_disease_baseline = clamp(raw_baseline, BASELINE_FLOOR_MIN,
                                               BASELINE_FLOOR_MAX)

Aggregate baseline = sum(severity_index_i * per_disease_baseline_i)
                     / sum(severity_index_i)

The clamp prevents the floor from either disappearing (a severe disease
in a strong county still warrants attention) or saturating the score
(an active outbreak can still push the displayed value above the
baseline).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Output clamp for per-disease baseline scores. Tunable; the defaults
# keep the floor visible without ever exceeding mid-band so that the
# acute signal retains room to dominate during real outbreaks.
BASELINE_FLOOR_MIN = 0.10
BASELINE_FLOOR_MAX = 0.60


def _safe_float(value: Any, default: float) -> float:
    try:
        v = float(value)
        if v != v:  # NaN
            return default
        return v
    except (TypeError, ValueError):
        return default


def _get_county_vulnerability_inputs(county_name: str) -> Dict[str, Any]:
    """
    Pull already-cached county vulnerability inputs. Every lookup is
    wrapped so a failing helper does not crash the baseline
    computation. Missing values resolve to None and the consumer
    substitutes a neutral 0.5.
    """
    out: Dict[str, Any] = {
        'svi': None,
        'mmr_rate_pct': None,
        'copd_prevalence_pct': None,
        'primary_care_per_100k': None,
        'flu_vax_pct': None,
    }
    try:
        from utils.svi_data import get_svi_data
        svi_dict = get_svi_data(county_name) or {}
        svi_val = svi_dict.get('overall') if isinstance(svi_dict, dict) else None
        if svi_val is not None:
            out['svi'] = _safe_float(svi_val, 0.5)
    except Exception as exc:
        logger.debug(f"strategic_baseline: svi lookup failed for {county_name}: {exc}")

    try:
        from utils.dhs_data import get_vaccination_rate
        mmr = get_vaccination_rate(county_name)
        if mmr is not None:
            out['mmr_rate_pct'] = _safe_float(mmr, 87.8)
    except Exception as exc:
        logger.debug(f"strategic_baseline: mmr lookup failed for {county_name}: {exc}")

    try:
        from utils.health_metrics_data import get_copd_prevalence, get_primary_care_access, get_flu_vaccination_rate
        copd = get_copd_prevalence(county_name)
        if copd is not None:
            out['copd_prevalence_pct'] = _safe_float(copd, 7.0)
        pcp = get_primary_care_access(county_name)
        if pcp is not None:
            out['primary_care_per_100k'] = _safe_float(pcp, 65.0)
        flu = get_flu_vaccination_rate(county_name)
        if flu is not None:
            out['flu_vax_pct'] = _safe_float(flu, 45.0)
    except Exception as exc:
        logger.debug(f"strategic_baseline: health_metrics lookup failed for {county_name}: {exc}")

    return out


def _compute_county_factors(inputs: Dict[str, Any]) -> Tuple[float, float]:
    """
    Derive (county_vulnerability, response_capacity) from raw inputs.
    Both outputs are clamped to [0.0, 1.0]. Missing inputs default to
    a neutral 0.5 so a county with sparse data lands in the middle of
    the distribution rather than at either extreme.
    """
    svi = inputs.get('svi')
    svi_norm = _safe_float(svi, 0.5)
    svi_norm = max(0.0, min(1.0, svi_norm))

    mmr_pct = inputs.get('mmr_rate_pct')
    if mmr_pct is None:
        mmr_gap = 0.5
    else:
        # 95% is the herd-immunity benchmark; below 80% the gap saturates.
        mmr_gap = max(0.0, min(1.0, (95.0 - _safe_float(mmr_pct, 87.8)) / 15.0))

    copd_pct = inputs.get('copd_prevalence_pct')
    if copd_pct is None:
        copd_norm = 0.5
    else:
        # WI county range observed roughly 4.0% (Waukesha) to 10.5% (Forest).
        copd_norm = max(0.0, min(1.0, (_safe_float(copd_pct, 7.0) - 4.0) / 6.5))

    pcp = inputs.get('primary_care_per_100k')
    if pcp is None:
        pcp_norm = 0.5
    else:
        # AHRQ adequacy benchmark ~80/100k for primary care; saturate at 100.
        pcp_norm = max(0.0, min(1.0, _safe_float(pcp, 65.0) / 100.0))

    county_vulnerability = (svi_norm + mmr_gap + copd_norm + (1.0 - pcp_norm)) / 4.0
    response_capacity = (pcp_norm + (1.0 - svi_norm)) / 2.0
    return max(0.0, min(1.0, county_vulnerability)), max(0.0, min(1.0, response_capacity))


def _normalize_severity(profile: Dict[str, Any]) -> float:
    """
    Combine CFR + hospitalization + transmissibility into a 0-1
    severity index, then apply the vulnerable_population_multiplier.
    Normalization choices:
      - CFR: divide by 0.20 (any CFR at or above 20 percent saturates
        the dimension; covers H5N1 historical at 0.52 clamped to 1.0).
      - Hospitalization rate: divide by 0.50 (saturate at 50 percent).
      - R0: divide by 6.0 (covers seasonal influenza ~1.3 through
        measles ~15 mapped across the 0-1 range).
    """
    cfr = _safe_float(profile.get('case_fatality_rate'), 0.0)
    hosp = _safe_float(profile.get('hospitalization_rate'), 0.0)
    r0 = _safe_float(profile.get('r0'), 1.0)
    vuln_mult = _safe_float(profile.get('vulnerable_population_multiplier'), 1.0)

    cfr_norm = max(0.0, min(1.0, cfr / 0.20))
    hosp_norm = max(0.0, min(1.0, hosp / 0.50))
    r0_norm = max(0.0, min(1.0, r0 / 6.0))
    severity = (cfr_norm * 0.40 + hosp_norm * 0.30 + r0_norm * 0.30) * vuln_mult
    return max(0.0, min(2.0, severity))


def _get_severity_profiles() -> Dict[str, Dict[str, Any]]:
    """Read disease severity profiles from config; empty dict on failure."""
    try:
        from utils.config_manager import get_config_manager
        cfg = get_config_manager().config or {}
        profiles = cfg.get('disease_severity_profiles') or {}
        if not isinstance(profiles, dict):
            return {}
        return profiles
    except Exception as exc:
        logger.warning(f"strategic_baseline: cannot read disease_severity_profiles: {exc}")
        return {}


def compute_disease_baselines(county_name: str) -> Dict[str, Any]:
    """
    Compute per-disease and aggregate strategic preparedness baseline
    for one county. Returns a dict suitable for both the floor
    application in disease_surveillance and for direct dashboard
    rendering.

    The returned shape is stable; callers can iterate
    result['per_disease'] without checking for absence of any key.
    """
    inputs = _get_county_vulnerability_inputs(county_name)
    county_vulnerability, response_capacity = _compute_county_factors(inputs)
    profiles = _get_severity_profiles()

    per_disease: Dict[str, Dict[str, Any]] = {}
    severity_weighted_sum = 0.0
    severity_weight_total = 0.0

    for disease_key, profile in profiles.items():
        if not isinstance(profile, dict):
            continue
        severity = _normalize_severity(profile)
        raw_baseline = severity * county_vulnerability * (1.0 - 0.5 * response_capacity)
        clamped = max(BASELINE_FLOOR_MIN, min(BASELINE_FLOOR_MAX, raw_baseline))
        per_disease[disease_key] = {
            'baseline_score': round(clamped, 3),
            'raw_baseline': round(raw_baseline, 3),
            'severity_index': round(severity, 3),
            'display_name': profile.get('display_name', disease_key.replace('_', ' ').title()),
            'case_fatality_rate': profile.get('case_fatality_rate'),
            'hospitalization_rate': profile.get('hospitalization_rate'),
            'r0': profile.get('r0'),
            'vulnerable_population': profile.get('vulnerable_population_description', ''),
            'citation': profile.get('citation', ''),
            'citation_url': profile.get('citation_url', ''),
        }
        if severity > 0:
            severity_weighted_sum += severity * clamped
            severity_weight_total += severity

    if severity_weight_total > 0:
        aggregate = severity_weighted_sum / severity_weight_total
    else:
        aggregate = BASELINE_FLOOR_MIN

    aggregate = max(BASELINE_FLOOR_MIN, min(BASELINE_FLOOR_MAX, aggregate))

    return {
        'county': county_name,
        'aggregate_baseline': round(aggregate, 3),
        'per_disease': per_disease,
        'county_factors': {
            'county_vulnerability': round(county_vulnerability, 3),
            'response_capacity': round(response_capacity, 3),
            'inputs': inputs,
        },
        'method': (
            'Strategic Preparedness Baseline (Option 1): per-disease '
            'severity index times county vulnerability times '
            '(1 - 0.5 * response capacity), clamped to '
            f'[{BASELINE_FLOOR_MIN}, {BASELINE_FLOOR_MAX}], aggregated as '
            'severity-weighted mean across the disease portfolio.'
        ),
        'method_label': 'Strategic Preparedness Baseline (P x C floor)',
        'floor_range': [BASELINE_FLOOR_MIN, BASELINE_FLOOR_MAX],
    }


def get_aggregate_baseline(county_name: str) -> float:
    """Convenience accessor returning just the aggregate baseline score."""
    try:
        return compute_disease_baselines(county_name).get(
            'aggregate_baseline', BASELINE_FLOOR_MIN
        )
    except Exception as exc:
        logger.warning(f"get_aggregate_baseline failed for {county_name}: {exc}")
        return BASELINE_FLOOR_MIN
