"""Shared regional aggregation core for WEM and HERC regional dashboards.

Both regional dashboards (WEM and HERC) roll up per-jurisdiction risk data
into a single regional view. Historically each aggregator only rolled up the
numeric domain scores and discarded the supporting detail (component boxes,
metric tables, score provenance, source freshness), so regional dashboards
showed empty popovers and, worse, fell back to hardcoded placeholder
component values in the templates. This module centralizes the
integrity-correct rollup so WEM and HERC stay consistent and the detail
blocks the per-jurisdiction templates expect are produced honestly.

Aggregation rules:

  - Component blocks (exposure / vulnerability / resilience / health_impact /
    climate_multiplier, all 0-1 ratios): two-stage county mean. Within each
    county we average the constituent jurisdictions (so a county with many
    local health departments does not over-weight the region), then we
    average across the unique counties. This matches how the regional domain
    scores themselves are produced.

  - Metric fields: classified per field.
      * Additive tallies (event counts, injuries, fatalities, declarations,
        claims, dam counts, breaches, facility counts) are SUMMED across
        counties. Within a county they are averaged first, because the same
        county-level NOAA/FEMA figure is repeated for every local health
        department in that county; averaging collapses the duplicates before
        the cross-county sum.
      * Currency strings such as "$1.2M" are parsed, summed across counties
        (averaged within a county), then reformatted. If any value cannot be
        parsed the field is reported as varying rather than guessed.
      * Percentages and other ratios / scores are averaged.
      * Booleans are reduced with any() (regional presence).
      * Narrative or label strings, breakdown dicts, and date ranges are kept
        only when every county agrees; otherwise they are replaced with a
        "Varies across N counties" note so a single-county value is never
        presented as a regional figure.

  - score_provenance: rebuilt as an honest LINEAR weighted sum of the
    aggregated domain scores. Regional totals are a linear weighted sum, not
    the PHRAT quadratic mean used per jurisdiction, and the trace says so.

  - data_quality.source_freshness: reconciled to the most conservative
    (stalest) entry per source across the region, since all jurisdictions
    share the same cached data sources.

Everything in this module is pure (no I/O, no Flask, no database) so it can
be unit-tested and reused by both aggregators.
"""

import logging
import math
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Leaf metric fields that are additive tallies and should be SUMMED across
# counties. Anything numeric not listed here defaults to a mean, which is the
# safe choice for ratios, scores, and percentages.
_SUM_FIELDS = {
    # Flood
    'historical_flood_events', 'historical_flood_claims',
    'federal_flood_declarations', 'nfip_claims_total', 'mitigation_projects',
    # Tornado
    'historical_tornado_events', 'tornado_injuries', 'tornado_fatalities',
    'federal_tornado_declarations',
    # Winter storm
    'historical_winter_events', 'winter_injuries', 'winter_fatalities',
    'federal_winter_declarations',
    # Thunderstorm
    'historical_thunderstorm_events', 'thunderstorm_injuries',
    'thunderstorm_fatalities',
    # Straight-line wind
    'historical_wind_events', 'wind_injuries', 'wind_fatalities',
    # Dam failure
    'total_dams', 'high_hazard_dams', 'significant_hazard_dams',
    'low_hazard_dams', 'eap_count', 'modeled_population_at_risk',
    # Cyber
    'reported_breaches', 'cybercrime_reports', 'critical_vulnerabilities',
    # Hazmat
    'tri_facility_count',
    # Heat / health
    'ed_visits', 'heat_advisories',
}

# Currency strings produced by the data layer always start with a dollar
# sign, optionally followed by a number and a K / M / B magnitude suffix.
_CURRENCY_RE = re.compile(
    r'^\s*\$\s*([0-9][0-9,]*\.?[0-9]*)\s*([KMB]?)\s*$', re.IGNORECASE
)
_CURRENCY_MULT = {'': 1.0, 'K': 1e3, 'M': 1e6, 'B': 1e9}


def parse_currency(value: Any) -> Optional[float]:
    """Parse a formatted currency string like "$1.2M" into a float.

    Returns None when the value is not a currency string this module
    recognizes, so callers can fall back rather than guess.
    """
    if not isinstance(value, str):
        return None
    match = _CURRENCY_RE.match(value)
    if not match:
        return None
    number = float(match.group(1).replace(',', ''))
    suffix = match.group(2).upper()
    return number * _CURRENCY_MULT[suffix]


def format_currency(amount: float) -> str:
    """Format a dollar amount to match the data layer's own style."""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    return f"${amount:.0f}"


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _is_available(value: Any) -> bool:
    """True only when a domain value is a real, finite number.

    Mirrors the per-jurisdiction ``_domain_available`` check in
    ``data_processor.py``: ``None``, ``NaN``, ``inf`` and non-numeric values
    mean the domain carries no data and must be excluded from the composite
    and from weight renormalization (never coerced to a fabricated 0.0).
    """
    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))


