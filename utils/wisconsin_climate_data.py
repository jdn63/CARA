"""
Wisconsin statewide heat-related constants for use as exposure baselines.

CLEANUP HISTORY:
Prior versions of this module shipped a hand-keyed dictionary
(WISCONSIN_COUNTY_CLIMATE_DATA) with explicit annual_heat_days,
elderly_population_pct, estimated_heat_ed_visits and heat_advisories_2024
values for 15 Wisconsin counties (out of 72), with all other counties
silently falling back to a single default row.  That arrangement had two
problems:
    1. The per-county values were not traceable to a specific NOAA NCEI
       endpoint or CSV.  They appeared to be NOAA-informed author
       estimates, not a reproducible download.
    2. 57 of 72 counties received an identical default, producing the
       illusion of per-county precision in downstream displays.

This module now returns statewide values from cited public sources
and delegates demographic data to utils.census_data_loader, which is
the authoritative Census ACS loader.  Function signatures are
preserved so existing callers (utils/climate_adjusted_risk.py,
utils/extreme_heat_metrics.py) continue to work without change.

FUTURE IMPROVEMENT:
A scheduler job that pulls NOAA NCEI nClimGrid-County or daily-summaries
data per WI county and computes the annual count of days TMAX >= 90F
from a documented station-to-county mapping would replace the
statewide constant in get_wisconsin_heat_days() with a real per-county
value.  The NCEI Climate-at-a-Glance per-county time-series endpoint
returned 404 from this environment at the time of this cleanup
(2026-05-19); pursuing this should include verifying the current
endpoint URL pattern with NOAA documentation.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Wisconsin statewide annual count of days with daily maximum temperature
# >= 90 degrees F.  Source: NOAA NCEI Wisconsin state climate summary
# (1991-2020 climate normals) reports a statewide average of roughly
# 10-14 days above 90F per year; midpoint used here.
_WI_STATEWIDE_ANNUAL_HEAT_DAYS = 12

# Wisconsin statewide average count of NWS heat advisories per County
# Warning Area per year.  Source: NWS Milwaukee/Sullivan, Green Bay, and
# La Crosse forecast offices issue roughly 2-4 heat advisories per year
# across their WI service areas in a typical season; midpoint used here.
_WI_STATEWIDE_ANNUAL_HEAT_ADVISORIES = 3

# Wisconsin statewide rate of heat-related emergency department visits per
# 100,000 population per year.  Source: WI DHS Environmental Public Health
# Tracking heat-related illness indicator reports a statewide rate in the
# range of 5-7 per 100,000 per year over the 2015-2022 period; midpoint
# used here.  ED visit COUNTS are then derived from Census ACS county
# population, not hand-keyed.
_WI_STATEWIDE_HEAT_ED_RATE_PER_100K = 6.0


def get_wisconsin_heat_days(county_name: str) -> int:
    """
    Return the Wisconsin statewide annual count of days TMAX >= 90F.

    Until a per-county NOAA NCEI loader is integrated (see module
    docstring), every Wisconsin county returns the same statewide value.
    The county_name argument is accepted for API compatibility and is
    only used in log output.
    """
    clean = county_name.replace(' County', '').strip() if county_name else ''
    logger.info(
        "Wisconsin statewide annual heat days returned for %s: %d "
        "(per-county NOAA loader not yet integrated)",
        clean, _WI_STATEWIDE_ANNUAL_HEAT_DAYS,
    )
    return _WI_STATEWIDE_ANNUAL_HEAT_DAYS


def get_wisconsin_elderly_population(county_name: str) -> float:
    """
    Return the population aged 65+ percentage for a Wisconsin county.

    Delegates to utils.census_data_loader.wisconsin_census, which is the
    authoritative Census ACS loader.  Falls back to the Wisconsin
    statewide percentage (18.7%, ACS 2018-2022 5-year estimates) only
    if the Census loader is unavailable for the requested county.
    """
    try:
        from utils.census_data_loader import wisconsin_census
        pct = wisconsin_census.get_elderly_population_percentage(county_name)
        if pct is not None:
            return pct
    except Exception as e:
        logger.warning(
            "Census elderly fetch failed for %s: %s; using WI statewide 18.7",
            county_name, e,
        )
    return 18.7


def get_wisconsin_heat_ed_visits(county_name: str) -> int:
    """
    Return an estimated annual count of heat-related ED visits for a
    Wisconsin county, derived from Census ACS population and the WI DHS
    EPHT statewide heat-related ED-visit rate per 100,000.

    This replaces the previous hand-keyed per-county estimate.  A real
    per-county count from the WI DHS EPHT county-level export would be
    a follow-up improvement.
    """
    try:
        from utils.census_data_loader import wisconsin_census
        population = wisconsin_census.get_county_population(county_name) or 80000
    except Exception as e:
        logger.warning(
            "Census population fetch failed for %s: %s; using WI median 80000",
            county_name, e,
        )
        population = 80000
    return int(round((population / 100000.0) * _WI_STATEWIDE_HEAT_ED_RATE_PER_100K))


def get_wisconsin_heat_advisories(county_name: str) -> int:
    """
    Return the Wisconsin statewide annual count of NWS heat advisories.

    Until per-CWA NWS advisory counts are integrated, every Wisconsin
    county returns the same statewide value.  The county_name argument
    is accepted for API compatibility.
    """
    return _WI_STATEWIDE_ANNUAL_HEAT_ADVISORIES
