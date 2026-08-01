"""Observed county climate trends from the baked NOAA nClimDiv snapshot.

Data file: data/climate/nclimdiv_county_climate_trends.json, built by
scripts/build_nclimdiv_snapshot.py from NOAA NCEI's Climate at a Glance
county time series (nClimDiv dataset).  These are MEASURED annual values
(precipitation, mean temperature) per county, compared across two
documented periods:

    baseline  1951-2000 mean (50 years)
    recent    2011-2025 mean (15 years)

This module replaced the static per-zone climate projection multipliers
retired in August 2026.  Those multipliers applied one literature-derived
constant to every county in a three-zone map, which created score
differences that no local measurement supported.  Observed nClimDiv
trends differentiate counties with real data: for example, Dane County's
annual precipitation is up about 14 percent over its 1951-2000 baseline
while Bayfield County's is up under 2 percent.

Availability semantics (house convention):
- Functions return None when the snapshot is missing or the county is
  absent.  Callers must drop the term and renormalize remaining weights
  (never coerce to 0.0, which would fabricate a "no trend" claim).
"""
import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_SNAPSHOT_PATH = os.path.join('data', 'climate', 'nclimdiv_county_climate_trends.json')
_snapshot_cache: Optional[Dict[str, Any]] = None
_snapshot_loaded = False


def load_climate_trends() -> Dict[str, Any]:
    """Load the baked snapshot once per process.  Returns {} when missing
    so callers fall through to their documented None/neutral paths."""
    global _snapshot_cache, _snapshot_loaded
    if _snapshot_loaded:
        return _snapshot_cache or {}
    _snapshot_loaded = True
    try:
        if os.path.exists(_SNAPSHOT_PATH):
            with open(_SNAPSHOT_PATH) as f:
                _snapshot_cache = json.load(f)
            n = len(_snapshot_cache.get('counties', {}))
            logger.info(f"Loaded nClimDiv county climate trends ({n} counties)")
            return _snapshot_cache
        logger.warning(
            f"nClimDiv snapshot not found at {_SNAPSHOT_PATH}; observed "
            "climate-trend terms will be dropped (weights renormalize)"
        )
    except Exception as e:
        logger.warning(f"Error loading nClimDiv snapshot: {e}")
    _snapshot_cache = {}
    return {}


def _county_entry(county_name: str, variable: str) -> Optional[Dict[str, Any]]:
    snapshot = load_climate_trends()
    entry = snapshot.get('counties', {}).get(county_name, {}).get(variable)
    if not entry or entry.get('ratio') is None:
        return None
    return entry


def get_precip_trend_info(county_name: str) -> Optional[Dict[str, Any]]:
    """Observed precipitation trend detail for one county, or None.

    Keys: ratio, pct_change, baseline_mean, recent_mean (inches),
    baseline_period, recent_period.
    """
    entry = _county_entry(county_name, 'pcp')
    if entry is None:
        return None
    meta = load_climate_trends().get('metadata', {})
    return {
        'ratio': entry['ratio'],
        'pct_change': entry.get('pct_change'),
        'baseline_mean': entry.get('baseline_mean'),
        'recent_mean': entry.get('recent_mean'),
        'baseline_period': meta.get('baseline_period', '1951-2000'),
        'recent_period': meta.get('recent_period', '2011-2025'),
    }


def get_precip_trend_percentile(county_name: str) -> Optional[float]:
    """Percentile rank (0-1) of this county's observed precipitation trend
    ratio against all Wisconsin counties in the snapshot.

    Same midrank convention as the NOAA storm-events percentiles: a county
    at the median observed trend lands at 0.5.  Returns None when the
    snapshot is unavailable or the county is missing, so callers drop the
    term and renormalize (never zero-impute).
    """
    snapshot = load_climate_trends()
    counties = snapshot.get('counties', {})
    if not counties:
        return None
    ratios = {
        name: data.get('pcp', {}).get('ratio')
        for name, data in counties.items()
    }
    ratios = {n: r for n, r in ratios.items() if r is not None}
    my_ratio = ratios.get(county_name)
    if my_ratio is None or len(ratios) < 10:
        return None
    values = list(ratios.values())
    rank = sum(1 for v in values if v < my_ratio)
    ties = sum(1 for v in values if v == my_ratio)
    pct = (rank + 0.5 * ties) / len(values)
    return max(0.0, min(1.0, pct))


def get_tavg_trend_info(county_name: str) -> Optional[Dict[str, Any]]:
    """Observed mean-temperature trend detail for one county, or None.

    Keys: delta_f (recent mean minus baseline mean, degrees F),
    baseline_mean, recent_mean, baseline_period, recent_period.
    """
    entry = _county_entry(county_name, 'tavg')
    if entry is None:
        return None
    baseline_mean = entry.get('baseline_mean')
    recent_mean = entry.get('recent_mean')
    if baseline_mean is None or recent_mean is None:
        return None
    meta = load_climate_trends().get('metadata', {})
    return {
        'delta_f': round(recent_mean - baseline_mean, 2),
        'baseline_mean': baseline_mean,
        'recent_mean': recent_mean,
        'baseline_period': meta.get('baseline_period', '1951-2000'),
        'recent_period': meta.get('recent_period', '2011-2025'),
    }
