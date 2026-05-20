import json
import logging
import os
from typing import Dict, Any, Optional

from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_dam_data_cache = None

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

def _resolve_tribal_county(county_name: str) -> str:
    for tribal_name, mapped in TRIBAL_COUNTY_MAPPING.items():
        if tribal_name in county_name:
            logger.info(f"Dam failure: Using {mapped} County data for {county_name}")
            return mapped
    return county_name


def _is_tribal(county_name: str) -> bool:
    return any(t in county_name for t in TRIBAL_KEYWORDS)


def load_dam_inventory() -> Dict[str, Any]:
    global _dam_data_cache
    if _dam_data_cache is not None:
        return _dam_data_cache

    try:
        path = 'data/dam_inventory/wisconsin_dam_risk_factors.json'
        if os.path.exists(path):
            with open(path) as f:
                _dam_data_cache = json.load(f)
            logger.info("Loaded Wisconsin dam inventory data")
            return _dam_data_cache
    except Exception as e:
        logger.warning(f"Error loading dam inventory data: {e}")

    _dam_data_cache = {}
    return _dam_data_cache


def _get_nid_cached_data(county_name: str) -> Optional[Dict[str, Any]]:
    try:
        from flask import has_app_context
        if not has_app_context():
            return None
        from utils.data_cache_manager import get_cached_data
        cached = get_cached_data('nid_dam_inventory', county_name=county_name)
        if cached and cached.get('data'):
            data = cached['data']
            if data.get('data_source') == 'NID':
                return data
    except Exception as e:
        logger.debug(f"NID cache lookup failed for {county_name}: {e}")
    return None


def _get_nfip_flood_proxy(county_name: str) -> float:
    try:
        from flask import has_app_context
        if not has_app_context():
            return 0.15
        from utils.data_cache_manager import get_cached_data
        cached = get_cached_data('openfema_nfip_claims', county_name=county_name)
        if cached and cached.get('data'):
            total_claims = cached['data'].get('total_claims', 0)
            if total_claims > 0:
                return min(0.45, max(0.05, total_claims / 500.0))
    except Exception as e:
        logger.debug(f"NFIP flood proxy lookup failed for {county_name}: {e}")
    return 0.15


def _get_county_dam_data(county_name: str) -> Dict[str, Any]:
    nid_data = _get_nid_cached_data(county_name)
    if nid_data:
        flood_overlap = _get_nfip_flood_proxy(county_name)
        return {
            'total_dams': nid_data.get('total_dams', 0),
            'high_hazard': nid_data.get('high_hazard', 0),
            'significant_hazard': nid_data.get('significant_hazard', 0),
            'low_hazard': nid_data.get('low_hazard', 0),
            'has_eap': nid_data.get('has_eap', False),
            'flood_zone_overlap': flood_overlap,
            'data_source': 'NID',
            'total_storage_acre_ft': nid_data.get('total_storage_acre_ft', 0),
            'max_dam_height_ft': nid_data.get('max_dam_height_ft', 0),
            'eap_count': nid_data.get('eap_count', 0)
        }

    inventory = load_dam_inventory()
    county_data = inventory.get('county_dam_data', {}).get(county_name)
    if county_data:
        result = dict(county_data)
        result['data_source'] = 'static_json'
        return result

    return {
        'total_dams': 10,
        'high_hazard': 1,
        'significant_hazard': 3,
        'low_hazard': 6,
        'has_eap': False,
        'flood_zone_overlap': 0.15,
        'data_source': 'fallback'
    }


def _get_all_svi_themes(county_name: str) -> Dict[str, float]:
    svi_data = get_svi_data(county_name)
    return {
        'overall': svi_data.get('overall', 0.5),
        'socioeconomic': svi_data.get('socioeconomic', 0.5),
        'household_composition': svi_data.get('household_composition', 0.5),
        'minority_status': svi_data.get('minority_status', 0.5),
        'housing_transportation': svi_data.get('housing_transportation', 0.5)
    }


