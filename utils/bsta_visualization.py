"""
BSTA visualization payload builder.

Enriches the existing temporal_risk_data dictionary (produced by
utils.temporal_risk.TemporalRiskComponent) with the additional fields the
dashboard needs to render the redesigned BSTA panel:

- seasonal_curve:   list of 12 monthly factors (0-1) for the hazard's
                    seasonal pattern, used to render an inline SVG sparkline
- current_month:    1-12 index for the "you are here" dot on the sparkline
- peak_months:      list of 3-letter month names making up the seasonal peak
- in_peak_window:   true if current month is in or adjacent to the peak
- trend_direction:  'rising' | 'declining' | 'stable'
- has_acute:        true only for infectious_disease (the only domain that
                    still carries the Acute component, per the 2026-05
                    retirement)
- posture_label:    plain-language sentence describing the temporal posture
                    (e.g. "Strongly seasonal -- currently in peak window
                    (Jun-Aug)")
- baseline_level:   'high' | 'elevated' | 'moderate' | 'low' bucket

This module is pure-Python and pulls no external data. It reads the
canonical seasonal patterns from utils.temporal_risk.SEASONAL_PATTERNS so
the sparkline and the composite calculation stay in sync.
"""

from datetime import datetime
from typing import Dict, List, Optional

from utils.temporal_risk import SEASONAL_PATTERNS

_MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _baseline_bucket(baseline: float) -> str:
    if baseline >= 0.7:
        return 'high'
    if baseline >= 0.5:
        return 'elevated'
    if baseline >= 0.3:
        return 'moderate'
    return 'low'


def _trend_direction(trend: float) -> str:
    if trend is None:
        return 'stable'
    if trend >= 0.55:
        return 'rising'
    if trend <= 0.45:
        return 'declining'
    return 'stable'


def _trend_phrase(direction: str, has_trend: bool) -> str:
    if not has_trend:
        return 'no multi-year trend tracked'
    return {
        'rising': 'rising trend',
        'declining': 'declining trend',
        'stable': 'stable trend',
    }[direction]


def _peak_window(curve: List[float]) -> List[int]:
    """Return the contiguous month indices (1-12) where the curve is
    within 15% of its peak value. Handles wraparound (winter storm
    peaks Dec-Feb)."""
    if not curve:
        return []
    peak = max(curve)
    if peak <= 0:
        return []
    threshold = peak * 0.85
    peak_months = [i + 1 for i, v in enumerate(curve) if v >= threshold]
    return peak_months


def _format_peak_window(peak_months: List[int]) -> str:
    if not peak_months:
        return ''
    if len(peak_months) == 1:
        return _MONTH_ABBR[peak_months[0] - 1]
    # detect wraparound (e.g. [11, 12, 1, 2])
    sorted_m = sorted(peak_months)
    gaps = [sorted_m[i + 1] - sorted_m[i] for i in range(len(sorted_m) - 1)]
    if gaps and max(gaps) > 1:
        # split point
        split_idx = gaps.index(max(gaps)) + 1
        tail = sorted_m[split_idx:]
        head = sorted_m[:split_idx]
        ordered = tail + head
        return f"{_MONTH_ABBR[ordered[0] - 1]}-{_MONTH_ABBR[ordered[-1] - 1]}"
    return f"{_MONTH_ABBR[sorted_m[0] - 1]}-{_MONTH_ABBR[sorted_m[-1] - 1]}"


def _in_peak_window(current_month: int, peak_months: List[int]) -> bool:
    """Current month is in or adjacent to peak (allowing +/- 1 month
    tolerance with wraparound)."""
    if not peak_months:
        return False
    if current_month in peak_months:
        return True
    for m in peak_months:
        diff = abs(m - current_month)
        diff = min(diff, 12 - diff)
        if diff <= 1:
            return True
    return False


def _is_flat_curve(curve: List[float]) -> bool:
    if not curve:
        return True
    return (max(curve) - min(curve)) < 0.15


