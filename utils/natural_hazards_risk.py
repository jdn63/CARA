import json
import logging
import os
import time
from typing import Dict, Any, Optional, Tuple

from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_climate_projections_cache = None
_thunderstorm_severity_cache = None
_real_data_cache = {}

# Bulk-loaded cross-county rate caches.  Populated on first lookup; each entry
# maps county_name -> events-per-year (NOAA) or claims-per-year (NFIP).
# Used by the percentile-normalization helpers below so that raw NOAA/NFIP
# counts contribute to exposure scores on a comparable 0-1 scale across the
# 72 Wisconsin counties.  Without normalization, large urban counties would
# dominate every hazard simply because more events occur in larger areas.
# Time-stamped cross-county rate caches.  Each entry is (built_at_epoch, data)
# so the caches can self-expire after _RATE_CACHE_TTL_SECONDS instead of
# locking in process-lifetime stale data.  In particular, an empty NFIP cache
# (when the underlying OpenFEMA cache has not yet been populated by the
# scheduler) must not persist forever — once the scheduler refresh lands,
# the next request after TTL expiry will rebuild and pick up the new data.
_RATE_CACHE_TTL_SECONDS = 3600  # 1 hour
_storm_rate_cache: Dict[str, Tuple[float, Dict[str, float]]] = {}
_nfip_rate_cache: Optional[Tuple[float, Dict[str, float]]] = None


def reset_rate_caches() -> None:
    """Clear cross-county NOAA/NFIP rate caches.  Call after the scheduler
    refreshes underlying noaa_storm_events or openfema caches so dashboards
    pick up the new data immediately rather than waiting out the TTL."""
    global _nfip_rate_cache
    _storm_rate_cache.clear()
    _nfip_rate_cache = None
    logger.info("Natural-hazards cross-county rate caches reset")

# Wisconsin county list (72 counties).  Mirrors WI_COUNTY_FIPS_3DIGIT in
# utils/openfema_data.py.  Kept local to avoid a circular import.
_WI_COUNTIES = (
    'Adams', 'Ashland', 'Barron', 'Bayfield', 'Brown', 'Buffalo', 'Burnett',
    'Calumet', 'Chippewa', 'Clark', 'Columbia', 'Crawford', 'Dane', 'Dodge',
    'Door', 'Douglas', 'Dunn', 'Eau Claire', 'Florence', 'Fond du Lac',
    'Forest', 'Grant', 'Green', 'Green Lake', 'Iowa', 'Iron', 'Jackson',
    'Jefferson', 'Juneau', 'Kenosha', 'Kewaunee', 'La Crosse', 'Lafayette',
    'Langlade', 'Lincoln', 'Manitowoc', 'Marathon', 'Marinette', 'Marquette',
    'Menominee', 'Milwaukee', 'Monroe', 'Oconto', 'Oneida', 'Outagamie',
    'Ozaukee', 'Pepin', 'Pierce', 'Polk', 'Portage', 'Price', 'Racine',
    'Richland', 'Rock', 'Rusk', 'Sauk', 'Sawyer', 'Shawano', 'Sheboygan',
    'St. Croix', 'Taylor', 'Trempealeau', 'Vernon', 'Vilas', 'Walworth',
    'Washburn', 'Washington', 'Waukesha', 'Waupaca', 'Waushara', 'Winnebago',
    'Wood'
)


def _parse_years_covered(years_str: Any) -> int:
    """Convert a 'YYYY-YYYY' window string into an inclusive year count.
    Falls back to a 20-year default if parsing fails."""
    try:
        if isinstance(years_str, str) and '-' in years_str:
            start, end = years_str.split('-', 1)
            n = int(end) - int(start) + 1
            if n > 0:
                return n
    except (ValueError, AttributeError):
        pass
    return 20


def _build_storm_rate_cache(category: str) -> Dict[str, float]:
    """Build a {county -> events-per-year} map for one hazard category by
    iterating all 72 Wisconsin counties.  Cached for _RATE_CACHE_TTL_SECONDS.
    The per-county lookup hits an in-process dict in noaa_storm_events, so
    this is cheap once warm.

    Always returns an entry for every county in _WI_COUNTIES (0.0 when no
    NOAA data is available for that county) so the percentile denominator
    below is the full statewide distribution."""
    entry = _storm_rate_cache.get(category)
    if entry is not None:
        built_at, cached = entry
        if (time.time() - built_at) < _RATE_CACHE_TTL_SECONDS:
            return cached

    rates: Dict[str, float] = {county: 0.0 for county in _WI_COUNTIES}
    try:
        from utils.noaa_storm_events import get_county_storm_summary
    except Exception as e:
        logger.warning(f"NOAA storm events module unavailable: {e}")
        _storm_rate_cache[category] = (time.time(), {})
        return {}

    any_data_found = False
    for county in _WI_COUNTIES:
        summary = get_county_storm_summary(county)
        if not summary:
            continue
        any_data_found = True
        years = _parse_years_covered(summary.get('years_covered'))
        cat = summary.get('by_category', {}).get(category, {})
        count = cat.get('event_count', 0) or 0
        rates[county] = count / max(1, years)

    # If we found no summaries for any county, the underlying NOAA cache is
    # unavailable — return {} so callers can drop the storm term and
    # renormalize instead of zero-imputing every county.
    final = rates if any_data_found else {}
    _storm_rate_cache[category] = (time.time(), final)
    if final:
        nonzero = sum(1 for v in final.values() if v > 0)
        logger.info(
            f"Built storm-rate cache for '{category}': "
            f"{nonzero}/{len(final)} counties have non-zero events"
        )
    return final