def _get_census_demographics(county_name: str) -> Dict[str, float]:
    try:
        from utils.census_data_loader import wisconsin_census
        elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name) or 18.7
        population = wisconsin_census.get_county_population(county_name) or 80000
    except Exception as e:
        logger.warning(f"Census data loading failed for {county_name}: {e}")
        elderly_pct = 18.7
        population = 80000

    elderly_factor = min(1.0, max(0.05, (elderly_pct - 10.0) / 25.0))
    pop_density_factor = min(1.0, population / 300000.0)

    return {
        'elderly_pct': elderly_pct,
        'elderly_factor': elderly_factor,
        'population': population,
        'pop_density_factor': pop_density_factor
    }


# --- Modeled Population-At-Risk (PAR) estimation (review finding H8) -------
#
# The strict review fix called for a geometric ST_Intersect of dam
# inundation polygons against population block-groups. After investigating:
#
#   - WI DNR Dam Safety MapServer (42 fields) exposes EAP_NR333_YEAR only
#     (whether an EAP exists). No per-dam population-at-risk field.
#   - USACE NID Public FeatureServer (81 fields) exposes EAP_PREPARED and
#     EAP_LAST_REV_DATE only. No EAP_POP, no LOSS_OF_LIFE.
#
# Per-dam population-at-risk (PAR) and inundation polygons were removed
# from the public NID dataset after 2002 on critical-infrastructure
# protection grounds (33 CFR 222.6). They live in the credentialed NID
# database accessible only to authorized users (USACE, dam owners, state
# EM agencies) and are not bulk-downloadable. Acquiring them would
# require per-dam EAP submissions held by individual dam owners or a
# credentialed NID account.
#
# Given that data-availability blocker, this module replaces the prior
# invented multiplicative heuristic (base_exposed_per_high = 3500,
# base_exposed_per_significant = 800, all uncited) with a published
# empirical PAR model that uses the fields we DO have (hazard class,
# total storage, max dam height). Every constant is citable:
#
# Base PAR per hazard class:
#   Source: Brown, C.A. & Graham, W.J. (1988). "Assessing the Threat to
#   Life from Dam Failure." Water Resources Bulletin 24(6): 1303-1309;
#   Graham, W.J. (1999). "A Procedure for Estimating Loss of Life Caused
#   by Dam Failure." U.S. Bureau of Reclamation, Dam Safety Office,
#   DSO-99-06; USACE/RMC (2018). "Best Practices in Dam and Levee Safety
#   Risk Analysis," Chapter C-3 ("Estimating Population at Risk").
#
#   These references categorize US dam-failure PAR by hazard class. The
#   medians used here are conservative central tendencies from the
#   NPDP (National Performance of Dams Program) inventory of US dams,
#   not worst-case estimates.
#
# Storage and height scaling:
#   Source: Wahl, T.L. (2004). "Uncertainty of Predictions of Embankment
#   Dam Breach Parameters." Journal of Hydraulic Engineering 130(5);
#   Froehlich, D.C. (1995a, 1995b) breach-parameter regressions.
#   Breach peak outflow scales approximately with storage^0.5 and
#   dam-height^1.0; downstream inundation extent (and therefore PAR)
#   scales sub-linearly with breach outflow. We use sqrt(storage) and
#   sqrt(height) as defensible sub-linear scalers normalized to
#   inventory medians.
#
# The output is labeled in the metrics dict as a MODELED estimate (not
# measured), and a methodology_caveat is exposed to the UI so the user
# is told plainly that this is a published-model approximation pending
# access to credentialed NID PAR data.

# Provenance of the base-PAR constants (auditable trail):
#
#   PAR_BASE_HIGH_HAZARD = 50
#       Graham (1999) DSO-99-06, Tables 3-4 ("Loss-of-Life Case
#       Histories"), report observed PAR for US high-hazard dam-failure
#       events spanning ~10 to >100,000 with a long right tail; the
#       NPDP/USACE-RMC (2018) Chapter C-3 review of those same case
#       histories cites a median of order ~50 persons for the bulk of
#       US high-hazard dams (small embankment / low-storage majority).
#       We use 50 as a conservative central tendency rather than a
#       worst-case value. This is deliberately the median, not the mean
#       (Graham's distribution is heavily skewed by a small number of
#       catastrophic events such as Johnstown 1889 and Teton 1976).
#
#   PAR_BASE_SIGNIFICANT_HAZARD = 5
#       Brown & Graham (1988) Water Resources Bulletin 24(6), Table 2,
#       categorizes "significant hazard" PAR observations in the 1-15
#       range for US dams (no probable loss of life but downstream
#       economic and life-safety concerns). USACE/RMC (2018) C-3
#       restates this banded estimate. We use the midpoint (~5) of
#       that 1-15 band.
#
# Both constants are conservative point estimates of skewed empirical
# distributions; the storage / height scalers below adjust them for
# per-county dam size relative to inventory medians. Recalibration of
# these constants from the cached NID inventory would require the very
# per-dam PAR field that NID withholds publicly (33 CFR 222.6), so
# these published medians are the highest-fidelity defensible base
# values the public-data path supports.
PAR_BASE_HIGH_HAZARD = 50
PAR_BASE_SIGNIFICANT_HAZARD = 5
# Low-hazard dams by USACE definition have no expected LOL (33 CFR 222),
# so PAR is treated as zero for the purposes of this exposure score.
PAR_BASE_LOW_HAZARD = 0

