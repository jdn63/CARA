"""
CDC NNDSS Wisconsin Communicable Disease Surveillance

Fetches Wisconsin weekly case counts for reportable communicable diseases
from the CDC National Notifiable Diseases Surveillance System (NNDSS) via
the Socrata open-data API on data.cdc.gov.  No API key is required.

Dataset:  NNDSS Weekly Data (current year, all reportable conditions)
Endpoint: https://data.cdc.gov/resource/x9gk-5huc.json
Coverage: All US states + territories, weekly, by disease label
Update:   Weekly (typically Tuesdays for the prior MMWR week)
Diseases tracked here:
    - Measles, Indigenous
    - Measles, Imported
    - Meningococcal disease, All serogroups

Pertussis was removed in v28.7. The prior "pertussis_elevated" flag was
a CARA-specific operational heuristic (1.5x 5-year weekly median, floor
5 cases) without CSTE/CDC published provenance. Re-introduction will be
considered only when a Farrington- or EARS-style aberration detector
based on the full multi-year per-week NNDSS distribution can be wired
in; until then, no pertussis signal is surfaced.

This is the only public machine-readable source for these reportable
diseases for Wisconsin.  WI DHS WEDSS itself does not expose a public
API; WEDSS data flows to CDC NNDSS which publishes the aggregated
state-level counts here.

Granularity note: NNDSS is state-level.  Wisconsin counts are applied
uniformly to all 72 counties as a statewide outbreak signal, not a
county-specific incidence rate.  Callers must surface this clearly.

References:
  https://www.cdc.gov/nndss/
  https://data.cdc.gov/Public-Health-Surveillance/NNDSS-Weekly-Data/x9gk-5huc
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

NNDSS_ENDPOINT = "https://data.cdc.gov/resource/x9gk-5huc.json"
NNDSS_DATASET_URL = (
    "https://data.cdc.gov/Public-Health-Surveillance/"
    "NNDSS-Weekly-Data/x9gk-5huc"
)
NNDSS_CACHE_KEY = "nndss_wi_communicable_v1"
NNDSS_CACHE_DAYS = 7

_SCRAPER_UA = "CARA-WI-PublicHealth/1.0 (contact: github.com/jdn63)"

# NNDSS disease label exactly as it appears in the dataset (case-sensitive).
# These labels are stable; CDC has used them since the NNDSS modernization.
_DISEASE_LABELS = {
    "measles_indigenous": "Measles, Indigenous",
    "measles_imported": "Measles, Imported",
    "meningococcal": "Meningococcal disease, All serogroups",
}

# How many recent MMWR weeks to fetch per disease.  Six weeks gives us
# a current-week reading plus a recent-month rolling window for the
# active-outbreak flag.
_LOOKBACK_WEEKS = 6


def _to_int(value: Any) -> int:
    """Coerce NNDSS m-fields (which may be None, '', or string ints) to int."""
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def _fetch_disease(label: str) -> List[Dict[str, Any]]:
    """Fetch the most recent N weeks for a single disease label in Wisconsin.

    Note on case sensitivity: the NNDSS dataset uses 'WISCONSIN' (uppercase)
    for records through 2024-W52 and 'Wisconsin' (mixed case) from 2025-W1
    onward. The query uses upper(states) to match both conventions, and
    orders by sort_order (a year-week composite int) so the newest records
    appear first regardless of which case convention is in use.

    SECURITY (v28.7): the disease label is interpolated into the Socrata
    `$where` clause. We enforce an explicit allowlist check against the
    internal _DISEASE_LABELS values AND route the label through
    utils/soql_safe.safe_eq() which doubles any embedded single quote
    per SoQL convention. Defense in depth so no Socrata-injection path
    opens up even if a future refactor lets the label flow in from
    config or user input.
    """
    allowed = set(_DISEASE_LABELS.values())
    if label not in allowed:
        logger.warning(
            f"NNDSS: refused fetch for non-allowlisted label {label!r}; "
            f"allowed labels are {sorted(allowed)}"
        )
        return []
    from utils.soql_safe import safe_eq
    params = {
        "$where": "upper(states)='WISCONSIN' AND " + safe_eq("label", label),
        "$select": "year,week,label,m1,m2,m3,m4",
        "$order": "sort_order DESC",
        "$limit": _LOOKBACK_WEEKS,
    }
    from utils.http_client import fetch_json, CircuitOpenError
    try:
        rows = fetch_json(
            source_id='cdc_nndss',
            url=NNDSS_ENDPOINT,
            params=params,
            headers={"User-Agent": _SCRAPER_UA},
            timeout=20,
        )
    except CircuitOpenError as exc:
        logger.warning(f"NNDSS fetch refused by circuit breaker for {label}: {exc}")
        return []
    if not isinstance(rows, list):
        logger.warning(f"NNDSS: unexpected response shape for {label}: {type(rows).__name__}")
        return []
    return rows


def _summarise(label_key: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute current-week + recent-4-week + YTD metrics from raw NNDSS rows."""
    if not rows:
        return {
            "disease": label_key,
            "available": False,
            "current_week_cases": 0,
            "recent_4wk_cases": 0,
            "ytd_cases": 0,
            "prior_ytd_cases": 0,
            "five_year_median": 0,
            "latest_week": None,
            "latest_year": None,
        }
    current = rows[0]
    recent_4 = rows[:4]
    return {
        "disease": label_key,
        "available": True,
        "current_week_cases": _to_int(current.get("m1")),
        "recent_4wk_cases": sum(_to_int(r.get("m1")) for r in recent_4),
        "ytd_cases": _to_int(current.get("m2")),
        "prior_ytd_cases": _to_int(current.get("m3")),
        "five_year_median": _to_int(current.get("m4")),
        "latest_week": int(current.get("week", 0)) if current.get("week") else None,
        "latest_year": int(current.get("year", 0)) if current.get("year") else None,
    }


