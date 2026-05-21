"""Planning Projections Module - real-data extrapolation.

This module replaces the previous synthetic placeholder predictor. Forward
projections are now built from real cached trend signals computed by
utils.real_trend_calculator (NOAA Storm Events counts, OpenFEMA NFIP claims
and disaster declarations, EPA AirNow history, ACS demographic change, and
NOAA climate projections), so every projection is anchored in real data.

Outputs are clearly labeled as "model projections" rather than forecasts:
they extrapolate observed direction and magnitude from the historical record
and do not predict specific future events. Confidence bands widen each year
to reflect cumulative extrapolation uncertainty.

The public RiskPredictor interface is preserved so existing callers
(routes/dashboard.py and routes/api.py) keep working without changes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Map composite risk keys (returned to callers) to the trend signal names
# exposed by utils.real_trend_calculator.get_all_trend_scores().
_RISK_TO_TREND = {
    'natural_hazards_risk': ['flood', 'tornado', 'winter_storm', 'thunderstorm', 'straight_line_wind'],
    'health_risk': ['demographic'],
    'extreme_heat_risk': ['extreme_heat'],
    'air_quality_risk': ['air_quality'],
    'active_shooter_risk': ['demographic'],  # uses demographic trend as a proxy
    'total_risk': None,                      # synthesized from the others
}

# Per-year confidence band widening (additive). Year 1 = base; year 5 grows.
_BAND_BASE = 0.05
_BAND_PER_YEAR = 0.02
_PROJECTION_HORIZON_YEARS = 5


class RiskPredictor:
    """Generate real-data planning projections for a jurisdiction.

    Projections are linear extrapolations anchored to the current assessment
    score, with the slope determined by real cached trend signals. They are
    explicitly model projections, not statistical forecasts, and should be
    used only for strategic preparedness planning.
    """

    def __init__(self, historical_data: Optional[List[Dict[str, Any]]] = None):
        self.historical_data = historical_data or []

    def generate_predictions(
        self,
        jurisdiction_id: str,
        current_risk_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate 5-year projections for a single jurisdiction.

        Args:
            jurisdiction_id: ID of the jurisdiction (used for logging).
            current_risk_data: Current risk assessment dict; must contain
                county_name plus per-domain risk values.

        Returns:
            Dict with years, predictions, confidence_intervals, historical,
            trend_strength, and a methodology block describing the data
            sources used. If no real trend data is available the result is
            marked unavailable rather than synthesized.
        """
        county_name = (
            current_risk_data.get('county_name')
            or current_risk_data.get('county')
            or current_risk_data.get('jurisdiction_name')
            or ''
        )
        logger.info(
            "Generating real-data projections for jurisdiction %s (county=%s)",
            jurisdiction_id, county_name or 'unknown',
        )

        trend_scores = self._load_trend_scores(county_name)
        return self._build_projection_payload(
            current_risk_data=current_risk_data,
            trend_scores=trend_scores,
            band_base=_BAND_BASE,
            band_per_year=_BAND_PER_YEAR,
            scope_label=f'jurisdiction {jurisdiction_id}',
        )

    def generate_regional_predictions(
        self,
        region_id: str,
        current_risk_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate 5-year projections for a HERC or WEM region.

        Regional aggregates show less volatility than single counties because
        idiosyncratic county trends partially cancel out, so the confidence
        band widens more slowly.
        """
        county_name = (
            current_risk_data.get('representative_county')
            or current_risk_data.get('county_name')
            or current_risk_data.get('county')
            or ''
        )
        logger.info(
            "Generating real-data regional projections for region %s "
            "(representative county=%s)", region_id, county_name or 'unknown',
        )

        trend_scores = self._load_trend_scores(county_name)
        return self._build_projection_payload(
            current_risk_data=current_risk_data,
            trend_scores=trend_scores,
            band_base=max(0.0, _BAND_BASE - 0.02),
            band_per_year=max(0.0, _BAND_PER_YEAR - 0.01),
            scope_label=f'region {region_id}',
        )

    @staticmethod
    def _load_trend_scores(county_name: str) -> Dict[str, Dict[str, Any]]:
        """Fetch real trend signals from the cached history."""
        if not county_name:
            return {}
        try:
            from utils.real_trend_calculator import get_all_trend_scores
            return get_all_trend_scores(county_name) or {}
        except Exception as exc:
            logger.warning(
                "Trend signal lookup failed for %s: %s", county_name, exc,
            )
            return {}

    @classmethod
    def _build_projection_payload(
        cls,
        current_risk_data: Dict[str, Any],
        trend_scores: Dict[str, Dict[str, Any]],
        band_base: float,
        band_per_year: float,
        scope_label: str,
    ) -> Dict[str, Any]:
        current_year = datetime.now().year
        years = list(range(current_year, current_year + _PROJECTION_HORIZON_YEARS))

        if not trend_scores:
            logger.info(
                "No real trend data available for %s; returning unavailable "
                "projection payload (no synthetic fill).", scope_label,
            )
            return {
                'available': False,
                'years': years,
                'predictions': {},
                'confidence_intervals': {},
                'historical': [],
                'trend_strength': {},
                'methodology': {
                    'classification': 'model_projection',
                    'description': (
                        'No real cached trend data is available for this '
                        'jurisdiction yet. Projections will appear once the '
                        'scheduled refresh jobs have populated the cache.'
                    ),
                    'data_sources': [],
                },
                'last_updated': datetime.utcnow().isoformat(),
            }

        predictions: Dict[str, List[float]] = {}
        confidence_intervals: Dict[str, Dict[str, List[float]]] = {}
        trend_strength: Dict[str, Dict[str, Any]] = {}
        per_domain_sources: Dict[str, List[str]] = {}

        composite_slopes: List[float] = []
        composite_signal_count = 0

        for risk_key, trend_keys in _RISK_TO_TREND.items():
            if risk_key == 'total_risk':
                continue  # synthesized after the loop

            current_value = float(current_risk_data.get(risk_key, 0.5) or 0.5)
            slope, signal_count, sources = cls._aggregate_slope(
                trend_keys or [], trend_scores,
            )

            if signal_count > 0:
                composite_slopes.append(slope)
                composite_signal_count += signal_count

            projection = cls._project_series(current_value, slope)
            band = cls._confidence_band(projection, band_base, band_per_year)

            predictions[risk_key] = projection
            confidence_intervals[risk_key] = band
            trend_strength[risk_key] = cls._summarize_trend(slope, signal_count)
            per_domain_sources[risk_key] = sources

        # Synthesize the total-risk projection from the per-domain projections,
        # weighted equally (the composite weighting in PHRAT is itself
        # data-dependent, so a simple mean is the most defensible projection).
        total_current = float(current_risk_data.get('total_risk_score', 0.5) or 0.5)
        if composite_slopes:
            total_slope = sum(composite_slopes) / len(composite_slopes)
        else:
            total_slope = 0.0
        total_projection = cls._project_series(total_current, total_slope)
        predictions['total_risk'] = total_projection
        confidence_intervals['total_risk'] = cls._confidence_band(
            total_projection, band_base, band_per_year,
        )
        trend_strength['total_risk'] = cls._summarize_trend(
            total_slope, composite_signal_count,
        )

        # Two historical anchor points: previous-year reconstruction (current
        # minus one year of slope) and the current value. Reconstructed from
        # the same real trend slope so the chart line is continuous.
        historical = [max(0.0, min(1.0, total_current - total_slope)), total_current]

        all_sources = sorted({
            src for sources in per_domain_sources.values() for src in sources
        })

        return {
            'available': True,
            'years': years,
            'predictions': predictions,
            'confidence_intervals': confidence_intervals,
            'historical': historical,
            'trend_strength': trend_strength,
            'methodology': {
                'classification': 'model_projection',
                'description': (
                    'Linear extrapolation anchored to the current assessment '
                    'score. Annual slope is derived from real cached trend '
                    'signals; confidence band widens each year to reflect '
                    'cumulative extrapolation uncertainty. Not a statistical '
                    'forecast - do not interpret as a prediction of specific '
                    'future events.'
                ),
                'data_sources': all_sources,
                'horizon_years': _PROJECTION_HORIZON_YEARS,
                'signal_count': composite_signal_count,
            },
            'last_updated': datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _aggregate_slope(
        trend_keys: List[str],
        trend_scores: Dict[str, Dict[str, Any]],
    ) -> tuple[float, int, List[str]]:
        """Convert one or more real trend signals into an annual slope.

        Each trend score from real_trend_calculator is a 0-1 score where
        0.5 is "no change". We map that into an annual delta in the same
        0-1 risk space: above-0.5 trend pushes risk up, below-0.5 pushes
        it down. Magnitude is bounded so a single noisy signal cannot
        dominate the projection.
        """
        slopes: List[float] = []
        sources: List[str] = []
        for key in trend_keys:
            entry = trend_scores.get(key)
            if not entry:
                continue
            score = entry.get('score') if isinstance(entry, dict) else None
            if score is None:
                continue
            try:
                score = float(score)
            except (TypeError, ValueError):
                continue
            # 0.5 -> 0 slope, 1.0 -> +0.04/year, 0.0 -> -0.04/year.
            slope = max(-0.04, min(0.04, (score - 0.5) * 0.08))
            slopes.append(slope)
            label = entry.get('source') if isinstance(entry, dict) else None
            if label:
                sources.append(str(label))
            else:
                sources.append(f'real_trend_calculator:{key}')

        if not slopes:
            return 0.0, 0, []
        return sum(slopes) / len(slopes), len(slopes), sources

    @staticmethod
    def _project_series(current_value: float, slope: float) -> List[float]:
        """Project a single value forward by _PROJECTION_HORIZON_YEARS."""
        series: List[float] = []
        value = float(current_value)
        for _ in range(_PROJECTION_HORIZON_YEARS):
            value = max(0.0, min(1.0, value + slope))
            series.append(round(value, 4))
        return series

    @staticmethod
    def _confidence_band(
        series: List[float],
        band_base: float,
        band_per_year: float,
    ) -> Dict[str, List[float]]:
        """Return an asymmetric-bounded confidence band that widens each year."""
        lower: List[float] = []
        upper: List[float] = []
        for idx, value in enumerate(series):
            half_width = band_base + band_per_year * idx
            lower.append(round(max(0.0, value - half_width), 4))
            upper.append(round(min(1.0, value + half_width), 4))
        return {'lower': lower, 'upper': upper}

    @staticmethod
    def _summarize_trend(slope: float, signal_count: int) -> Dict[str, Any]:
        """Translate a numeric slope into the (direction, strength) summary."""
        if signal_count == 0:
            return {'direction': 'unknown', 'strength': 0.0,
                    'signal_count': 0, 'slope_per_year': 0.0}
        if slope > 0.005:
            direction = 'increasing'
        elif slope < -0.005:
            direction = 'decreasing'
        else:
            direction = 'stable'
        return {
            'direction': direction,
            'strength': round(min(1.0, abs(slope) * 25.0), 2),
            'signal_count': signal_count,
            'slope_per_year': round(slope, 4),
        }