def _get_storm_rate_percentile(county_name: str, category: str) -> Optional[float]:
    """Return the percentile rank (0-1) of this county's events-per-year for
    the given NOAA category, relative to all 72 Wisconsin counties.

    Returns None only when the cross-county data is truly UNAVAILABLE
    (NOAA cache not populated for any county), so callers can drop the
    term and renormalize remaining weights.

    Returns 0.0 when the data is available but the entire state shows zero
    events in this category (a true low-signal floor, not missing data)
    or when this county is at the very bottom of the distribution.
    """
    rates = _build_storm_rate_cache(category)
    if not rates:  # No data available statewide -> caller drops term
        return None

    my_rate = rates.get(county_name, 0.0)
    if my_rate <= 0:
        # County has zero events in window: true low-risk signal at the
        # bottom of the distribution, not missing data.
        return 0.0

    # Percentile rank against the full 72-county distribution (including
    # zeros) so that a county at the median of the event distribution
    # lands at 0.5 and big urban counties don't auto-saturate.
    values = list(rates.values())
    rank = sum(1 for v in values if v < my_rate)
    ties = sum(1 for v in values if v == my_rate)
    pct = (rank + 0.5 * ties) / len(values)
    return max(0.0, min(1.0, pct))


def _build_nfip_rate_cache() -> Dict[str, float]:
    """Build a {county -> NFIP-claims-per-year} map across all 72 counties.
    Cached for _RATE_CACHE_TTL_SECONDS so empty-cache states don't lock in.

    Always returns an entry for every county in _WI_COUNTIES (0.0 when that
    county has no NFIP claims) so the percentile denominator is the full
    statewide distribution.  Returns {} only if the OpenFEMA cache is
    completely unpopulated for every county."""
    global _nfip_rate_cache
    if _nfip_rate_cache is not None:
        built_at, cached = _nfip_rate_cache
        if (time.time() - built_at) < _RATE_CACHE_TTL_SECONDS:
            return cached

    rates: Dict[str, float] = {county: 0.0 for county in _WI_COUNTIES}
    try:
        from utils.openfema_data import get_county_openfema_summary
    except Exception as e:
        logger.warning(f"OpenFEMA module unavailable: {e}")
        _nfip_rate_cache = (time.time(), {})
        return {}

    # NFIP claims data goes back to program inception (1978).  Use a
    # conservative 30-year window to convert totals to a rate; the exact
    # window matters less than the cross-county ordering for percentile rank.
    NFIP_YEARS = 30
    any_data_found = False
    any_nonzero = False
    for county in _WI_COUNTIES:
        summary = get_county_openfema_summary(county)
        if summary is None:
            continue
        any_data_found = True
        nfip = summary.get('nfip_claims') or {}
        total = nfip.get('total_claims', 0) or 0
        if total > 0:
            rates[county] = total / NFIP_YEARS
            any_nonzero = True

    # If no county returned a summary at all, treat as unavailable so
    # callers drop the NFIP term and renormalize.
    final = rates if any_data_found else {}
    _nfip_rate_cache = (time.time(), final)
    if any_nonzero:
        logger.info(
            f"Built NFIP rate cache: "
            f"{sum(1 for v in final.values() if v > 0)} counties have claims"
        )
    elif any_data_found:
        logger.info(
            "NFIP rate cache built with all zeros (no claims data in cache "
            "yet); flood exposure will renormalize remaining weights"
        )
    else:
        logger.info(
            "NFIP rate cache empty (OpenFEMA cache unpopulated); flood "
            "exposure will renormalize remaining weights"
        )
    return final


def _get_nfip_rate_percentile(county_name: str) -> Optional[float]:
    """Return the percentile rank (0-1) of this county's NFIP claims-per-year
    against all 72 Wisconsin counties.

    Returns None when the cross-county cache is unavailable (OpenFEMA not
    populated at all) OR when no county has any claims yet — in both cases
    the NFIP signal carries no information and callers should drop the term
    and renormalize the remaining flood-exposure weights.

    Returns 0.0 only when the cache contains real claim data for some
    counties but this specific county has zero claims (true low signal).
    """
    rates = _build_nfip_rate_cache()
    if not rates:
        return None

    # If the statewide distribution is all zeros, NFIP has no discriminating
    # signal yet — treat as missing rather than slamming every county to 0.
    if not any(v > 0 for v in rates.values()):
        return None

    my_rate = rates.get(county_name, 0.0)
    if my_rate <= 0:
        return 0.0

    values = list(rates.values())
    rank = sum(1 for v in values if v < my_rate)
    ties = sum(1 for v in values if v == my_rate)
    pct = (rank + 0.5 * ties) / len(values)
    return max(0.0, min(1.0, pct))


def _weighted_exposure_with_optional(
    components: Dict[str, float],
    weights: Dict[str, float],
    additive_boost: float = 0.0,
) -> float:
    """Combine 0-1 exposure components with their target weights.

    Components whose value is None are treated as missing data: their weight
    is removed and the remaining weights are renormalized pro-rata so they
    still sum to the original total.  This prevents missing data sources
    (e.g. an empty NFIP cache) from silently dragging exposure scores down.

    additive_boost is added after the weighted sum and clamped to [0,1].  Used
    by flood exposure for the urban-stormwater factor, which the methodology
    documents as an additive correction for impervious-surface-driven
    flooding that FEMA NRI systematically underestimates.
    """
    present = {k: v for k, v in components.items() if v is not None and k in weights}
    if not present:
        return min(1.0, max(0.0, additive_boost))

    target_total = sum(weights[k] for k in components if k in weights)
    present_total = sum(weights[k] for k in present)
    if present_total <= 0:
        return min(1.0, max(0.0, additive_boost))
    scale = target_total / present_total

    score = sum(present[k] * weights[k] * scale for k in present)
    return max(0.0, min(1.0, score + additive_boost))

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

NORTHERN_TREE_COUNTIES = ['Bayfield', 'Ashland', 'Iron', 'Vilas', 'Forest',
                          'Florence', 'Marinette', 'Oconto', 'Langlade']