def derive_posture_label(hazard_type: str,
                         baseline: float,
                         trend: float,
                         acute: float,
                         seasonal_curve: List[float],
                         current_month: int,
                         has_acute: bool,
                         has_trend: bool) -> str:
    """Build a plain-language description of this hazard's temporal posture."""
    baseline = baseline if baseline is not None else 0.5
    trend = trend if trend is not None else 0.5
    acute = acute if acute is not None else 0.0
    direction = _trend_direction(trend)
    trend_phrase = _trend_phrase(direction, has_trend)
    baseline_level = _baseline_bucket(baseline)
    peak_months = _peak_window(seasonal_curve)
    peak_label = _format_peak_window(peak_months)
    in_peak = _in_peak_window(current_month, peak_months)
    flat = _is_flat_curve(seasonal_curve)

    # Infectious-disease specific framing
    if has_acute:
        if acute >= 0.6:
            return (f"Active outbreak signal on a {baseline_level} baseline "
                    f"(surveillance elevated)")
        if acute >= 0.4:
            return (f"Elevated surveillance signal on a {baseline_level} "
                    f"baseline")
        if in_peak and not flat:
            return (f"In seasonal peak window ({peak_label}); "
                    f"{baseline_level} baseline, surveillance quiet")
        return (f"{baseline_level.title()} baseline, surveillance quiet, "
                f"off-peak ({peak_label} peak)")

    # All other domains: B+S+T model
    if baseline >= 0.7:
        return f"Persistent {baseline_level} year-round risk, {trend_phrase}"

    if flat:
        # No meaningful seasonality (e.g. active_shooter)
        return f"{baseline_level.title()} baseline, year-round, {trend_phrase}"

    if in_peak:
        return (f"Strongly seasonal -- currently in peak window "
                f"({peak_label}); {trend_phrase}")

    return (f"Strongly seasonal (peaks {peak_label}), currently off-peak; "
            f"{trend_phrase}")


def build_bsta_visualization(temporal_risk_data: Dict,
                             current_month: Optional[int] = None) -> Dict:
    """
    Enrich an existing temporal_risk_data dict with visualization fields.

    Mutates and returns the same dict. Each hazard entry gains a
    `visualization` sub-dict consumed by templates/dashboard/_bsta_temporal.html.
    """
    if current_month is None:
        current_month = datetime.now().month

    for hazard_type, entry in temporal_risk_data.items():
        components = entry.get('temporal_components', {}) or {}
        baseline = components.get('baseline')
        seasonal = components.get('seasonal')
        trend = components.get('trend')
        acute = components.get('acute')

        # Pull the canonical 12-month seasonal pattern. Fall back to a flat
        # 0.5 curve so the sparkline still renders for unknown hazards.
        pattern = SEASONAL_PATTERNS.get(
            hazard_type, {m: 0.5 for m in range(1, 13)}
        )
        seasonal_curve = [float(pattern.get(m, 0.5)) for m in range(1, 13)]

        has_acute = (hazard_type == 'infectious_disease')
        has_trend = not has_acute  # ID uses acute INSTEAD of trend

        peak_months = _peak_window(seasonal_curve)
        in_peak = _in_peak_window(current_month, peak_months)
        direction = _trend_direction(trend if trend is not None else 0.5)

        # Composite "now" marker on the sparkline. We position the dot at
        # the current month and size it by the composite score so the eye
        # picks up both timing and magnitude.
        now_value = entry.get('composite_score')
        if now_value is None:
            now_value = baseline if baseline is not None else 0.5

        posture = derive_posture_label(
            hazard_type=hazard_type,
            baseline=baseline,
            trend=trend,
            acute=acute,
            seasonal_curve=seasonal_curve,
            current_month=current_month,
            has_acute=has_acute,
            has_trend=has_trend,
        )

        entry['visualization'] = {
            'seasonal_curve': seasonal_curve,
            'current_month': current_month,
            'current_month_label': _MONTH_ABBR[current_month - 1],
            'peak_months': peak_months,
            'peak_label': _format_peak_window(peak_months),
            'in_peak_window': in_peak,
            'is_flat_curve': _is_flat_curve(seasonal_curve),
            'trend_direction': direction,
            'has_trend': has_trend,
            'has_acute': has_acute,
            'baseline_level': _baseline_bucket(
                baseline if baseline is not None else 0.5
            ),
            'now_value': float(now_value),
            'posture_label': posture,
        }

    return temporal_risk_data
