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
    - Pertussis
    - Meningococcal disease, All serogroups

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
import requests
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

# Documented defaults that mirror config/risk_weights.yaml
# disease_alert_thresholds.pertussis. Used if the config block is missing
# or malformed (defensive fallback) so the surveillance fetch never crashes
# on a config error. The config block is the source of truth; this mirror
# only exists so the function is robust when the yaml has been hand-edited.
_PERTUSSIS_DEFAULT_THRESHOLDS = {
    "median_multiplier": 1.5,
    "min_cases_floor": 5,
    "method_label": (
        "CARA heuristic (1.5x 5-year weekly median, floor 5 cases); "
        "not a CSTE/CDC published threshold"
    ),
    "citation_status": (
        "uncited operational heuristic - see disease_alert_thresholds "
        "comment block"
    ),
}


def _get_pertussis_thresholds() -> Dict[str, Any]:
    """
    Read pertussis_elevated thresholds from config/risk_weights.yaml
    (disease_alert_thresholds.pertussis), with documented defaults as
    defensive fallback. See review finding H3 and the config block
    comments for rationale, citation status, and the planned
    Farrington/EARS replacement path.

    Returns a dict with median_multiplier (float), min_cases_floor (int),
    method_label (str), and citation_status (str). Invalid types or
    non-positive values fall back to the corresponding default and a
    warning is logged.
    """
    defaults = dict(_PERTUSSIS_DEFAULT_THRESHOLDS)
    try:
        from utils.config_manager import get_config_manager
        cfg = get_config_manager().config or {}
        block = (cfg.get('disease_alert_thresholds') or {}).get('pertussis') or {}
    except Exception as exc:
        logger.warning(
            f"NNDSS pertussis thresholds: could not load config, using defaults "
            f"({_PERTUSSIS_DEFAULT_THRESHOLDS}); reason: {exc}"
        )
        return defaults

    out = dict(defaults)
    try:
        m = float(block.get('median_multiplier', defaults['median_multiplier']))
        if m > 0:
            out['median_multiplier'] = m
        else:
            logger.warning(
                f"NNDSS pertussis: median_multiplier must be > 0, got {m}; "
                f"using default {defaults['median_multiplier']}"
            )
    except (TypeError, ValueError) as exc:
        logger.warning(
            f"NNDSS pertussis: median_multiplier invalid ({exc}); "
            f"using default {defaults['median_multiplier']}"
        )
    try:
        f = int(block.get('min_cases_floor', defaults['min_cases_floor']))
        if f >= 0:
            out['min_cases_floor'] = f
        else:
            logger.warning(
                f"NNDSS pertussis: min_cases_floor must be >= 0, got {f}; "
                f"using default {defaults['min_cases_floor']}"
            )
    except (TypeError, ValueError) as exc:
        logger.warning(
            f"NNDSS pertussis: min_cases_floor invalid ({exc}); "
            f"using default {defaults['min_cases_floor']}"
        )
    label = block.get('method_label')
    if isinstance(label, str) and label.strip():
        out['method_label'] = label
    cite = block.get('citation_status')
    if isinstance(cite, str) and cite.strip():
        out['citation_status'] = cite
    return out