def fetch_nndss_wi_communicable() -> Dict[str, Any]:
    """
    Fetch Wisconsin weekly case counts for tracked reportable diseases.

    Returns a structured dict with:
      - diseases: per-disease summary (measles_indigenous, measles_imported,
        meningococcal) with current-week / 4-week / YTD counts
      - outbreak_flags: derived boolean indicators used downstream
        (active_measles_outbreak granular flags + meningococcal_elevated)
      - report_date / last_updated / data_source provenance fields

    Results are cached for 7 days (NNDSS publishes weekly on Tuesdays).
    On any error, returns a fallback dict with available=False on every
    disease so callers can degrade gracefully.

    GRANULARITY: All values are statewide Wisconsin.  Applying them to a
    specific county represents a statewide signal, not local incidence.
    """
    cached = get_from_persistent_cache(NNDSS_CACHE_KEY, max_age_days=NNDSS_CACHE_DAYS)
    if cached:
        logger.info(
            f"NNDSS communicable disease data loaded from cache "
            f"(latest: {cached.get('report_date', 'unknown')})"
        )
        return cached

    # Cache-only enforcement: live HTTP is forbidden in the user dashboard
    # request path. The scheduler job refresh_all_cdc_nndss_communicable
    # must warm the cache. See utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("cdc_nndss_communicable")
        return _fallback()

    diseases: Dict[str, Dict[str, Any]] = {}
    any_success = False
    latest_year: Optional[int] = None
    latest_week: Optional[int] = None

    for key, label in _DISEASE_LABELS.items():
        try:
            rows = _fetch_disease(label)
            summary = _summarise(key, rows)
            diseases[key] = summary
            if summary["available"]:
                any_success = True
                if summary["latest_year"] and summary["latest_week"]:
                    yr, wk = summary["latest_year"], summary["latest_week"]
                    if latest_year is None or (yr, wk) > (latest_year, latest_week or 0):
                        latest_year, latest_week = yr, wk
        except Exception as exc:
            logger.error(f"NNDSS fetch error for {label}: {exc}")
            diseases[key] = _summarise(key, [])

    if not any_success:
        logger.warning("NNDSS: no diseases returned data; returning fallback")
        return _fallback()

    # Derive outbreak flags from the structured per-disease summaries.
    m_ind = diseases["measles_indigenous"]
    m_imp = diseases["measles_imported"]
    mening = diseases["meningococcal"]

    # Measles outbreak flags. Per CDC/CSTE convention, "active local
    # transmission", "elevated import pressure", and "year-to-date
    # elevated incidence" drive different response postures and must
    # not be conflated. We expose three orthogonal granular flags here
    # and keep the historical umbrella ``active_measles_outbreak`` as
    # the OR of all three for backward compatibility with older code.
    # New downstream code should consume the granular flags.
    active_local_transmission = bool(m_ind["recent_4wk_cases"] > 0)
    import_pressure_elevated = bool(m_imp["recent_4wk_cases"] > 2)
    ytd_elevated = bool(
        m_ind["ytd_cases"] > 0
        and m_ind["ytd_cases"] >= m_ind["prior_ytd_cases"]
    )
    active_measles_outbreak = bool(
        active_local_transmission or import_pressure_elevated or ytd_elevated
    )

    # meningococcal_elevated: any current-week case (rare disease, single
    # case is operationally significant), or YTD running ahead of prior YTD.
    meningococcal_elevated = bool(
        mening["current_week_cases"] > 0
        or mening["ytd_cases"] > mening["prior_ytd_cases"]
    )

    report_date = (
        f"{latest_year}-W{latest_week:02d}"
        if latest_year and latest_week else
        datetime.now().strftime("%Y-W%U")
    )

    result = {
        "report_url": NNDSS_DATASET_URL,
        "report_date": report_date,
        "latest_year": latest_year,
        "latest_week": latest_week,
        "last_updated": datetime.now().isoformat(),
        "data_source": "cdc_nndss",
        "data_source_label": "CDC NNDSS Weekly Data (data.cdc.gov/resource/x9gk-5huc)",
        "granularity_note": (
            "State-level Wisconsin counts. Applied statewide to all 72 "
            "counties; not a county-specific incidence rate."
        ),
        "diseases": diseases,
        "outbreak_flags": {
            # Granular measles flags - prefer these in new code.
            "active_local_transmission": active_local_transmission,
            "import_pressure_elevated": import_pressure_elevated,
            "ytd_elevated": ytd_elevated,
            # Umbrella OR-flag, kept for backward compatibility.
            "active_measles_outbreak": active_measles_outbreak,
            "meningococcal_elevated": meningococcal_elevated,
        },
    }

    logger.info(
        f"NNDSS fetched {report_date}: "
        f"measles_indig={m_ind['recent_4wk_cases']} (4wk), "
        f"measles_imp={m_imp['recent_4wk_cases']} (4wk), "
        f"mening_ytd={mening['ytd_cases']} vs prior {mening['prior_ytd_cases']}; "
        f"outbreak_flags={result['outbreak_flags']}"
    )
    set_in_persistent_cache(NNDSS_CACHE_KEY, result, expiry_days=NNDSS_CACHE_DAYS)
    return result