def _calculate_em_resilience(svi: Dict[str, float], census: Dict[str, float],
                             county_name: str) -> float:
    # Resilience is derived purely from inverse SVI socioeconomic and housing
    # scores, matching the published methodology.  Hard-coded county lists
    # (formerly EOC_COUNTIES and a population-threshold bonus) were removed
    # because they created abrupt cliffs between adjacent counties and were
    # not backed by a cited dataset.  If a continuous capacity index (e.g.
    # WI WEM staffing FTE per capita, hospital beds per capita) becomes
    # available, reintroduce it here as a smooth term, not a list lookup.
    resilience_raw = 0.45
    resilience_raw += ((1.0 - svi['socioeconomic']) * 0.10)
    resilience_raw += ((1.0 - svi['housing_transportation']) * 0.15)
    return max(0.1, min(0.9, resilience_raw))


def _resolve_tribal_county(county_name: str) -> str:
    for tribal_name, mapped in TRIBAL_COUNTY_MAPPING.items():
        if tribal_name in county_name:
            logger.info(f"Using {mapped} County data for {county_name}")
            return mapped
    return county_name


def _is_tribal(county_name: str) -> bool:
    return any(t in county_name for t in TRIBAL_KEYWORDS)


def load_climate_projections() -> Dict[str, Any]:
    global _climate_projections_cache
    if _climate_projections_cache is not None:
        return _climate_projections_cache

    try:
        path = 'data/climate/natural_hazard_climate_projections.json'
        if os.path.exists(path):
            with open(path) as f:
                _climate_projections_cache = json.load(f)
            logger.info("Loaded climate projections for natural hazards")
            return _climate_projections_cache
    except Exception as e:
        logger.warning(f"Error loading climate projections: {e}")

    _climate_projections_cache = {}
    return _climate_projections_cache


def get_climate_zone(county_name: str) -> str:
    projections = load_climate_projections()
    zones = projections.get('county_climate_zones', {})
    for zone, counties in zones.items():
        if county_name in counties:
            return zone
    return 'central_wisconsin'


def get_climate_multiplier(county_name: str, hazard_type: str) -> float:
    projections = load_climate_projections()
    hazard_data = projections.get(hazard_type, {})

    base_multiplier = hazard_data.get('exposure_multiplier', 1.0)
    regional = hazard_data.get('regional_variation', {})
    zone = get_climate_zone(county_name)
    regional_multiplier = regional.get(zone, base_multiplier)

    return regional_multiplier


def get_thunderstorm_severity(county_name: str) -> float:
    global _thunderstorm_severity_cache
    if _thunderstorm_severity_cache is None:
        projections = load_climate_projections()
        ts_data = projections.get('wisconsin_thunderstorm_severity', {})
        _thunderstorm_severity_cache = ts_data.get('counties', {})
    return _thunderstorm_severity_cache.get(county_name, 0.40)


def get_all_svi_themes(county_name: str) -> Dict[str, float]:
    svi_data = get_svi_data(county_name)
    return {
        'overall': svi_data.get('overall', 0.5),
        'socioeconomic': svi_data.get('socioeconomic', 0.5),
        'household_composition': svi_data.get('household_composition', 0.5),
        'minority_status': svi_data.get('minority_status', 0.5),
        'housing_transportation': svi_data.get('housing_transportation', 0.5)
    }


def _get_real_storm_data(county_name: str) -> Optional[Dict[str, Any]]:
    cache_key = f"storm_{county_name}"
    if cache_key in _real_data_cache:
        return _real_data_cache[cache_key]
    try:
        from utils.noaa_storm_events import get_county_storm_summary
        data = get_county_storm_summary(county_name)
        _real_data_cache[cache_key] = data
        return data
    except Exception as e:
        logger.debug(f"NOAA storm data not available for {county_name}: {e}")
        _real_data_cache[cache_key] = None
        return None


def _get_real_openfema_data(county_name: str) -> Dict[str, Any]:
    cache_key = f"fema_{county_name}"
    if cache_key in _real_data_cache:
        return _real_data_cache[cache_key]
    try:
        from utils.openfema_data import get_county_openfema_summary
        data = get_county_openfema_summary(county_name)
        _real_data_cache[cache_key] = data
        return data
    except Exception as e:
        logger.debug(f"OpenFEMA data not available for {county_name}: {e}")
        data = {"disaster_declarations": None, "nfip_claims": None, "hma_projects": None}
        _real_data_cache[cache_key] = data
        return data


def _format_damage(amount: float) -> str:
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    elif amount > 0:
        return f"${amount:.0f}"
    return "$0"


def get_census_demographics(county_name: str) -> Dict[str, float]:
    try:
        from utils.census_data_loader import wisconsin_census
        elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name) or 18.7
        mobile_home_pct = wisconsin_census.get_mobile_home_percentage(county_name) or 5.2
        population = wisconsin_census.get_county_population(county_name) or 80000
    except Exception as e:
        logger.warning(f"Census data loading failed for {county_name}: {e}")
        elderly_pct = 18.7
        mobile_home_pct = 5.2
        population = 80000

    elderly_factor = min(1.0, max(0.05, (elderly_pct - 10.0) / 25.0))
    mobile_home_factor = min(1.0, mobile_home_pct / 20.0)
    pop_density_factor = min(1.0, population / 300000.0)

    return {
        'elderly_pct': elderly_pct,
        'elderly_factor': elderly_factor,
        'mobile_home_pct': mobile_home_pct,
        'mobile_home_factor': mobile_home_factor,
        'population': population,
        'pop_density_factor': pop_density_factor
    }


