import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_baseline_data_cache = None

TRIBAL_COUNTY_MAPPING = {
    'HoChunk': 'Jackson',
    'Ho-Chunk': 'Jackson',
    'Menominee': 'Menominee',
    'Oneida': 'Brown',
    'Lac du Flambeau': 'Vilas',
    'Bad River': 'Ashland',
    'Red Cliff': 'Bayfield',
    'Potawatomi': 'Forest',
    'St. Croix': 'Burnett',
    'Sokaogon': 'Forest',
    'Lac Courte Oreilles': 'Sawyer'
}

TRIBAL_KEYWORDS = ['Ho-Chunk', 'HoChunk', 'Menominee', 'Oneida', 'Lac du Flambeau',
                   'Bad River', 'Red Cliff', 'Potawatomi', 'St. Croix', 'Sokaogon',
                   'Lac Courte Oreilles']


def _is_tribal(county_name: str) -> bool:
    return any(t in county_name for t in TRIBAL_KEYWORDS)


def _resolve_tribal_county(county_name: str) -> str:
    for tribal_name, mapped in TRIBAL_COUNTY_MAPPING.items():
        if tribal_name in county_name:
            logger.info(f"Using {mapped} County data for {county_name}")
            return mapped
    return county_name


def load_baseline_data() -> Dict[str, Any]:
    global _baseline_data_cache
    if _baseline_data_cache is not None:
        return _baseline_data_cache

    try:
        path = 'data/disease/wisconsin_vector_borne_baseline.json'
        if os.path.exists(path):
            with open(path) as f:
                _baseline_data_cache = json.load(f)
            logger.info("Loaded vector-borne disease baseline data")
            return _baseline_data_cache
    except Exception as e:
        logger.warning(f"Error loading vector-borne disease baseline data: {e}")

    _baseline_data_cache = {}
    return _baseline_data_cache


def _get_real_county_data(county_name: str) -> Optional[Dict[str, Any]]:
    try:
        from utils.vbd_data_fetcher import get_county_real_data
        return get_county_real_data(county_name)
    except Exception as e:
        logger.debug(f"Could not load real VBD data for {county_name}: {e}")
        return None


def _get_tier_score(tier: str, baseline: Dict[str, Any]) -> float:
    tier_scores = baseline.get('tier_scores', {})
    return tier_scores.get(tier, 0.45)


def _get_deer_density_score(density: str, baseline: Dict[str, Any]) -> float:
    density_scores = baseline.get('deer_density_scores', {})
    return density_scores.get(density, 0.45)


def _get_seasonal_factor() -> float:
    month = datetime.now().month

    tick_active = [4, 5, 6, 7, 8, 9, 10]
    tick_peak = [5, 6, 7]
    mosquito_active = [6, 7, 8, 9]
    mosquito_peak = [7, 8]

    tick_factor = 0.0
    if month in tick_peak:
        tick_factor = 1.0
    elif month in tick_active:
        tick_factor = 0.6
    else:
        tick_factor = 0.15

    mosquito_factor = 0.0
    if month in mosquito_peak:
        mosquito_factor = 1.0
    elif month in mosquito_active:
        mosquito_factor = 0.6
    else:
        mosquito_factor = 0.10

    combined = (tick_factor * 0.75) + (mosquito_factor * 0.25)
    return max(0.15, min(1.0, combined))


def _get_climate_multiplier(baseline: Dict[str, Any]) -> float:
    climate = baseline.get('climate_impact', {})
    tick_mult = climate.get('tick_range_expansion', {}).get('multiplier', 1.15)
    season_mult = climate.get('extended_season', {}).get('multiplier', 1.10)
    mosquito_mult = climate.get('mosquito_habitat', {}).get('multiplier', 1.12)

    combined = (tick_mult * 0.50) + (season_mult * 0.30) + (mosquito_mult * 0.20)
    return combined


def get_all_svi_themes(county_name: str) -> Dict[str, float]:
    svi_data = get_svi_data(county_name)
    return {
        'overall': svi_data.get('overall', 0.5),
        'socioeconomic': svi_data.get('socioeconomic', 0.5),
        'household_composition': svi_data.get('household_composition', 0.5),
        'minority_status': svi_data.get('minority_status', 0.5),
        'housing_transportation': svi_data.get('housing_transportation', 0.5)
    }