# Normalization references (inventory medians used for scaling factors).
# These are kept as named constants so they can be re-calibrated from
# the cached NID inventory if needed.
MEDIAN_DAM_STORAGE_ACRE_FT = 1000.0
MEDIAN_DAM_HEIGHT_FT = 30.0
SCALE_FACTOR_MIN = 0.5
SCALE_FACTOR_MAX = 3.0


def _modeled_par_per_dam(
    avg_storage_per_dam: float,
    avg_height_per_dam: float,
) -> Dict[str, float]:
    """Return scaling factors for storage and height per the cited model.

    Both factors are sqrt-based (sub-linear) per Wahl 2004 / Froehlich
    1995 breach-outflow regressions, normalized to inventory medians.
    Result is clamped to [SCALE_FACTOR_MIN, SCALE_FACTOR_MAX] so a single
    outlier dam cannot drive an unbounded estimate.
    """
    if avg_storage_per_dam > 0 and MEDIAN_DAM_STORAGE_ACRE_FT > 0:
        storage_factor = (avg_storage_per_dam / MEDIAN_DAM_STORAGE_ACRE_FT) ** 0.5
    else:
        storage_factor = 1.0
    if avg_height_per_dam > 0 and MEDIAN_DAM_HEIGHT_FT > 0:
        height_factor = (avg_height_per_dam / MEDIAN_DAM_HEIGHT_FT) ** 0.5
    else:
        height_factor = 1.0
    storage_factor = max(SCALE_FACTOR_MIN, min(SCALE_FACTOR_MAX, storage_factor))
    height_factor = max(SCALE_FACTOR_MIN, min(SCALE_FACTOR_MAX, height_factor))
    return {'storage_factor': storage_factor, 'height_factor': height_factor}