# NNDSS disease label exactly as it appears in the dataset (case-sensitive).
# These labels are stable; CDC has used them since the NNDSS modernization.
_DISEASE_LABELS = {
    "measles_indigenous": "Measles, Indigenous",
    "measles_imported": "Measles, Imported",
    "pertussis": "Pertussis",
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

    SECURITY (review finding M3, 2026-05-20): the disease label is
    interpolated into the Socrata `$where` clause. To guarantee no
    Socrata-injection path exists even if a future refactor lets the
    label flow in from config or user input, this function enforces an
    explicit allowlist check against the internal _DISEASE_LABELS values
    AND defensively escapes single quotes before interpolation.
    """
    allowed = set(_DISEASE_LABELS.values())
    if label not in allowed:
        logger.warning(
            f"NNDSS: refused fetch for non-allowlisted label {label!r}; "
            f"allowed labels are {sorted(allowed)}"
        )
        return []
    # Defensive: Socrata uses single-quoted string literals in $where;
    # escape any embedded single quote by doubling it (SoQL convention).
    safe_label = label.replace("'", "''")
    params = {
        "$where": f"upper(states)='WISCONSIN' AND label='{safe_label}'",
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
        pertussis, meningococcal) with current-week / 4-week / YTD counts
      - outbreak_flags: derived boolean indicators used downstream
        (active_measles_outbreak, pertussis_elevated, meningococcal_elevated)
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
    pert = diseases["pertussis"]
    mening = diseases["meningococcal"]

    # Measles outbreak flags. Per CDC/CSTE convention, "active local
    # transmission", "elevated import pressure", and "year-to-date
    # elevated incidence" drive different response postures and must
    # not be conflated. We expose three orthogonal granular flags here
    # and keep the historical umbrella ``active_measles_outbreak`` as
    # the OR of all three for backward compatibility with older code.
    # New downstream code should consume the granular flags.
    #
    # active_local_transmission: any indigenous measles case in the last
    #     4 reported weeks. This is the only flag that signals current
    #     local community spread and triggers an acute outbreak response.
    # import_pressure_elevated: more than 2 imported cases in the last
    #     4 reported weeks. Sustained import pressure raises community-
    #     spread risk but is NOT itself an active outbreak.
    # ytd_elevated: any indigenous YTD case AND YTD count at or above
    #     the prior year. Year-level vulnerability signal, not acute.
    #     Handles the common case where NNDSS m1 (current week) is
    #     null/zero for the most recent weeks but m2 (YTD) shows active
    #     circulation earlier in the year.
    active_local_transmission = bool(m_ind["recent_4wk_cases"] > 0)
    import_pressure_elevated = bool(m_imp["recent_4wk_cases"] > 2)
    ytd_elevated = bool(
        m_ind["ytd_cases"] > 0
        and m_ind["ytd_cases"] >= m_ind["prior_ytd_cases"]
    )
    active_measles_outbreak = bool(
        active_local_transmission or import_pressure_elevated or ytd_elevated
    )

    # pertussis_elevated: CARA-specific heuristic alert (NOT a CSTE- or
    # CDC-published outbreak threshold). Thresholds are externalized to
    # config/risk_weights.yaml disease_alert_thresholds.pertussis so the
    # assumptions are inspectable and tunable without code changes.
    # See that config block for the rationale, citation status, and the
    # follow-up plan (replace with Farrington/EARS aberration detector
    # if the multi-year per-week distribution becomes available). The
    # method_label and citation_status are echoed onto the result dict
    # below so renderers can surface the caveat to users.
    pertussis_thresholds = _get_pertussis_thresholds()
    pertussis_median_multiplier = pertussis_thresholds["median_multiplier"]
    pertussis_min_cases_floor = pertussis_thresholds["min_cases_floor"]
    pertussis_alert_floor = max(
        pertussis_min_cases_floor,
        int(round(pert["five_year_median"] * pertussis_median_multiplier))
    )
    pertussis_elevated = bool(
        pert["five_year_median"] > 0
        and pert["current_week_cases"] >= pertussis_alert_floor
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
            "pertussis_elevated": pertussis_elevated,
            "meningococcal_elevated": meningococcal_elevated,
        },
        # Per review finding H3: the pertussis_elevated flag is a CARA
        # heuristic, not a CSTE/CDC published threshold. Surface the
        # current method label, citation status, and the exact alert
        # floor that fired (or would fire) for this report so renderers
        # can show the caveat to users.
        "pertussis_alert_method": {
            "median_multiplier": pertussis_median_multiplier,
            "min_cases_floor": pertussis_min_cases_floor,
            "alert_floor_cases": pertussis_alert_floor,
            "five_year_median": pert["five_year_median"],
            "current_week_cases": pert["current_week_cases"],
            "method_label": pertussis_thresholds["method_label"],
            "citation_status": pertussis_thresholds["citation_status"],
        },
    }

    logger.info(
        f"NNDSS fetched {report_date}: "
        f"measles_indig={m_ind['recent_4wk_cases']} (4wk), "
        f"measles_imp={m_imp['recent_4wk_cases']} (4wk), "
        f"pertussis={pert['current_week_cases']}/wk vs median {pert['five_year_median']}, "
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
        "pertussis_alert_method": {
            **_PERTUSSIS_DEFAULT_THRESHOLDS,
            "alert_floor_cases": None,
            "five_year_median": None,
            "current_week_cases": None,
        },
        "outbreak_flags": {
            "active_local_transmission": False,
            "import_pressure_elevated": False,
            "ytd_elevated": False,
            "active_measles_outbreak": False,
            "pertussis_elevated": False,
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
