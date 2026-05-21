"""SVI (Social Vulnerability Index) multiplier helpers.

Consolidates the "apply SVI themes as a capped multiplier on a domain
base score" pattern that recurred in several domain calculators with
slightly different math. The additive form here is the canonical
pattern going forward; multiplicative compositions of two SVI themes
(as the legacy air-quality path used) compound rapidly above 1.0 and
were flagged in code review (Medium #8).

Formula:

    multiplier = clamp(1.0 + sum(theme_value * theme_weight), 1.0, cap)
    adjusted   = min(1.0, base * multiplier)

Each theme contributes additively, so two themes at value 0.5 with
weights 0.3 and 0.2 yield a multiplier of 1.25, not (1.15 * 1.10) =
1.265. The difference is small at neutral values but grows quickly
when both themes spike.
"""

from __future__ import annotations

from typing import Dict


def apply_svi_multiplier(
    base: float,
    themes: Dict[str, float],
    weights: Dict[str, float],
    cap: float = 1.5,
) -> float:
    """Apply an additive, capped SVI multiplier to a base score.

    Args:
        base: Domain risk score in [0, 1].
        themes: SVI theme dict (e.g. {'housing_transportation': 0.5,
            'socioeconomic': 0.4}). Missing themes resolve to 0.5
            (neutral) per CARA convention.
        weights: How much each theme contributes (e.g.
            {'housing_transportation': 0.3, 'socioeconomic': 0.2}).
            Only keys present here are added to the multiplier.
        cap: Upper bound on the multiplier. Default 1.5 mirrors the
            historical air-quality cap.

    Returns:
        Adjusted score in [0, 1].
    """
    additive = 0.0
    for theme, weight in weights.items():
        value = float(themes.get(theme, 0.5))
        additive += value * float(weight)
    multiplier = max(1.0, min(cap, 1.0 + additive))
    return min(1.0, float(base) * multiplier)