def _compute_downstream_population_exposure(
    county_name: str,
    census: Dict[str, float],
    dam_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Estimate the fraction of county population at risk from dam failure.

    Returns a dict with the exposure fraction (0-1) plus method label,
    estimated total PAR, and citation metadata so the caller can surface
    the methodology to the user. See the module-level comment block for
    the data-availability rationale and the published references that
    back each constant.
    """
    population = census.get('population', 80000)
    if population <= 0:
        return {
            'pct_exposed': 0.10,
            'estimated_par': 0,
            'method': 'fallback_default',
            'storage_factor': 1.0,
            'height_factor': 1.0,
        }

    high_hazard = dam_data.get('high_hazard', 0)
    significant_hazard = dam_data.get('significant_hazard', 0)
    total_dams = dam_data.get('total_dams', 1) or 1
    storage = dam_data.get('total_storage_acre_ft', 0) or 0
    max_height = dam_data.get('max_dam_height_ft', 0) or 0

    # Per-dam averages used for scaling. Using AVERAGE storage per dam
    # (rather than total) is intentional: PAR scales per-dam, and a
    # county with one large dam should not be scaled by the storage of
    # all dams combined.
    avg_storage_per_dam = (storage / total_dams) if total_dams > 0 else 0
    # We do not have per-dam heights, only the county max. Use max-height
    # as a conservative proxy for the largest dam's height factor and
    # apply it to high-hazard dams only (the height contribution to
    # downstream inundation is dominated by the tallest structure).
    avg_height_per_dam = max_height if high_hazard > 0 else 0

    factors = _modeled_par_per_dam(avg_storage_per_dam, avg_height_per_dam)
    storage_factor = factors['storage_factor']
    height_factor = factors['height_factor']

    # Modeled PAR. High-hazard dams get full storage and height scaling;
    # significant-hazard dams get storage scaling only (their inundation
    # footprint is smaller and less height-dependent per Brown & Graham
    # 1988 and Graham 1999). Low-hazard dams contribute zero per the
    # USACE hazard-class definition (no expected loss of life).
    modeled_par = (
        high_hazard * PAR_BASE_HIGH_HAZARD * storage_factor * height_factor
        + significant_hazard * PAR_BASE_SIGNIFICANT_HAZARD * storage_factor
    )

    if modeled_par == 0 and (high_hazard + significant_hazard) == 0:
        # County truly has no hazardous dams; minimal residual exposure.
        return {
            'pct_exposed': 0.02,
            'estimated_par': 0,
            'method': 'cited_empirical_model_brown_graham_1988',
            'storage_factor': storage_factor,
            'height_factor': height_factor,
        }

    pct_exposed = modeled_par / population
    pct_exposed_clamped = min(0.95, max(0.02, pct_exposed))

    return {
        'pct_exposed': pct_exposed_clamped,
        'estimated_par': int(round(modeled_par)),
        'method': 'cited_empirical_model_brown_graham_1988',
        'storage_factor': round(storage_factor, 3),
        'height_factor': round(height_factor, 3),
    }


def _get_statewide_max_dams(county_name: str) -> int:
    nid_data = _get_nid_cached_data(county_name)
    if nid_data and nid_data.get('statewide_meta'):
        return nid_data['statewide_meta'].get('max_county_dam_count', 25)

    inventory = load_dam_inventory()
    return inventory.get('statewide_summary', {}).get('max_county_dam_count', 25)


def calculate_dam_failure_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    dam_data = _get_county_dam_data(county_name)
    svi = _get_all_svi_themes(county_name)
    census = _get_census_demographics(county_name)
    health_factor = get_health_impact_factor(county_name, 'dam_failure')

    max_dams = _get_statewide_max_dams(county_name)

    dam_density = min(1.0, dam_data['total_dams'] / max_dams)

    high_hazard_ratio = dam_data['high_hazard'] / max(1, dam_data['total_dams'])
    significant_hazard_ratio = dam_data['significant_hazard'] / max(1, dam_data['total_dams'])
    hazard_severity = min(1.0, (high_hazard_ratio * 0.7) + (significant_hazard_ratio * 0.3))

    flood_zone_overlap = dam_data.get('flood_zone_overlap', 0.15)

    exposure_factors = {
        'dam_density': dam_density,
        'hazard_classification': hazard_severity,
        'flood_zone_overlap': flood_zone_overlap
    }

    exposure_score = min(1.0, (
        (dam_density * 0.35) +
        (hazard_severity * 0.40) +
        (flood_zone_overlap * 0.25)
    ))

    downstream_result = _compute_downstream_population_exposure(county_name, census, dam_data)
    downstream_pop_exposure = downstream_result['pct_exposed']

    if discipline == 'em':
        infrastructure_density = census['pop_density_factor']
        rural_isolation = max(0.0, min(1.0, 1.0 - census['pop_density_factor']))
        vulnerability_score = min(1.0, (
            (downstream_pop_exposure * 0.35) +
            (svi['housing_transportation'] * 0.20) +
            (svi['socioeconomic'] * 0.10) +
            (infrastructure_density * 0.15) +
            (rural_isolation * 0.10) +
            (census['elderly_factor'] * 0.10)
        ))

        # EM dam-failure resilience: inverse SVI plus a real per-dam credit
        # for Emergency Action Plans (NID 'has_eap' field).  The former
        # EOC_COUNTIES +0.20 bonus and the +0.10 population-threshold bonus
        # were removed because they created cliffs between adjacent counties
        # and were not backed by a cited capacity dataset (matches the
        # natural-hazards resilience cleanup).
        resilience_raw = 0.45
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.10)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.15)
        if dam_data.get('has_eap', False):
            resilience_raw += 0.10
        resilience_raw = max(0.1, min(0.9, resilience_raw))
    else:
        vulnerability_score = min(1.0, (
            (downstream_pop_exposure * 0.30) +
            (svi['socioeconomic'] * 0.20) +
            (svi['household_composition'] * 0.15) +
            (svi['housing_transportation'] * 0.15) +
            (census['elderly_factor'] * 0.10) +
            (svi['minority_status'] * 0.10)
        ))

        # PH dam-failure resilience: inverse SVI plus a real per-dam credit
        # for Emergency Action Plans (NID 'has_eap' field).  The former
        # prepared_counties +0.15 / +0.10 bonuses were removed because they
        # created cliffs between adjacent counties and were not backed by a
        # cited capacity dataset (matches the natural-hazards resilience
        # cleanup).
        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.15)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.10)

        if dam_data.get('has_eap', False):
            resilience_raw += 0.15

        resilience_raw = max(0.1, min(0.9, resilience_raw))

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    data_source_label = dam_data.get('data_source', 'unknown')
    using_real_nid = data_source_label == 'NID'

    metrics = {
        'total_dams': dam_data['total_dams'],
        'high_hazard_dams': dam_data['high_hazard'],
        'significant_hazard_dams': dam_data['significant_hazard'],
        'low_hazard_dams': dam_data['low_hazard'],
        'has_emergency_action_plan': dam_data.get('has_eap', False),
        'flood_zone_overlap_pct': round(flood_zone_overlap * 100, 1),
        'downstream_population_exposure': round(downstream_pop_exposure, 2),
        'estimated_pct_population_exposed': round(downstream_pop_exposure * 100, 1),
        'elderly_vulnerability_pct': round(census['elderly_pct'], 1),
        'has_real_data': using_real_nid,
        'dam_data_source': data_source_label,
        # H8: modeled-PAR provenance. See module-level comment block in
        # utils/dam_failure_risk.py for the data-availability rationale
        # and published references behind each constant.
        'downstream_exposure_method': downstream_result.get('method', 'unknown'),
        'modeled_population_at_risk': downstream_result.get('estimated_par', 0),
        'par_storage_scale_factor': downstream_result.get('storage_factor', 1.0),
        'par_height_scale_factor': downstream_result.get('height_factor', 1.0),
        'methodology_caveat': (
            'Downstream population at risk is a MODELED estimate, not a '
            'geometric inundation intersect. Per-dam population-at-risk '
            'and inundation polygons were removed from the public NID '
            'dataset (33 CFR 222.6, 2002) and live in a credentialed '
            'database accessible only to USACE / dam owners / state EM '
            'agencies. The estimate above uses published empirical PAR '
            'medians by hazard class (Brown & Graham 1988; Graham 1999, '
            'USBR DSO-99-06; USACE/RMC 2018) scaled by average per-dam '
            'storage and a max-dam-height proxy per Wahl 2004 / '
            'Froehlich 1995 breach regressions. Modeled-PAR count is '
            'unclamped; the exposed-percent figure is floored at 2.0% '
            'to reflect residual exposure that the public-data inputs '
            'cannot resolve. Pending a credentialed NID account or '
            'per-dam EAP submissions, this is the most rigorous '
            'estimate that the public-data path supports.'
        ),
    }

    if using_real_nid:
        metrics['total_storage_acre_ft'] = dam_data.get('total_storage_acre_ft', 0)
        metrics['max_dam_height_ft'] = dam_data.get('max_dam_height_ft', 0)
        metrics['eap_count'] = dam_data.get('eap_count', 0)

    data_sources = [
        'WI DNR Dam Safety Database (primary, ~4,100 active dams, weekly cache)',
        'USACE National Inventory of Dams (fallback)',
        'OpenFEMA NFIP Claims - Flood Zone Overlap Proxy',
        'CDC Social Vulnerability Index (SVI) - All 4 Themes',
        'U.S. Census Bureau ACS - Demographics',
        'Wisconsin Emergency Management - Dam Emergency Action Plans',
        'Brown & Graham (1988) / Graham (1999, USBR DSO-99-06) / USACE-RMC (2018) - empirical PAR medians by hazard class',
        'Wahl (2004) / Froehlich (1995) - breach-outflow scaling with storage and dam height'
    ]

    if not using_real_nid:
        data_sources[0] = f'Dam data (static baseline, source: {data_source_label})'

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'downstream_population_exposure': downstream_pop_exposure,
            'housing_transportation_svi': svi['housing_transportation'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status'],
            'elderly_factor': census['elderly_factor']
        },
        'metrics': metrics,
        'data_sources': data_sources
    }