def get_census_demographics(county_name: str) -> Dict[str, float]:
    try:
        from utils.census_data_loader import wisconsin_census
        elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name) or 18.7
        population = wisconsin_census.get_county_population(county_name) or 80000
    except Exception as e:
        logger.warning(f"Census data loading failed for {county_name}: {e}")
        elderly_pct = 18.7
        population = 80000

    elderly_factor = min(1.0, max(0.05, (elderly_pct - 10.0) / 25.0))
    rural_factor = min(1.0, max(0.0, 1.0 - (population / 300000.0)))

    return {
        'elderly_pct': elderly_pct,
        'elderly_factor': elderly_factor,
        'population': population,
        'rural_factor': rural_factor
    }


def calculate_vector_borne_disease_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    baseline = load_baseline_data()
    county_data = baseline.get('county_baselines', {}).get(county_name, None)

    if county_data is None:
        logger.warning(f"No vector-borne disease baseline for {county_name}, using defaults")
        county_data = {
            'lyme_tier': 'moderate',
            'wnv_tier': 'low',
            'forest_cover_pct': 30,
            'deer_density': 'moderate',
            'outdoor_workforce_pct': 10
        }

    real_data = _get_real_county_data(county_name)
    using_real_data = real_data is not None

    svi = get_all_svi_themes(county_name)
    census = get_census_demographics(county_name)
    seasonal_factor = _get_seasonal_factor()
    climate_mult = _get_climate_multiplier(baseline)

    # Defaults for shrinkage / reliability metadata (overwritten when real
    # data is available; kept here so the metrics dict has a stable shape
    # whether or not the EPHT CSVs have populated this county yet).
    lyme_rate_observed = None
    wnv_rate_observed = None
    lyme_rate_shrunk = None
    wnv_rate_shrunk = None
    lyme_shrinkage_weight = None
    wnv_shrinkage_weight = None
    lyme_rate_ci = None
    wnv_rate_ci = None
    lyme_reliability = 'low'
    wnv_reliability = 'low'
    wnv_cases_annual = None

    if using_real_data:
        from utils.vbd_data_fetcher import (
            rate_to_score,
            classify_lyme_rate,
            classify_wnv_rate,
            get_statewide_background_rates,
            apply_credibility_shrinkage,
            compute_reliability,
            poisson_rate_ci,
            LYME_PRIOR_STRENGTH_K,
            WNV_PRIOR_STRENGTH_K,
        )

        lyme_rate_observed = real_data.get('lyme_avg_annual_rate') or 0
        wnv_rate_observed = real_data.get('wnv_avg_annual_rate') or 0
        wnv_total_5yr = real_data.get('wnv_total_cases_5yr') or 0
        lyme_cases = real_data.get('lyme_avg_annual_cases') or 0
        wnv_cases_5yr = real_data.get('wnv_total_cases_5yr') or 0
        wnv_cases_annual = (
            real_data.get('wnv_avg_annual_cases')
            if real_data.get('wnv_avg_annual_cases') is not None
            else (wnv_cases_5yr / 5.0 if wnv_cases_5yr else 0.0)
        )

        # Review finding H9: shrink crude rates toward the statewide
        # background before they reach the scoring curve. Small counties
        # (Florence, Menominee, Iron) have annual case counts in the
        # single digits, so the unsmoothed rate per 100k swings by tens
        # of points on a single observed case. The Buhlmann credibility
        # weight w = c / (c + k) is equivalent to the posterior mean of
        # a Poisson-Gamma model and is the standard small-area correction
        # for rare-event incidence rates.
        state_rates = get_statewide_background_rates()
        lyme_shrink = apply_credibility_shrinkage(
            observed_rate=lyme_rate_observed,
            observed_cases=lyme_cases,
            state_rate=state_rates['lyme'],
            prior_strength_k=LYME_PRIOR_STRENGTH_K,
        )
        wnv_shrink = apply_credibility_shrinkage(
            observed_rate=wnv_rate_observed,
            observed_cases=wnv_cases_annual or 0.0,
            state_rate=state_rates['wnv'],
            prior_strength_k=WNV_PRIOR_STRENGTH_K,
        )
        lyme_rate_shrunk = lyme_shrink['rate']
        wnv_rate_shrunk = wnv_shrink['rate']
        lyme_shrinkage_weight = lyme_shrink['weight']
        wnv_shrinkage_weight = wnv_shrink['weight']

        # Score off the shrunk rate so the existing scoring curve does not
        # need to be modified. Classification tiers still use the observed
        # rate so the user-visible "Lyme tier" matches what EPHT publishes
        # in its county tables, but the SCORE that drives the composite is
        # smoothed.
        lyme_score = rate_to_score(lyme_rate_shrunk, 'lyme')
        wnv_score = rate_to_score(wnv_rate_shrunk, 'wnv')

        lyme_tier = classify_lyme_rate(lyme_rate_observed)
        wnv_tier = classify_wnv_rate(wnv_rate_observed, wnv_total_5yr)

        # Per-disease and combined reliability tiers (low / medium / high).
        # The combined tier follows the weakest disease (precautionary).
        lyme_reliability = compute_reliability(lyme_cases)
        wnv_reliability = compute_reliability(wnv_cases_annual or 0.0)

        # 95% approximate CIs on the OBSERVED (unshrunk) rate, so the UI
        # can show a confidence band around the per-100k figure that EPHT
        # publishes. Shrunk rates intentionally do not get a CI -- they
        # are a posterior point estimate and a credibility interval would
        # require carrying the full posterior, which is out of scope.
        lyme_rate_ci = poisson_rate_ci(lyme_cases, lyme_rate_observed)
        wnv_rate_ci = poisson_rate_ci(wnv_cases_annual or 0.0, wnv_rate_observed)

        # Preserve the legacy names downstream code consumes.
        lyme_rate = lyme_rate_shrunk
        wnv_rate = wnv_rate_shrunk

        logger.info(
            f"VBD real data for {county_name}: "
            f"Lyme observed={lyme_rate_observed:.1f}/100k cases={lyme_cases:.1f} "
            f"shrunk={lyme_rate_shrunk:.1f} w={lyme_shrinkage_weight:.2f} "
            f"reliability={lyme_reliability}; "
            f"WNV observed={wnv_rate_observed:.2f}/100k cases={(wnv_cases_annual or 0):.2f} "
            f"shrunk={wnv_rate_shrunk:.2f} w={wnv_shrinkage_weight:.2f} "
            f"reliability={wnv_reliability}"
        )
    else:
        lyme_score = _get_tier_score(county_data['lyme_tier'], baseline)
        wnv_score = _get_tier_score(county_data['wnv_tier'], baseline)
        lyme_tier = county_data['lyme_tier']
        wnv_tier = county_data['wnv_tier']
        lyme_rate = None
        wnv_rate = None
        lyme_cases = None
        wnv_cases_5yr = None

    forest_cover_factor = min(1.0, county_data['forest_cover_pct'] / 100.0)
    deer_density_score = _get_deer_density_score(county_data['deer_density'], baseline)
    outdoor_workforce_factor = min(1.0, county_data['outdoor_workforce_pct'] / 25.0)

    case_rate_composite = (lyme_score * 0.65) + (wnv_score * 0.35)
    land_cover_factor = (forest_cover_factor * 0.60) + (deer_density_score * 0.40)

    # Combined reliability across both diseases (weakest tier wins). When
    # the underlying case counts are too small to support a stable rate,
    # the review (H9) requires that we NOT amplify that rate with the
    # climate trend multiplier -- doing so layers an additional source of
    # spurious variation on top of an already noisy baseline. The gate is
    # graduated: low reliability drops the climate boost entirely, medium
    # reliability halves it, high reliability keeps the full boost.
    if using_real_data:
        from utils.vbd_data_fetcher import combine_reliability
        combined_reliability = combine_reliability(lyme_reliability, wnv_reliability)
    else:
        # No EPHT data => tier-based fallback; treat as low-reliability so
        # we do not stack a climate boost on top of a default tier estimate.
        combined_reliability = 'low'

    raw_climate_trend = min(1.0, case_rate_composite * climate_mult) - case_rate_composite
    if combined_reliability == 'low':
        climate_trend_gated = 0.0
    elif combined_reliability == 'medium':
        climate_trend_gated = raw_climate_trend * 0.5
    else:
        climate_trend_gated = raw_climate_trend

    exposure_factors = {
        'historical_case_rates': case_rate_composite,
        'land_cover_risk': land_cover_factor,
        'seasonal_activity': seasonal_factor,
        'climate_trend': climate_trend_gated,
    }

    exposure_score = min(1.0, (
        (exposure_factors['historical_case_rates'] * 0.45) +
        (exposure_factors['land_cover_risk'] * 0.25) +
        (exposure_factors['seasonal_activity'] * 0.15) +
        (exposure_factors['climate_trend'] * 0.15)
    ))

    if discipline == 'em':
        vulnerability_score = min(1.0, (
            (outdoor_workforce_factor * 0.25) +
            (census['elderly_factor'] * 0.20) +
            (census['rural_factor'] * 0.20) +
            (svi['socioeconomic'] * 0.15) +
            (svi['household_composition'] * 0.10) +
            (svi['minority_status'] * 0.10)
        ))

        resilience_raw = 0.45
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.10)
        resilience_raw += ((1.0 - census['rural_factor']) * 0.15)

        surveillance_counties = ['Milwaukee', 'Dane', 'Brown', 'Waukesha', 'La Crosse',
                                 'Marathon', 'Eau Claire', 'Outagamie', 'Winnebago']
        if county_name in surveillance_counties:
            resilience_raw += 0.20
        elif census['population'] > 50000:
            resilience_raw += 0.10

        resilience_raw = max(0.1, min(0.9, resilience_raw))
    else:
        vulnerability_score = min(1.0, (
            (outdoor_workforce_factor * 0.20) +
            (census['elderly_factor'] * 0.20) +
            (census['rural_factor'] * 0.15) +
            (svi['socioeconomic'] * 0.20) +
            (svi['household_composition'] * 0.15) +
            (svi['minority_status'] * 0.10)
        ))

        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.15)
        resilience_raw += ((1.0 - census['rural_factor']) * 0.10)

        well_resourced = ['Milwaukee', 'Dane', 'Brown', 'Waukesha', 'La Crosse']
        if county_name in well_resourced:
            resilience_raw += 0.20
        elif county_name in ['Marathon', 'Eau Claire', 'Outagamie', 'Winnebago', 'Rock']:
            resilience_raw += 0.10

        resilience_raw = max(0.1, min(0.9, resilience_raw))

    # Use the vector_borne_disease health-impact factor (1.2 default), NOT the
    # flood HIF that was used previously by mistake. VBD health consequences
    # (Lyme, WNV) are unrelated to flood health burden, so using the flood key
    # was producing incorrectly-amplified VBD scores in flood-prone counties
    # and incorrectly-dampened VBD scores in non-flood counties.
    health_factor = 1.2
    try:
        health_factor = get_health_impact_factor(county_name, 'vector_borne_disease')
    except Exception:
        health_factor = 1.2

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    season_label = _get_season_label()

    metrics = {
        'lyme_disease_tier': lyme_tier,
        'west_nile_virus_tier': wnv_tier,
        'forest_cover_pct': county_data['forest_cover_pct'],
        'deer_density': county_data['deer_density'],
        'outdoor_workforce_pct': county_data['outdoor_workforce_pct'],
        'seasonal_risk_level': season_label,
        'seasonal_factor': round(seasonal_factor, 2),
        'climate_trend_impact': f"+{int((climate_mult - 1.0) * 100)}%",
        'elderly_vulnerability_pct': round(census['elderly_pct'], 1),
        'diseases_assessed': ['Lyme Disease', 'West Nile Virus', 'Anaplasmosis', 'Ehrlichiosis'],
        'using_real_data': using_real_data,
    }

    if using_real_data:
        # 'lyme_incidence_rate' historically held the value that drives
        # the score; under H9 that is now the shrunk posterior rate.
        # The OBSERVED (unshrunk) rate is exposed alongside it so the UI
        # can show both and explain the difference.
        metrics['lyme_incidence_rate'] = lyme_rate  # shrunk; drives the score
        metrics['lyme_incidence_rate_observed'] = lyme_rate_observed
        metrics['lyme_incidence_rate_shrunk'] = lyme_rate_shrunk
        metrics['lyme_shrinkage_weight'] = round(lyme_shrinkage_weight, 3) if lyme_shrinkage_weight is not None else None
        metrics['lyme_rate_ci_low'] = round(lyme_rate_ci['low'], 1) if lyme_rate_ci else None
        metrics['lyme_rate_ci_high'] = round(lyme_rate_ci['high'], 1) if lyme_rate_ci else None
        metrics['lyme_reliability'] = lyme_reliability
        metrics['lyme_avg_annual_cases'] = lyme_cases

        metrics['wnv_incidence_rate'] = wnv_rate  # shrunk; drives the score
        metrics['wnv_incidence_rate_observed'] = wnv_rate_observed
        metrics['wnv_incidence_rate_shrunk'] = wnv_rate_shrunk
        metrics['wnv_shrinkage_weight'] = round(wnv_shrinkage_weight, 3) if wnv_shrinkage_weight is not None else None
        metrics['wnv_rate_ci_low'] = round(wnv_rate_ci['low'], 2) if wnv_rate_ci else None
        metrics['wnv_rate_ci_high'] = round(wnv_rate_ci['high'], 2) if wnv_rate_ci else None
        metrics['wnv_reliability'] = wnv_reliability
        metrics['wnv_avg_annual_cases'] = round(wnv_cases_annual, 2) if wnv_cases_annual is not None else None
        metrics['wnv_total_cases_5yr'] = wnv_cases_5yr

        metrics['vbd_reliability_combined'] = combined_reliability
        metrics['vbd_climate_gate'] = (
            'full' if combined_reliability == 'high'
            else 'half' if combined_reliability == 'medium'
            else 'suppressed'
        )

        data_years = real_data.get('lyme_data_years', [])
        if data_years:
            metrics['data_period'] = f"{min(data_years)}-{max(data_years)}"
        else:
            try:
                from utils.vbd_data_fetcher import load_real_vbd_data
                meta = load_real_vbd_data().get('metadata', {})
                metrics['data_period'] = meta.get('data_years', '2019-2024')
            except Exception:
                metrics['data_period'] = '2019-2024'

    data_sources = [
        'WI DHS EPHT Lyme Disease Surveillance (county-level incidence rates)' if using_real_data else 'Wisconsin DHS Tick-Borne Disease Surveillance Reports',
        'WI DHS Vectorborne Disease Program (WNV county case data)' if using_real_data else 'CDC ArboNET West Nile Virus Surveillance',
        'USDA Forest Service NLCD 2021 Land Cover Data',
        'Wisconsin DNR Deer Population Estimates',
        'CDC Social Vulnerability Index (SVI)',
        'U.S. Census Bureau ACS Demographics',
        'NOAA/WICCI Climate Projections'
    ]

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor,
            'climate_multiplier': climate_mult,
            'seasonal_factor': seasonal_factor
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'outdoor_workforce_factor': outdoor_workforce_factor,
            'elderly_factor': census['elderly_factor'],
            'rural_factor': census['rural_factor'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status']
        },
        'metrics': metrics,
        'data_sources': data_sources
    }


def _get_season_label() -> str:
    """Return a human-readable label for the current vector-borne
    disease season.

    Review finding M11 (2026-05-20): the previous month-by-month if/elif
    chain put the tick branches before the mosquito branches with
    overlapping months (e.g. July and August appeared in both tick and
    mosquito conditions), making the mosquito-only branches unreachable.
    The condition order is now month-disjoint, and overlap months
    return a combined "tick + mosquito" label so neither vector is
    silently dropped from the UI.
    """
    month = datetime.now().month
    # Combined peak window: ticks (May-Jul) overlap mosquitoes (Jul-Aug)
    # in July, and tick shoulder (Aug-Oct) overlaps mosquito shoulder
    # (Jun, Sep) in August/September.
    if month == 7:
        return 'Peak tick and mosquito season'
    if month == 8:
        return 'Peak mosquito and active tick season'
    if month in (5, 6):
        return 'Peak tick season'
    if month == 9:
        return 'Active tick and mosquito season'
    if month in (4, 10):
        return 'Active tick season'
    if month in (11, 12, 1, 2, 3):
        return 'Low season (winter)'
    return 'Moderate activity'