def calculate_enhanced_flood_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    from utils.data_processor import load_nri_data
    county_risk = load_nri_data().get(county_name, {'flood_risk': 0.3})
    base_flood_risk = county_risk.get('flood_risk', 0.3)

    svi = get_all_svi_themes(county_name)
    census = get_census_demographics(county_name)
    climate_mult = get_climate_multiplier(county_name, 'flood')
    health_factor = get_health_impact_factor(county_name, 'flood')

    river_counties = ['Buffalo', 'Crawford', 'Grant', 'La Crosse', 'Pepin', 'Pierce',
                      'Trempealeau', 'Vernon', 'Richland', 'Sauk', 'Columbia', 'Dodge',
                      'Jefferson', 'Waukesha', 'Milwaukee', 'Racine', 'Kenosha']
    lake_counties = ['Bayfield', 'Douglas', 'Ashland', 'Iron', 'Vilas', 'Florence',
                     'Marinette', 'Oconto', 'Brown', 'Kewaunee', 'Door', 'Manitowoc',
                     'Sheboygan', 'Ozaukee', 'Milwaukee', 'Racine', 'Kenosha']
    flat_terrain_counties = ['Columbia', 'Dodge', 'Fond du Lac', 'Green Lake', 'Marquette',
                             'Winnebago', 'Calumet', 'Outagamie', 'Brown']
    high_precip_counties = ['Bayfield', 'Douglas', 'Ashland', 'Iron', 'Vilas', 'Florence']
    # Urban counties with high impervious surface coverage — primary flood mechanism is
    # stormwater runoff and sewer surcharge, which FEMA NRI systematically underestimates
    # because NRI is calibrated on riverine/coastal flooding, not urban runoff.
    urban_stormwater_counties = ['Milwaukee', 'Racine', 'Kenosha', 'Waukesha',
                                 'Ozaukee', 'Washington']

    # Each component is on a native 0-1 scale.  Weights are applied exactly
    # once in _weighted_exposure_with_optional below, so there is no hidden
    # pre-scaling.  Components set to None are dropped and remaining weights
    # renormalize (used when NFIP cross-county data is unavailable).
    storm_pct = _get_storm_rate_percentile(county_name, 'flood')
    nfip_pct = _get_nfip_rate_percentile(county_name)

    exposure_factors = {
        'historical_nri': base_flood_risk,
        'noaa_storm_events': storm_pct if storm_pct is not None else 0.0,
        'nfip_claims': nfip_pct if nfip_pct is not None else 0.0,
        'proximity_to_water': 0.0,
        'terrain_risk': 0.15,
        'precipitation_patterns': 0.15,
        'urban_stormwater': 0.0,
        'climate_trend': min(1.0, base_flood_risk * climate_mult) - base_flood_risk
    }

    if county_name in river_counties:
        exposure_factors['proximity_to_water'] += 0.3
    if county_name in lake_counties:
        exposure_factors['proximity_to_water'] += 0.2
    if county_name in flat_terrain_counties:
        exposure_factors['terrain_risk'] = 0.25
    if county_name in high_precip_counties:
        exposure_factors['precipitation_patterns'] = 0.25
    # Urban impervious surface boost: dense urban counties flood frequently via
    # stormwater runoff, basement backups, and combined sewer overflows —
    # mechanisms not captured by NRI riverine flood indices.  Applied as an
    # ADDITIVE boost (capped at +0.10) rather than a weighted component, so the
    # urban-stormwater correction actually moves the final score instead of
    # being diluted by a small sub-weight.
    if county_name in urban_stormwater_counties:
        exposure_factors['urban_stormwater'] = 0.25
    urban_boost = 0.10 if county_name in urban_stormwater_counties else 0.0

    # Documented weights.  NFIP is dropped and weights renormalized when the
    # OpenFEMA NFIP cache is empty so that "no data" does not silently push
    # every county's flood exposure downward.
    components_for_weighting = {
        'historical_nri': exposure_factors['historical_nri'],
        'noaa_storm_events': storm_pct,  # None if cross-county data missing
        'nfip_claims': nfip_pct,         # None if cross-county data missing
        'proximity_to_water': exposure_factors['proximity_to_water'],
        'terrain_risk': exposure_factors['terrain_risk'],
        'precipitation_patterns': exposure_factors['precipitation_patterns'],
        'climate_trend': exposure_factors['climate_trend'],
    }
    weights = {
        'historical_nri':         0.30,
        'noaa_storm_events':      0.20,
        'nfip_claims':            0.10,
        'proximity_to_water':     0.15,
        'terrain_risk':           0.05,
        'precipitation_patterns': 0.05,
        'climate_trend':          0.05,
    }
    exposure_score = _weighted_exposure_with_optional(
        components_for_weighting, weights, additive_boost=urban_boost
    )

    if discipline == 'em':
        infrastructure_density = census['pop_density_factor']
        rural_isolation = max(0.0, min(1.0, 1.0 - census['pop_density_factor']))
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.35) +
            (svi['socioeconomic'] * 0.10) +
            (svi['household_composition'] * 0.05) +
            (svi['minority_status'] * 0.05) +
            (infrastructure_density * 0.15) +
            (census['mobile_home_factor'] * 0.10) +
            (census['elderly_factor'] * 0.05) +
            (rural_isolation * 0.15)
        ))
        # Flood-specific EM resilience: pure inverse SVI, matching the
        # published methodology.  Population-threshold bonus removed for the
        # same reason as the other hard-coded resilience bonuses (creates
        # cliffs between adjacent counties, no cited data source).
        resilience_raw = 0.45
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.10)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.15)
        resilience_raw = max(0.1, min(0.9, resilience_raw))
    else:
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.30) +
            (svi['socioeconomic'] * 0.20) +
            (svi['household_composition'] * 0.15) +
            (svi['minority_status'] * 0.10) +
            (census['elderly_factor'] * 0.15) +
            (census['mobile_home_factor'] * 0.10)
        ))

        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.20)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.10)

        # Hard-coded stormwater-investment county list removed: it was author
        # judgment without a cited capital-investment dataset and created
        # cliffs between adjacent counties.  Resilience is now purely
        # inverse SVI as the methodology documentation states.
        resilience_raw = max(0.1, min(0.9, resilience_raw))

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    storm_data = _get_real_storm_data(county_name)
    openfema = _get_real_openfema_data(county_name)

    flood_storm = storm_data.get('by_category', {}).get('flood', {}) if storm_data else {}
    nfip_data = openfema.get('nfip_claims')
    decl_data = openfema.get('disaster_declarations')
    hma_data = openfema.get('hma_projects')

    flood_decl_count = 0
    if decl_data:
        for itype in ['Flood', 'Coastal', 'Severe Storm(s)']:
            flood_decl_count += decl_data.get('by_incident_type', {}).get(itype, 0)

    metrics = {
        'historical_flood_events': flood_storm.get('event_count') if flood_storm.get('event_count') else None,
        'flood_property_damage': _format_damage(flood_storm.get('property_damage', 0)) if flood_storm.get('property_damage') else None,
        'flood_injuries': flood_storm.get('injuries', 0) if flood_storm else None,
        'nfip_claims_total': nfip_data.get('total_claims') if nfip_data else None,
        'nfip_total_payout': _format_damage(nfip_data.get('total_payout', 0)) if nfip_data else None,
        'federal_flood_declarations': flood_decl_count if decl_data else None,
        'mitigation_projects': hma_data.get('total_projects') if hma_data else None,
        'mitigation_federal_funding': _format_damage(hma_data.get('total_federal_share', 0)) if hma_data else None,
        'climate_trend_impact': f"+{int((climate_mult - 1.0) * 100)}%",
        'elderly_vulnerability_pct': round(census['elderly_pct'], 1),
        'mobile_home_vulnerability_pct': round(census['mobile_home_pct'], 1),
        'data_period': storm_data.get('years_covered', 'N/A') if storm_data else None,
        'has_real_data': bool(flood_storm.get('event_count') or nfip_data or decl_data)
    }

    data_sources = [
        'FEMA National Risk Index (NRI) - Census Tract Level',
        'CDC Social Vulnerability Index (SVI) - All 4 Themes',
        'U.S. Census Bureau ACS - Housing & Demographics',
        'NOAA/WICCI Climate Projections (2030-2050)',
        'FEMA NRI Health Impact Factor',
        'NOAA NCEI Storm Events Database',
        'OpenFEMA NFIP Redacted Claims',
        'OpenFEMA Disaster Declarations Summaries'
    ]

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor,
            'climate_multiplier': climate_mult
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'housing_transportation_svi': svi['housing_transportation'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status'],
            'elderly_factor': census['elderly_factor'],
            'mobile_home_factor': census['mobile_home_factor']
        },
        'metrics': metrics,
        'data_sources': data_sources
    }