def _as_score(value: Any) -> float:
    """Coerce a domain/component value to a scalar score.

    Some aggregated domain values arrive as nested dicts (e.g. a block that
    carries an 'overall'/'composite'/'risk_score' alongside sub-fields).
    Extract the scalar so provenance math never crashes on a dict.
    """
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for candidate in (
            'overall', 'composite', 'composite_risk',
            'risk_score', 'score', 'value',
        ):
            inner = value.get(candidate)
            if isinstance(inner, (int, float)):
                return float(inner)
        logger.warning(
            "Regional provenance: dict value had no scalar score field; "
            "using 0.0. Keys: %s", list(value.keys())[:8]
        )
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _merge(values: List[Any], field_name: str, additive: bool) -> Any:
    """Recursively merge a list of like-typed values into one.

    additive=True allows summing of additive tallies and currency; it is set
    only for the across-county stage. Within a county we always average so
    duplicate health departments collapse instead of inflating totals.
    """
    values = [v for v in values if v is not None]
    if not values:
        return None

    # Nested dicts: merge key by key, preserving first-seen key order.
    if all(isinstance(v, dict) for v in values):
        ordered_keys: List[str] = []
        seen = set()
        for v in values:
            for k in v.keys():
                if k not in seen:
                    seen.add(k)
                    ordered_keys.append(k)
        merged: Dict[str, Any] = {}
        for k in ordered_keys:
            sub = [v.get(k) for v in values if k in v]
            merged[k] = _merge(sub, k, additive)
        return merged

    # Booleans must be checked before numbers (bool is an int subclass).
    if all(isinstance(v, bool) for v in values):
        return any(values)

    # Plain numbers.
    if all(isinstance(v, (int, float)) and not isinstance(v, bool)
           for v in values):
        if additive and field_name in _SUM_FIELDS:
            total = sum(values)
            if all(float(v).is_integer() for v in values):
                return int(round(total))
            return round(total, 4)
        result = _mean(values)
        if all(isinstance(v, int) for v in values) and result.is_integer():
            return int(result)
        return round(result, 4)

    # Currency strings.
    if all(isinstance(v, str) for v in values):
        parsed = [parse_currency(v) for v in values]
        if all(p is not None for p in parsed):
            amount = sum(parsed) if additive else _mean(parsed)
            return format_currency(amount)

    # Lists of scalars: union of unique items, preserving order.
    if all(isinstance(v, list) for v in values):
        out: List[Any] = []
        seen_items = set()
        for v in values:
            for item in v:
                key = item if isinstance(item, (str, int, float, bool)) else repr(item)
                if key not in seen_items:
                    seen_items.add(key)
                    out.append(item)
        return out

    # Other strings / mixed: keep the shared value, else flag the variance.
    first = values[0]
    if all(v == first for v in values):
        return first
    if additive:
        return f"Varies across {len(values)} counties"
    return "Varies by jurisdiction"


def _aggregate_block(per_county_values: Dict[str, List[Any]],
                     block_key: str) -> Optional[Any]:
    """Two-stage county aggregation of one named block.

    per_county_values maps a county key to the list of that block's value
    from each jurisdiction in the county.
    """
    county_reprs: List[Any] = []
    for _county, vals in per_county_values.items():
        vals = [v for v in vals if v is not None]
        if not vals:
            continue
        within = _merge(vals, block_key, additive=False)
        if within is not None:
            county_reprs.append(within)
    if not county_reprs:
        return None
    return _merge(county_reprs, block_key, additive=True)


