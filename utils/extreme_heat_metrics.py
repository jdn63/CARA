"""
Extreme Heat support metrics - WI DHS Heat Vulnerability Index era.

Historically this module fetched per-county annual heat-day counts
from CDC EPHT and the NCEI Climate-at-a-Glance heuristic so the
prior EVR heat formula in utils/climate_adjusted_risk.py could read
them. As of v29 the Extreme Heat domain relies solely on the WI DHS
Heat Vulnerability Index (HVI), which already folds environmental
exposure (including extreme-heat-day patterns) and heat-related
health outcomes into a single block-group composite. Per-county
heat-day counts and ED-visit estimates are no longer fetched here.

The remaining accessor functions return HVI-derived informational
values for callers that still import this module (strategic panels,
the dashboard heat tile). New code should call
utils.climate_adjusted_risk.calculate_enhanced_extreme_heat_risk()
directly and read the metrics dict it returns.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ExtremeHeatMetrics:
    """HVI-backed informational metrics for the heat dashboard tile."""

    def get_annual_heat_days(
        self, county_name: str, year: Optional[int] = None
    ) -> Optional[int]:
        """Heat-day counts are folded into the WI DHS HVI composite (v29)."""
        return None

    def get_heat_advisories_count(
        self, county_name: str, year: Optional[int] = None
    ) -> Optional[int]:
        """No longer surfaced separately; HVI environmental sub-index covers it."""
        return None

    def get_elderly_population_percentage(self, county_name: str) -> Optional[float]:
        """HVI population sub-index already includes age structure; not surfaced separately."""
        return None

    def get_heat_related_ed_visits(
        self, county_name: str, year: Optional[int] = None
    ) -> Optional[int]:
        """HVI health sub-index already includes heat-related ED visit patterns."""
        return None

    def get_comprehensive_heat_metrics(self, county_name: str) -> Dict[str, Any]:
        """
        Return the HVI-backed informational payload for a county. The
        underlying score and sub-indices live in
        utils.wi_dhs_hvi.get_hvi_data(); this method imports lazily so
        the legacy callers do not pull HVI machinery at module import
        time.
        """
        try:
            from utils.wi_dhs_hvi import get_hvi_data
            record = get_hvi_data(county_name) or {}
        except Exception as exc:
            logger.debug(
                "extreme_heat_metrics could not read HVI for %s: %s",
                county_name, exc,
            )
            record = {}

        return {
            "annual_heat_days": None,
            "heat_days_source": (
                "Folded into WI DHS HVI composite (environmental + "
                "health sub-indices)"
            ),
            "heat_days_year": None,
            "heat_advisories": None,
            "elderly_percentage": None,
            "ed_visits": None,
            "hvi_score": record.get("vulnerability_score"),
            "hvi_category": record.get("category"),
            "data_year": datetime.now().year,
            "last_updated": record.get("last_updated"),
            "data_sources": {
                "primary": (
                    "Wisconsin DHS Heat Vulnerability Index "
                    "(https://www.dhs.wisconsin.gov/climate/hvi.htm)"
                ),
            },
        }


heat_metrics = ExtremeHeatMetrics()


def get_extreme_heat_metrics(county_name: str) -> Dict[str, Any]:
    """Stable accessor used by other modules and strategic panels."""
    return heat_metrics.get_comprehensive_heat_metrics(county_name)
