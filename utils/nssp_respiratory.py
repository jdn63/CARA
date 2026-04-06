"""
CDC NSSP Respiratory Emergency Department Visits

Fetches Wisconsin respiratory virus activity data from the CDC National
Syndromic Surveillance Program (NSSP) via the Socrata open-data API on
data.cdc.gov.  No API key is required.

Dataset:  2023 Respiratory Virus Response - NSSP Emergency Department Visits
          (COVID-19, Flu, RSV, Combined)
Endpoint: https://data.cdc.gov/resource/vutn-jzwm.json
Coverage: Wisconsin-specific weekly data, Influenza + COVID-19 + RSV
Update:   Every Friday
History:  Available from October 2022

The key metric is ``percent_visits``: the percentage of all emergency
department visits for a given week that are attributable to each pathogen.
This is the same NSSP/ESSENCE data that WI DHS visualises in its Tableau
respiratory dashboards.

References:
  https://data.cdc.gov/Public-Health-Surveillance/
  2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/vutn-jzwm
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

NSSP_ENDPOINT = "https://data.cdc.gov/resource/vutn-jzwm.json"
NSSP_DATASET_URL = (
    "https://data.cdc.gov/Public-Health-Surveillance/"
    "2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/vutn-jzwm"
)
NSSP_CACHE_KEY = "nssp_wi_respiratory_v1"
NSSP_CACHE_DAYS = 1

_SCRAPER_UA = "CARA-WI-PublicHealth/1.0 (contact: github.com/jdn63)"

# Activity-level thresholds (% of total ED visits per pathogen).
# Derived from CDC NSSP seasonal baselines and WI DHS historical patterns.
_THRESHOLDS: Dict[str, List[tuple]] = {
    "influenza": [
        (0.0, 0.5, "minimal"),
        (0.5, 1.5, "low"),
        (1.5, 3.0, "moderate"),
        (3.0, 6.0, "high"),
        (6.0, float("inf"), "very_high"),
    ],
    "covid19": [
        (0.0, 0.3, "minimal"),
        (0.3, 0.8, "low"),
        (0.8, 2.0, "moderate"),
        (2.0, 4.0, "high"),
        (4.0, float("inf"), "very_high"),
    ],
    "rsv": [
        (0.0, 0.3, "minimal"),
        (0.3, 0.8, "low"),
        (0.8, 1.5, "moderate"),
        (1.5, 3.0, "high"),
        (3.0, float("inf"), "very_high"),
    ],
}

_LEVEL_INT = {"minimal": 0, "low": 1, "moderate": 2, "high": 3, "very_high": 4}
_INT_LEVEL = {v: k for k, v in _LEVEL_INT.items()}

_PATHOGEN_MAP = {
    "Influenza": "influenza",
    "COVID-19": "covid19",
    "RSV": "rsv",
}


def _pct_to_level(pct: float, pathogen: str) -> str:
    for lo, hi, label in _THRESHOLDS.get(pathogen, _THRESHOLDS["influenza"]):
        if lo <= pct < hi:
            return label
    return "moderate"


def _trend(current: float, prior: float) -> str:
    if prior <= 0:
        return "stable"
    change = (current - prior) / prior * 100
    if change >= 20:
        return "increasing"
    if change <= -15:
        return "decreasing"
    return "stable"


def _overall_level(flu: str, covid: str, rsv: str) -> str:
    weighted = (
        _LEVEL_INT.get(flu, 1) * 0.50
        + _LEVEL_INT.get(covid, 0) * 0.30
        + _LEVEL_INT.get(rsv, 0) * 0.20
    )
    if weighted < 0.4:
        return "minimal"
    if weighted < 1.0:
        return "low"
    if weighted < 2.0:
        return "moderate"
    if weighted < 3.0:
        return "high"
    return "very_high"


def _risk_indicators(flu_pct: float, covid_pct: float, rsv_pct: float) -> Dict[str, float]:
    flu_s = min(1.0, flu_pct / 6.0)
    covid_s = min(1.0, covid_pct / 4.0)
    rsv_s = min(1.0, rsv_pct / 3.0)
    activity = flu_s * 0.50 + covid_s * 0.30 + rsv_s * 0.20
    lab = min(1.0, (flu_pct + covid_pct + rsv_pct) / 10.0)
    combined = activity * 0.70 + lab * 0.30
    return {
        "activity_risk": round(activity, 3),
        "laboratory_risk": round(lab, 3),
        "combined_risk": round(min(1.0, combined), 3),
        "confidence": 0.90,
    }


def fetch_nssp_wi_respiratory() -> Dict[str, Any]:
    """
    Fetch Wisconsin respiratory ED visit data from the CDC NSSP Socrata API.

    Returns a structured dict with:
      - statewide_activity: activity levels and trajectories per pathogen
      - ed_visit_data: raw percent_visits values (% of ED visits)
      - emergency_dept_data: combined respiratory burden and trends
      - risk_indicators: normalized composite scores for CARA
      - data provenance fields

    Results are cached for 24 hours via the persistent cache.
    The NSSP dataset is updated every Friday; a 24-hour cache is acceptable
    because daily re-fetches stay current while avoiding unnecessary API load.
    """
    cached = get_from_persistent_cache(NSSP_CACHE_KEY, max_age_days=NSSP_CACHE_DAYS)
    if cached:
        logger.info(
            "NSSP respiratory data loaded from cache "
            f"(week: {cached.get('report_date', 'unknown')})"
        )
        return cached

    try:
        resp = requests.get(
            NSSP_ENDPOINT,
            params={
                "$where": "geography='Wisconsin'",
                "$order": "week_end DESC",
                "$limit": 36,
            },
            headers={"User-Agent": _SCRAPER_UA},
            timeout=20,
        )
        resp.raise_for_status()
        rows = resp.json()

        if not rows:
            logger.warning("NSSP API: empty response for Wisconsin")
            return _fallback()

        by_week: Dict[str, Dict[str, float]] = {}
        for row in rows:
            week = (row.get("week_end") or "").split("T")[0]
            raw_pathogen = row.get("pathogen", "")
            pathogen = _PATHOGEN_MAP.get(raw_pathogen)
            if not week or not pathogen:
                continue
            try:
                pct = float(row.get("percent_visits", 0))
            except (ValueError, TypeError):
                pct = 0.0
            if week not in by_week:
                by_week[week] = {}
            by_week[week][pathogen] = pct

        if not by_week:
            logger.warning("NSSP API: no usable rows for Wisconsin")
            return _fallback()

        sorted_weeks = sorted(by_week.keys(), reverse=True)
        current_week = sorted_weeks[0]
        current = by_week[current_week]

        flu_pct = current.get("influenza", 0.0)
        covid_pct = current.get("covid19", 0.0)
        rsv_pct = current.get("rsv", 0.0)

        prior_week = sorted_weeks[3] if len(sorted_weeks) > 3 else None
        prior = by_week[prior_week] if prior_week else {}

        flu_trend = _trend(flu_pct, prior.get("influenza", flu_pct))
        covid_trend = _trend(covid_pct, prior.get("covid19", covid_pct))
        rsv_trend = _trend(rsv_pct, prior.get("rsv", rsv_pct))

        flu_level = _pct_to_level(flu_pct, "influenza")
        covid_level = _pct_to_level(covid_pct, "covid19")
        rsv_level = _pct_to_level(rsv_pct, "rsv")
        overall = _overall_level(flu_level, covid_level, rsv_level)

        result = {
            "report_url": NSSP_DATASET_URL,
            "report_date": current_week,
            "last_updated": datetime.now().isoformat(),
            "data_source": "nssp_ed_visits",
            "data_source_label": "CDC NSSP Emergency Department Visits (data.cdc.gov/resource/vutn-jzwm)",
            "statewide_activity": {
                "overall": overall,
                "influenza": flu_level,
                "covid19": covid_level,
                "rsv": rsv_level,
                "influenza_trajectory": flu_trend,
                "covid19_trajectory": covid_trend,
                "rsv_trajectory": rsv_trend,
            },
            "ed_visit_data": {
                "influenza_percent": flu_pct,
                "covid19_percent": covid_pct,
                "rsv_percent": rsv_pct,
                "week_end": current_week,
                "metric_note": (
                    "Percent of all ED visits attributable to each pathogen "
                    "(CDC NSSP/ESSENCE syndromic surveillance)"
                ),
            },
            "emergency_dept_data": {
                "respiratory_visits_percent": round(flu_pct + covid_pct + rsv_pct, 1),
                "trends": {
                    "influenza": flu_trend,
                    "covid19": covid_trend,
                    "rsv": rsv_trend,
                },
            },
            "regional_activity": {},
            "risk_indicators": _risk_indicators(flu_pct, covid_pct, rsv_pct),
        }

        logger.info(
            f"NSSP fetched week {current_week}: "
            f"flu={flu_pct}% [{flu_level}/{flu_trend}], "
            f"covid={covid_pct}% [{covid_level}/{covid_trend}], "
            f"rsv={rsv_pct}% [{rsv_level}/{rsv_trend}]"
        )
        set_in_persistent_cache(NSSP_CACHE_KEY, result, expiry_days=NSSP_CACHE_DAYS)
        return result

    except Exception as exc:
        logger.error(f"Error fetching NSSP respiratory data: {exc}")
        return _fallback()


def _fallback() -> Dict[str, Any]:
    """
    Conservative fallback when the NSSP API is unreachable.

    Values represent a typical low-activity early-spring baseline for
    Wisconsin, consistent with historical patterns when influenza season
    is winding down.  Confidence is set to 0.40 to signal data limitation.
    """
    return {
        "report_url": NSSP_DATASET_URL,
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().isoformat(),
        "data_source": "nssp_fallback",
        "data_source_label": "CDC NSSP ED Visits (fallback - API unavailable)",
        "statewide_activity": {
            "overall": "low",
            "influenza": "low",
            "covid19": "minimal",
            "rsv": "minimal",
            "influenza_trajectory": "stable",
            "covid19_trajectory": "stable",
            "rsv_trajectory": "stable",
        },
        "ed_visit_data": {
            "influenza_percent": 1.5,
            "covid19_percent": 0.3,
            "rsv_percent": 0.5,
            "week_end": None,
            "metric_note": "Fallback estimates - NSSP API unavailable",
        },
        "emergency_dept_data": {
            "respiratory_visits_percent": 2.3,
            "trends": {
                "influenza": "stable",
                "covid19": "stable",
                "rsv": "stable",
            },
        },
        "regional_activity": {},
        "risk_indicators": {
            "activity_risk": 0.30,
            "laboratory_risk": 0.23,
            "combined_risk": 0.28,
            "confidence": 0.40,
        },
    }