def aggregate_detail_blocks(
    risk_by_county: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """Aggregate every per-jurisdiction detail block into regional blocks.

    Discovers any top-level key ending in "_components" or "_metrics" plus the
    nested "utilities" block, so it adapts to the data layer's key naming
    (for example cyber_components, vbd_metrics) without a hardcoded list.
    """
    block_keys = set()
    for jurs in risk_by_county.values():
        for rd in jurs:
            if not isinstance(rd, dict):
                continue
            for k, v in rd.items():
                if (k.endswith('_components') or k.endswith('_metrics')) \
                        and isinstance(v, dict):
                    block_keys.add(k)

    out: Dict[str, Any] = {}
    for key in sorted(block_keys):
        per_county = {
            county: [rd.get(key) for rd in jurs
                     if isinstance(rd, dict) and isinstance(rd.get(key), dict)]
            for county, jurs in risk_by_county.items()
        }
        agg = _aggregate_block(per_county, key)
        if agg is not None:
            out[key] = agg

    # Utilities is a nested block (overall + components + sub-scores) and does
    # not match the _components / _metrics suffix.
    util_per_county = {
        county: [rd.get('utilities') for rd in jurs
                 if isinstance(rd, dict) and isinstance(rd.get('utilities'), dict)]
        for county, jurs in risk_by_county.items()
    }
    util_agg = _aggregate_block(util_per_county, 'utilities')
    if util_agg is not None:
        out['utilities'] = util_agg

    return out


# Display metadata for the regional provenance trace. Data-source lists are
# kept short; the per-jurisdiction dashboards carry the full citations.
_DOMAIN_META = {
    'natural_hazards': (
        'Natural Hazards',
        ['FEMA NRI', 'NOAA Storm Events', 'Census ACS', 'CDC SVI'],
    ),
    'health_metrics': (
        'Health Metrics',
        ['CDC NSSP', 'WI DHS WIR', 'County Health Rankings', 'CDC PLACES'],
    ),
    'active_shooter': (
        'Active Shooter',
        ['Gun Violence Archive', 'NCES SSOCS', 'Census ACS'],
    ),
    'extreme_heat': (
        'Extreme Heat',
        ['WI DHS Heat Vulnerability Index'],
    ),
    'air_quality': (
        'Air Quality',
        ['EPA AirNow', 'Census ACS', 'CDC SVI'],
    ),
    'cybersecurity': (
        'Cybersecurity',
        ['Census ACS', 'WI DOR', 'CDC SVI'],
    ),
    'dam_failure': (
        'Dam Failure',
        ['WI DNR Dam Safety', 'USACE NID', 'OpenFEMA NFIP', 'CDC SVI'],
    ),
    'vector_borne_disease': (
        'Vector-Borne Disease',
        ['WI DHS EPHT', 'USDA NLCD', 'WI DNR', 'WICCI/NOAA'],
    ),
    'infectious_disease': (
        'Infectious Disease',
        ['CDC NSSP', 'CDC NNDSS', 'WI DHS surveillance'],
    ),
    'hazmat_industrial': (
        'Hazmat (Industrial)',
        ['EPA TRI', 'EPA RMP', 'PHMSA', 'Census ACS'],
    ),
    'hazmat_agricultural': (
        'Hazmat (Agricultural)',
        ['WI DATCP', 'USDA Census of Agriculture', 'Census ACS'],
    ),
    'utilities': (
        'Utilities',
        ['Census ACS', 'CDC SVI', 'County characteristics'],
    ),
}

# Order domains appear in the provenance table.
_DOMAIN_ORDER = [
    'natural_hazards', 'health_metrics', 'active_shooter', 'extreme_heat',
    'air_quality', 'dam_failure', 'vector_borne_disease', 'infectious_disease',
    'hazmat_industrial', 'hazmat_agricultural', 'cybersecurity', 'utilities',
]

# Domains that are contextual and never part of the composite score in the
# Public Health discipline.
_SUPPLEMENTARY_KEYS = ('cybersecurity', 'utilities')

# Scalar utility sub-scores the data layer exposes at the top level of the
# nested "utilities" block (alongside "overall" and a "components" dict). These
# are the honest values to surface in the regional provenance trace.
UTILITIES_SUBKEYS = (
    'electrical_outage', 'utilities_disruption', 'supply_chain',
    'fuel_shortage',
)


def build_regional_provenance(
    domain_scores: Dict[str, float],
    *,
    weights: Dict[str, float],
    discipline_label: str,
    unique_counties_count: int,
    jurisdiction_count: int,
    nh_sub_components: Optional[Dict[str, float]] = None,
    utilities_sub_components: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Build an honest regional score_provenance trace (linear weighted sum)."""
    primary_keys = [
        k for k in _DOMAIN_ORDER
        if weights.get(k, 0.0) > 0
        and k in domain_scores
        and _is_available(domain_scores.get(k))
    ]

    aggregation_note = (
        f'Two-stage county mean across {unique_counties_count} counties '
        f'({jurisdiction_count} jurisdictions)'
    )

    domains: List[Dict[str, Any]] = []
    for key in primary_keys:
        name, sources = _DOMAIN_META.get(key, (key, []))
        weight = float(weights.get(key, 0.0))
        score = _as_score(domain_scores.get(key, 0.0))
        entry: Dict[str, Any] = {
            'name': name,
            'weight': round(weight, 4),
            'final_score': round(score, 4),
            'weighted_contribution': round(weight * score, 4),
            'svi_adjustment': 'Applied per jurisdiction before regional rollup',
            'data_sources': sources,
            'aggregation': aggregation_note,
        }
        if key == 'natural_hazards' and nh_sub_components:
            entry['sub_components'] = {
                k: round(_as_score(v), 4) for k, v in nh_sub_components.items()
            }
        if key == 'utilities' and utilities_sub_components:
            entry['sub_components'] = {
                k: round(_as_score(v), 4)
                for k, v in utilities_sub_components.items()
            }
        domains.append(entry)

    weighted_sum = sum(d['weighted_contribution'] for d in domains)
    weights_sum = sum(float(weights.get(k, 0.0)) for k in primary_keys)
    # Renormalize over the domains that actually carry data so the regional
    # total is a true weighted mean on the same 0-1 scale as the
    # per-jurisdiction composite, which also renormalizes its weights over the
    # surviving domain set. Without this, a region missing a primary domain
    # (for example hazmat, which is not rolled up at the HERC level) would be
    # silently deflated by the missing weight.
    total = (weighted_sum / weights_sum) if weights_sum > 0 else 0.0

    # Supplementary domains: contextual scores not in the composite.
    supplementary: List[Dict[str, Any]] = []
    for key in _SUPPLEMENTARY_KEYS:
        if key in primary_keys:
            continue
        if key not in domain_scores:
            continue
        if not _is_available(domain_scores.get(key)):
            continue
        name, sources = _DOMAIN_META.get(key, (key, []))
        sup_entry: Dict[str, Any] = {
            'name': name,
            'final_score': round(_as_score(domain_scores.get(key, 0.0)), 4),
            'svi_adjustment': 'Applied per jurisdiction before regional rollup',
            'data_sources': sources,
            'not_in_phrat': True,
        }
        if key == 'utilities' and utilities_sub_components:
            sup_entry['sub_components'] = {
                k: round(_as_score(v), 4)
                for k, v in utilities_sub_components.items()
            }
        supplementary.append(sup_entry)

    manual_check = (
        ' + '.join(
            f'{d["weight"]:.2f}×{d["final_score"]:.4f}' for d in domains
        ) + f' = {weighted_sum:.4f}; renormalized {weighted_sum:.4f} / '
        f'{weights_sum:.4f} = {total:.4f}'
        if domains else 'No domains contributed to the regional composite'
    )

    return {
        'method': 'linear_weighted_sum',
        'formula': (
            f'Regional weighted mean: Σ(weightᵢ × Domainᵢ) / Σ(weightᵢ) over '
            f'two-stage county-mean domain scores across '
            f'{unique_counties_count} counties ({jurisdiction_count} '
            f'jurisdictions). Weights are renormalized over the domains that '
            f'carry data. Regional totals use this linear weighted mean, not '
            f'the {discipline_label} quadratic mean (p=2) used per '
            f'jurisdiction.'
        ),
        'p': 1,
        'domains': domains,
        'supplementary_domains': supplementary,
        'weighted_sum': round(weighted_sum, 6),
        'total_risk_score': round(total, 4),
        'svi_themes_used': {},
        'region_scope': aggregation_note,
        'verification': {
            'weights_sum': round(weights_sum, 4),
            'manual_check': manual_check,
        },
    }


def _freshness_rank(entry: Any) -> tuple:
    """Rank a source-freshness entry so the stalest sorts highest."""
    if not isinstance(entry, dict):
        return (0, 0.0)
    stale = entry.get('stale')
    if stale is None:
        stale = entry.get('is_stale')
    if stale is None:
        stale = not entry.get('fresh', True)
    age = entry.get('age_days', 0)
    if not isinstance(age, (int, float)):
        age = 0
    return (1 if stale else 0, float(age))


def build_regional_data_quality(
    risk_by_county: Dict[str, List[Dict[str, Any]]],
    *,
    discipline_label: str,
    unique_counties_count: int,
    jurisdiction_count: int,
) -> Dict[str, Any]:
    """Build regional data_quality with the most conservative freshness."""
    merged_freshness: Dict[str, Any] = {}
    coverage: List[float] = []
    confidence: List[float] = []

    for jurs in risk_by_county.values():
        for rd in jurs:
            if not isinstance(rd, dict):
                continue
            dq = rd.get('data_quality') or {}
            cf = dq.get('coverage_fraction')
            if isinstance(cf, (int, float)):
                coverage.append(cf)
            cc = dq.get('composite_confidence')
            if isinstance(cc, (int, float)):
                confidence.append(cc)
            sf = dq.get('source_freshness')
            if isinstance(sf, dict):
                for source_id, entry in sf.items():
                    existing = merged_freshness.get(source_id)
                    if existing is None or \
                            _freshness_rank(entry) > _freshness_rank(existing):
                        merged_freshness[source_id] = entry

    scope = (
        f'{unique_counties_count} counties, {jurisdiction_count} jurisdictions'
    )
    return {
        'discipline': discipline_label,
        'coverage_fraction': round(_mean(coverage), 3) if coverage else None,
        'composite_confidence': (
            round(_mean(confidence), 3) if confidence else None
        ),
        'source_freshness': merged_freshness,
        'regional_scope': scope,
        'banner': (
            f'Regional aggregate across {scope}. Source freshness shows the '
            f'most conservative (stalest) value among constituent counties.'
        ),
    }