def calculate_enhanced_tornado_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    from utils.data_processor import load_nri_data
    county_risk = load_nri_data().get(county_name, {'tornado_risk': 0.3})
    base_tornado_risk = county_risk.get('tornado_risk', 0.3)

    svi = get_all_svi_themes(county_name)
    census = get_census_demographics(county_name)
    climate_mult = get_climate_multiplier(county_name, 'tornado')
    health_factor = get_health_impact_factor(county_name, 'tornado')

    tornado_alley_counties = ['Grant', 'Iowa', 'Lafayette', 'Green', 'Rock', 'Walworth',
                              'Jefferson', 'Waukesha', 'Dane', 'Columbia', 'Sauk']
    open_terrain_counties = ['Columbia', 'Dodge', 'Fond du Lac', 'Green Lake', 'Marquette',
                             'Winnebago', 'Calumet', 'Outagamie', 'Brown', 'Rock', 'Walworth']

    # Each component on its native 0-1 scale; weights applied once below.
    storm_pct = _get_storm_rate_percentile(county_name, 'tornado')

    exposure_factors = {
        'historical_nri': base_tornado_risk,
        'noaa_storm_events': storm_pct if storm_pct is not None else 0.0,
        'tornado_alley_proximity': 0.2,
        'terrain_factors': 0.1,
        'climate_trend': min(1.0, base_tornado_risk * climate_mult) - base_tornado_risk
    }

    if county_name in tornado_alley_counties:
        exposure_factors['tornado_alley_proximity'] = 0.4
    if county_name in open_terrain_counties:
        exposure_factors['terrain_factors'] = 0.3

    weights = {
        'historical_nri':          0.40,
        'noaa_storm_events':       0.25,
        'tornado_alley_proximity': 0.15,
        'terrain_factors':         0.10,
        'climate_trend':           0.10,
    }
    components_for_weighting = {
        'historical_nri': exposure_factors['historical_nri'],
        'noaa_storm_events': storm_pct,
        'tornado_alley_proximity': exposure_factors['tornado_alley_proximity'],
        'terrain_factors': exposure_factors['terrain_factors'],
        'climate_trend': exposure_factors['climate_trend'],
    }
    exposure_score = _weighted_exposure_with_optional(
        components_for_weighting, weights
    )

    if discipline == 'em':
        infrastructure_density = census['pop_density_factor']
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.30) +
            (svi['socioeconomic'] * 0.10) +
            (svi['household_composition'] * 0.05) +
            (svi['minority_status'] * 0.05) +
            (infrastructure_density * 0.15) +
            (census['mobile_home_factor'] * 0.25) +
            (census['elderly_factor'] * 0.05) +
            (census['pop_density_factor'] * 0.05)
        ))
        resilience_raw = _calculate_em_resilience(svi, census, county_name)
    else:
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.25) +
            (svi['socioeconomic'] * 0.15) +
            (svi['household_composition'] * 0.10) +
            (svi['minority_status'] * 0.10) +
            (census['mobile_home_factor'] * 0.25) +
            (census['elderly_factor'] * 0.10) +
            (census['pop_density_factor'] * 0.05)
        ))

        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.20)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.10)

        # Hard-coded tornado prepared_counties / urban_counties adjustments
        # removed: not backed by a cited dataset and produced abrupt cliffs.
        # Resilience is now purely inverse SVI per the published methodology.
        resilience_raw = max(0.1, min(0.9, resilience_raw))

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    storm_data = _get_real_storm_data(county_name)
    openfema = _get_real_openfema_data(county_name)

    tornado_storm = storm_data.get('by_category', {}).get('tornado', {}) if storm_data else {}
    decl_data = openfema.get('disaster_declarations')

    tornado_decl_count = 0
    if decl_data:
        tornado_decl_count = decl_data.get('by_incident_type', {}).get('Tornado', 0)

    tornado_mags = storm_data.get('tornado_magnitudes', []) if storm_data else []
    avg_ef = None
    if tornado_mags:
        ef_values = []
        for m in tornado_mags:
            m_clean = m.replace('EF', '').replace('F', '').strip()
            try:
                ef_values.append(int(m_clean))
            except (ValueError, TypeError):
                pass
        if ef_values:
            avg_ef = round(sum(ef_values) / len(ef_values), 1)

    metrics = {
        'historical_tornado_events': tornado_storm.get('event_count') if tornado_storm.get('event_count') else None,
        'average_ef_rating': avg_ef,
        'tornado_property_damage': _format_damage(tornado_storm.get('property_damage', 0)) if tornado_storm.get('property_damage') else None,
        'tornado_injuries': tornado_storm.get('injuries', 0) if tornado_storm else None,
        'tornado_fatalities': tornado_storm.get('fatalities', 0) if tornado_storm else None,
        'federal_tornado_declarations': tornado_decl_count if decl_data else None,
        'climate_trend_impact': f"+{int((climate_mult - 1.0) * 100)}%",
        'mobile_home_vulnerability_pct': round(census['mobile_home_pct'], 1),
        'data_period': storm_data.get('years_covered', 'N/A') if storm_data else None,
        'has_real_data': bool(tornado_storm.get('event_count') or decl_data)
    }

    data_sources = [
        'FEMA National Risk Index (NRI) - Census Tract Level',
        'CDC Social Vulnerability Index (SVI) - All 4 Themes',
        'U.S. Census Bureau ACS - Housing & Demographics',
        'NOAA/IPCC Climate Projections (2030-2050)',
        'FEMA NRI Health Impact Factor',
        'NOAA NCEI Storm Events Database',
        'OpenFEMA Disaster Declarations Summaries'
    ]

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor,
            'climate_multiplier': climate_mult
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'housing_transportation_svi': svi['housing_transportation'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status'],
            'mobile_home_factor': census['mobile_home_factor'],
            'elderly_factor': census['elderly_factor'],
            'pop_density_factor': census['pop_density_factor']
        },
        'metrics': metrics,
        'data_sources': data_sources
    }


