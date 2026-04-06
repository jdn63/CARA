"""
Wisconsin DHS Respiratory Surveillance Data

Provides Wisconsin-specific respiratory surveillance data by combining:

  1. CDC NSSP Emergency Department Visits (primary respiratory activity source)
     Fetched via utils.nssp_respiratory.fetch_nssp_wi_respiratory().
     Covers Influenza, COVID-19, and RSV activity levels, ED visit percentages,
     and trends for Wisconsin.  Updated weekly (Fridays).  No API key required.

  2. WI DHS vaccination data estimates (static, manually updated annually)
     MMR county rates: WI DHS WIR county-immunization-data.csv (via dhs_data.py)
     Flu county rates:  County Health Rankings BRFSS (via health_metrics_data.py)
     COVID-19:          WI DHS estimate (static; no live API)

Note: The Wisconsin DHS Tableau respiratory dashboards (bi.wisconsin.gov) and
legacy PDF reports (dhs.wisconsin.gov/influenza/data.htm, retired May 2025)
are no longer used.  Both were inaccessible for automated data collection.
The NSSP dataset used here is the same underlying ESSENCE/NSSP data that
WI DHS Tableau dashboards visualise.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class WisconsinDHSScraper:
    """
    Assembles Wisconsin respiratory surveillance data from the CDC NSSP
    API and static vaccination coverage estimates.

    Respiratory activity data (flu, COVID-19, RSV activity levels, ED
    visit percentages, trends) comes entirely from the NSSP module.

    Vaccination data is assembled from static WI DHS / CHR estimates.
    County-level MMR and flu rates are resolved at assessment time inside
    disease_surveillance.py via the WI DHS WIR CSV and CHR data modules.
    """

    def get_latest_surveillance_data(self) -> Dict[str, Any]:
        """
        Get current Wisconsin respiratory surveillance data.

        Delegates to fetch_nssp_wi_respiratory() for respiratory activity,
        then attaches vaccination data.
        """
        from utils.nssp_respiratory import fetch_nssp_wi_respiratory
        data = fetch_nssp_wi_respiratory()
        data["vaccination_data"] = self._get_vaccination_data()
        return data

    def _get_vaccination_data(self) -> Dict[str, Any]:
        """Assemble Wisconsin vaccination coverage estimates."""
        return {
            "mmr_vaccination": self._get_fallback_mmr_data(),
            "flu_vaccination": self._get_flu_vaccination_estimates(),
            "school_vaccination": self._get_school_vaccination_estimates(),
            "last_updated": datetime.now().isoformat(),
            "data_source_note": (
                "Statewide estimates used as fallbacks only.  County-level MMR "
                "rates are resolved from WI DHS WIR county-immunization-data.csv "
                "and county flu rates from County Health Rankings BRFSS at "
                "assessment time."
            ),
        }

    def _get_mmr_vaccination_data(self) -> Dict[str, Any]:
        """
        MMR statewide fallback.  County-specific rates are resolved
        via _fetch_mmr_county_data() in utils/dhs_data.py at assessment time.
        """
        return self._get_fallback_mmr_data()

    def _get_flu_vaccination_estimates(self) -> Dict[str, float]:
        """
        Statewide influenza vaccination estimates for Wisconsin.

        These are statewide averages used only when county-specific CHR
        data is unavailable.  County rates from CHR BRFSS (all-ages seasonal)
        are preferred and resolved via get_flu_vaccination_rate() in
        utils/health_metrics_data.py at assessment time.

        Source: Wisconsin DHS historical influenza vaccination surveillance.
        WI range: ~22% (Taylor/Polk) to ~69% (Dane); statewide mean ~45.6%.
        """
        return {
            "children_6_months_17_years": 62.8,
            "adults_18_64_years": 45.2,
            "adults_65_plus": 71.3,
            "overall_population": 45.6,
            "data_source": "WI DHS historical flu vaccination rates (statewide average)",
        }

    def _get_school_vaccination_estimates(self) -> Dict[str, float]:
        """
        School-year vaccination compliance estimates (2024-2025 school year).
        Source: Wisconsin DHS School Immunization Data.
        """
        return {
            "meeting_minimum_requirements": 86.4,
            "mmr_compliance": 88.1,
            "dtap_compliance": 87.9,
            "polio_compliance": 88.3,
            "data_source": "Wisconsin DHS School Immunization Data 2024-2025",
        }

    def _get_fallback_vaccination_data(self) -> Dict[str, Any]:
        """Fallback when vaccination data assembly fails."""
        return {
            "mmr_vaccination": self._get_fallback_mmr_data(),
            "flu_vaccination": self._get_flu_vaccination_estimates(),
            "school_vaccination": self._get_school_vaccination_estimates(),
            "last_updated": datetime.now().isoformat(),
            "data_source": "fallback_estimates",
        }

    def _get_fallback_mmr_data(self) -> Dict[str, Any]:
        """
        Statewide MMR fallback.  County-specific rates from WI DHS WIR
        county-immunization-data.csv are preferred and resolved at assessment time.
        """
        return {
            "children_24_months": 85.5,
            "children_5_6_years": 88.2,
            "children_5_18_years": 87.8,
            "data_source": "Wisconsin DHS WIR (statewide historical averages)",
            "report_year": "2024",
        }


def get_wisconsin_surveillance_data() -> Dict[str, Any]:
    """
    Get current Wisconsin respiratory surveillance data.

    Primary source: CDC NSSP Emergency Department Visits dataset
    (data.cdc.gov/resource/vutn-jzwm.json), Wisconsin-specific, weekly.

    Vaccination data is appended from static WI DHS / CHR estimates.
    County-level MMR and flu rates override statewide estimates at
    assessment time within disease_surveillance.py.
    """
    scraper = WisconsinDHSScraper()
    return scraper.get_latest_surveillance_data()


def refresh_dhs_surveillance_data() -> bool:
    """
    Scheduler-callable function to refresh the NSSP respiratory cache.

    Clears the NSSP cache and fetches fresh data from data.cdc.gov.
    Called weekly by the APScheduler disease_surveillance job.
    """
    try:
        from utils.persistent_cache import clear_cache_by_prefix
        from utils.nssp_respiratory import NSSP_CACHE_KEY, fetch_nssp_wi_respiratory
        clear_cache_by_prefix(NSSP_CACHE_KEY)
        result = fetch_nssp_wi_respiratory()
        success = result.get("data_source") == "nssp_ed_visits"
        if success:
            logger.info(
                f"NSSP respiratory cache refreshed (week: {result.get('report_date')})"
            )
        else:
            logger.warning("NSSP respiratory refresh returned fallback data")
        return success
    except Exception as exc:
        logger.error(f"Error refreshing NSSP respiratory data: {exc}")
        return False