def _fallback() -> Dict[str, Any]:
    """Conservative fallback when the NNDSS API is unreachable."""
    return {
        "report_url": NNDSS_DATASET_URL,
        "report_date": datetime.now().strftime("%Y-W%U"),
        "latest_year": None,
        "latest_week": None,
        "last_updated": datetime.now().isoformat(),
        "data_source": "cdc_nndss_fallback",
        "data_source_label": "CDC NNDSS (fallback - API unavailable)",
        "granularity_note": (
            "State-level Wisconsin counts (fallback - data unavailable)."
        ),
        "diseases": {
            key: _summarise(key, []) for key in _DISEASE_LABELS
        },
        "outbreak_flags": {
            "active_local_transmission": False,
            "import_pressure_elevated": False,
            "ytd_elevated": False,
            "active_measles_outbreak": False,
            "meningococcal_elevated": False,
        },
    }


def get_measles_outbreak_flags() -> Dict[str, bool]:
    """Return the four measles outbreak flags from the latest NNDSS pull.

    Returns the three granular flags
    (``active_local_transmission``, ``import_pressure_elevated``,
    ``ytd_elevated``) plus the umbrella ``active_measles_outbreak``
    (OR of the three) for backward compatibility. All four default to
    False on fallback / no data, so callers can safely access keys
    without an existence check.
    """
    default = {
        "active_local_transmission": False,
        "import_pressure_elevated": False,
        "ytd_elevated": False,
        "active_measles_outbreak": False,
    }
    try:
        data = fetch_nndss_wi_communicable()
        flags = data.get("outbreak_flags", {}) or {}
        result = {k: bool(flags.get(k, False)) for k in default}
        # Cache-transition fallback: a payload written before the
        # granular-flags split has only the umbrella flag set. To avoid
        # silently dropping the outbreak signal until the next scheduler
        # refresh, infer the weakest granular flag (ytd_elevated) so the
        # multiplier still applies a conservative boost.
        if (
            result["active_measles_outbreak"]
            and not result["active_local_transmission"]
            and not result["import_pressure_elevated"]
            and not result["ytd_elevated"]
        ):
            result["ytd_elevated"] = True
        return result
    except Exception as exc:
        logger.error(f"get_measles_outbreak_flags failed: {exc}")
        return default


def get_active_measles_outbreak() -> bool:
    """
    Convenience accessor (kept for backward compatibility with older
    code). New callers should prefer ``get_measles_outbreak_flags()``
    so they can distinguish active local transmission from import
    pressure and year-to-date elevated incidence, which under CDC/
    CSTE protocols drive different response postures.

    Returns True if the umbrella ``active_measles_outbreak`` flag is
    set in the latest NNDSS pull (i.e. any of local transmission,
    elevated import pressure, or YTD elevated incidence). Returns
    False on fallback / no data.
    """
    return get_measles_outbreak_flags()["active_measles_outbreak"]