def calculate_enhanced_winter_storm_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    from utils.data_processor import load_nri_data
    county_risk = load_nri_data().get(county_name, {'winter_storm_risk': 0.3})
    base_winter_risk = county_risk.get('winter_storm_risk', 0.3)

    svi = get_all_svi_themes(county_name)
    census = get_census_demographics(county_name)
    climate_mult = get_climate_multiplier(county_name, 'winter_storm')
    health_factor = get_health_impact_factor(county_name, 'winter_storm')

    northern_counties = ['Douglas', 'Bayfield', 'Ashland', 'Iron', 'Vilas', 'Forest',
                         'Florence', 'Marinette', 'Langlade', 'Lincoln', 'Sawyer',
                         'Price', 'Oneida', 'Taylor', 'Rusk', 'Barron', 'Washburn',
                         'Burnett', 'Polk', 'Chippewa']
    lake_effect_counties = ['Bayfield', 'Douglas', 'Ashland', 'Iron', 'Vilas', 'Florence',
                            'Kenosha', 'Racine', 'Milwaukee', 'Ozaukee', 'Sheboygan',
                            'Manitowoc', 'Kewaunee', 'Door', 'Brown', 'Oconto', 'Marinette']

    # Each component on its native 0-1 scale; weights applied once below.
    storm_pct = _get_storm_rate_percentile(county_name, 'winter')

    exposure_factors = {
        'historical_nri': base_winter_risk,
        'noaa_storm_events': storm_pct if storm_pct is not None else 0.0,
        'northern_location': 0.2,
        'lake_effect': 0.1,
        'climate_trend': 0.0
    }

    if county_name in northern_counties:
        exposure_factors['northern_location'] = 0.6
    elif county_name in ['Marathon', 'Clark', 'Eau Claire', 'Dunn', 'St. Croix']:
        exposure_factors['northern_location'] = 0.4

    if county_name in lake_effect_counties:
        exposure_factors['lake_effect'] = 0.5

    climate_ice_storm_boost = 0.0
    climate_data = load_climate_projections().get('winter_storm', {}).get('sub_factors', {})
    ice_storm_mult = climate_data.get('ice_storm_frequency', 1.0)
    climate_ice_storm_boost = max(0, (ice_storm_mult - 1.0) * 0.3)
    exposure_factors['climate_trend'] = min(0.15, (climate_mult - 1.0) * base_winter_risk + climate_ice_storm_boost)

    weights = {
        'historical_nri':    0.40,
        'noaa_storm_events': 0.15,
        'northern_location': 0.20,
        'lake_effect':       0.10,
        'climate_trend':     0.15,
    }
    components_for_weighting = {
        'historical_nri': exposure_factors['historical_nri'],
        'noaa_storm_events': storm_pct,
        'northern_location': exposure_factors['northern_location'],
        'lake_effect': exposure_factors['lake_effect'],
        'climate_trend': exposure_factors['climate_trend'],
    }
    exposure_score = _weighted_exposure_with_optional(
        components_for_weighting, weights
    )

    vulnerable_grid_counties = ['Bayfield', 'Ashland', 'Iron', 'Vilas', 'Forest',
                                'Florence', 'Sawyer', 'Price', 'Oneida', 'Lincoln']
    moderate_grid_counties = ['Washburn', 'Burnett', 'Polk', 'Barron', 'Rusk',
                              'Taylor', 'Langlade', 'Oconto', 'Marinette']
    rural_counties = ['Bayfield', 'Ashland', 'Iron', 'Vilas', 'Forest', 'Florence',
                      'Sawyer', 'Price', 'Burnett', 'Washburn', 'Polk', 'Rusk']

    power_grid_vuln = 0.3
    if county_name in vulnerable_grid_counties:
        power_grid_vuln = 0.7
    elif county_name in moderate_grid_counties:
        power_grid_vuln = 0.5

    rural_isolation = 0.3
    if county_name in rural_counties:
        rural_isolation = 0.7
    elif county_name in ['Barron', 'Taylor', 'Lincoln', 'Langlade', 'Oconto', 'Marinette',
                          'Shawano', 'Waupaca', 'Clark', 'Marathon']:
        rural_isolation = 0.5

    if discipline == 'em':
        em_power_grid_vuln = svi['housing_transportation']
        if county_name in rural_counties or county_name in moderate_grid_counties:
            em_power_grid_vuln = min(1.0, em_power_grid_vuln + 0.15)
        em_rural_isolation = max(0.0, min(1.0, 1.0 - census['pop_density_factor']))
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.25) +
            (svi['socioeconomic'] * 0.05) +
            (svi['household_composition'] * 0.05) +
            (svi['minority_status'] * 0.05) +
            (em_power_grid_vuln * 0.25) +
            (em_rural_isolation * 0.20) +
            (census['mobile_home_factor'] * 0.05) +
            (census['elderly_factor'] * 0.10)
        ))
        resilience_raw = _calculate_em_resilience(svi, census, county_name)
    else:
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.20) +
            (svi['socioeconomic'] * 0.10) +
            (svi['household_composition'] * 0.15) +
            (svi['minority_status'] * 0.05) +
            (census['elderly_factor'] * 0.20) +
            (census['mobile_home_factor'] * 0.05) +
            (power_grid_vuln * 0.15) +
            (rural_isolation * 0.10)
        ))

        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.15)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.10)

        # Hard-coded winter-storm prepared_counties / northern_counties
        # adjustments removed: not backed by a cited dataset and produced
        # cliffs between adjacent counties.  Resilience is now purely
        # inverse SVI per the published methodology.
        resilience_raw = max(0.1, min(0.9, resilience_raw))

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    storm_data = _get_real_storm_data(county_name)
    openfema = _get_real_openfema_data(county_name)

    winter_storm = storm_data.get('by_category', {}).get('winter', {}) if storm_data else {}
    decl_data = openfema.get('disaster_declarations')

    winter_decl_count = 0
    if decl_data:
        for itype in ['Snow', 'Ice Storm', 'Severe Ice Storm', 'Freezing']:
            winter_decl_count += decl_data.get('by_incident_type', {}).get(itype, 0)

    winter_event_breakdown = {}
    if winter_storm.get('event_types'):
        winter_event_breakdown = winter_storm['event_types']

    metrics = {
        'historical_winter_events': winter_storm.get('event_count') if winter_storm.get('event_count') else None,
        'winter_property_damage': _format_damage(winter_storm.get('property_damage', 0)) if winter_storm.get('property_damage') else None,
        'winter_injuries': winter_storm.get('injuries', 0) if winter_storm else None,
        'winter_fatalities': winter_storm.get('fatalities', 0) if winter_storm else None,
        'winter_event_breakdown': winter_event_breakdown if winter_event_breakdown else None,
        'federal_winter_declarations': winter_decl_count if decl_data else None,
        'climate_trend_impact': f"+{int((climate_mult - 1.0) * 100)}% intensity, +{int((ice_storm_mult - 1.0) * 100)}% ice storms",
        'elderly_vulnerability_pct': round(census['elderly_pct'], 1),
        'data_period': storm_data.get('years_covered', 'N/A') if storm_data else None,
        'has_real_data': bool(winter_storm.get('event_count') or decl_data)
    }

    data_sources = [
        'FEMA National Risk Index (NRI) - Census Tract Level',
        'CDC Social Vulnerability Index (SVI) - All 4 Themes',
        'U.S. Census Bureau ACS - Housing & Demographics',
        'NOAA/WICCI Climate Projections (2030-2050)',
        'FEMA NRI Health Impact Factor',
        'NOAA NCEI Storm Events Database'
    ]

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor,
            'climate_multiplier': climate_mult
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'housing_transportation_svi': svi['housing_transportation'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status'],
            'elderly_factor': census['elderly_factor'],
            'mobile_home_factor': census['mobile_home_factor'],
            'power_grid_vulnerability': power_grid_vuln,
            'rural_isolation': rural_isolation
        },
        'metrics': metrics,
        'data_sources': data_sources
    }


def calculate_enhanced_thunderstorm_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    thunderstorm_severity = get_thunderstorm_severity(county_name)

    svi = get_all_svi_themes(county_name)
    census = get_census_demographics(county_name)
    climate_mult = get_climate_multiplier(county_name, 'thunderstorm')
    health_factor = get_health_impact_factor(county_name, 'thunderstorm')

    high_thunderstorm_counties = ['Milwaukee', 'Waukesha', 'Washington', 'Ozaukee', 'Racine',
                                  'Kenosha', 'Walworth', 'Rock', 'Green', 'Lafayette', 'Grant']
    moderate_thunderstorm_counties = ['Iowa', 'Dane', 'Jefferson', 'Dodge', 'Columbia',
                                     'Sauk', 'Richland', 'Crawford', 'Vernon', 'La Crosse']

    lightning_density = 0.35
    heavy_rainfall_freq = 0.40
    if county_name in high_thunderstorm_counties:
        lightning_density = 0.70
        heavy_rainfall_freq = 0.65
    elif county_name in moderate_thunderstorm_counties:
        lightning_density = 0.50
        heavy_rainfall_freq = 0.55

    # Each component on its native 0-1 scale; weights applied once below.
    storm_pct = _get_storm_rate_percentile(county_name, 'thunderstorm')

    exposure_factors = {
        'noaa_severity_index': thunderstorm_severity,
        'noaa_storm_events': storm_pct if storm_pct is not None else 0.0,
        'lightning_density': lightning_density,
        'heavy_rainfall_frequency': heavy_rainfall_freq,
        'climate_trend': min(0.15, (climate_mult - 1.0) * thunderstorm_severity)
    }

    weights = {
        'noaa_severity_index':      0.30,
        'noaa_storm_events':        0.20,
        'lightning_density':        0.15,
        'heavy_rainfall_frequency': 0.15,
        'climate_trend':            0.20,
    }
    components_for_weighting = {
        'noaa_severity_index': exposure_factors['noaa_severity_index'],
        'noaa_storm_events': storm_pct,
        'lightning_density': exposure_factors['lightning_density'],
        'heavy_rainfall_frequency': exposure_factors['heavy_rainfall_frequency'],
        'climate_trend': exposure_factors['climate_trend'],
    }
    exposure_score = _weighted_exposure_with_optional(
        components_for_weighting, weights
    )

    flood_prone_counties = ['Milwaukee', 'Racine', 'Kenosha', 'Waukesha', 'Washington',
                            'Ozaukee', 'Crawford', 'Grant', 'Vernon', 'La Crosse']
    high_tree_counties = ['Bayfield', 'Douglas', 'Ashland', 'Iron', 'Vilas', 'Forest',
                          'Florence', 'Marinette', 'Oconto', 'Shawano', 'Menominee']
    moderate_tree_counties = ['Oneida', 'Lincoln', 'Langlade', 'Marathon', 'Waupaca',
                              'Outagamie', 'Sheboygan', 'Washington', 'Waukesha']

    flood_suscept = 0.4
    if county_name in flood_prone_counties:
        flood_suscept = 0.7
    tree_coverage = 0.4
    if county_name in high_tree_counties:
        tree_coverage = 0.8
    elif county_name in moderate_tree_counties:
        tree_coverage = 0.6

    if discipline == 'em':
        infrastructure_density = census['pop_density_factor']
        em_tree_coverage = 0.4 if county_name in NORTHERN_TREE_COUNTIES else 0.25
        em_flood_suscept = flood_suscept if flood_suscept != 0.4 else 0.3
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.30) +
            (svi['socioeconomic'] * 0.05) +
            (svi['household_composition'] * 0.05) +
            (svi['minority_status'] * 0.05) +
            (infrastructure_density * 0.15) +
            (em_tree_coverage * 0.15) +
            (em_flood_suscept * 0.15) +
            (census['mobile_home_factor'] * 0.10)
        ))
        resilience_raw = _calculate_em_resilience(svi, census, county_name)
    else:
        vulnerability_score = min(1.0, (
            (svi['housing_transportation'] * 0.25) +
            (svi['socioeconomic'] * 0.10) +
            (svi['household_composition'] * 0.10) +
            (svi['minority_status'] * 0.05) +
            (census['elderly_factor'] * 0.10) +
            (census['mobile_home_factor'] * 0.10) +
            (flood_suscept * 0.15) +
            (tree_coverage * 0.15)
        ))

        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.15)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.10)

        # Hard-coded thunderstorm high_/moderate_resilience_counties
        # adjustments removed: not backed by a cited dataset and produced
        # cliffs between adjacent counties.  Resilience is now purely
        # inverse SVI per the published methodology.
        resilience_raw = max(0.1, min(0.9, resilience_raw))

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    storm_data = _get_real_storm_data(county_name)

    ts_storm = storm_data.get('by_category', {}).get('thunderstorm', {}) if storm_data else {}

    ts_event_breakdown = {}
    if ts_storm.get('event_types'):
        ts_event_breakdown = ts_storm['event_types']

    metrics = {
        'historical_thunderstorm_events': ts_storm.get('event_count') if ts_storm.get('event_count') else None,
        'thunderstorm_property_damage': _format_damage(ts_storm.get('property_damage', 0)) if ts_storm.get('property_damage') else None,
        'thunderstorm_injuries': ts_storm.get('injuries', 0) if ts_storm else None,
        'thunderstorm_fatalities': ts_storm.get('fatalities', 0) if ts_storm else None,
        'thunderstorm_event_breakdown': ts_event_breakdown if ts_event_breakdown else None,
        'climate_trend_impact': f"+{int((climate_mult - 1.0) * 100)}%",
        'noaa_severity_index': round(thunderstorm_severity, 2),
        'data_period': storm_data.get('years_covered', 'N/A') if storm_data else None,
        'has_real_data': bool(ts_storm.get('event_count'))
    }

    data_sources = [
        'NOAA NCEI Storm Events Database',
        'CDC Social Vulnerability Index (SVI) - All 4 Themes',
        'U.S. Census Bureau ACS - Housing & Demographics',
        'NOAA/WICCI Climate Projections (2030-2050)',
        'FEMA NRI Health Impact Factor'
    ]

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor,
            'climate_multiplier': climate_mult
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'housing_transportation_svi': svi['housing_transportation'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status'],
            'elderly_factor': census['elderly_factor'],
            'mobile_home_factor': census['mobile_home_factor'],
            'flood_susceptibility': flood_suscept,
            'tree_coverage': tree_coverage
        },
        'metrics': metrics,
        'data_sources': data_sources
    }
