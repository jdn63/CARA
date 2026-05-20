"""
CDC NHSN Wisconsin Hospital Respiratory Capacity

Fetches Wisconsin weekly hospital capacity and respiratory admission data
from the CDC National Healthcare Safety Network (NHSN) Hospital Respiratory
Data (HRD) Metrics dataset via the Socrata open-data API on data.cdc.gov.
No API key is required.

Dataset:  Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction
Endpoint: https://data.cdc.gov/resource/ua7e-t2fy.json
Coverage: All US states + territories, weekly, including ICU bed counts,
          ICU occupancy, and confirmed COVID/Flu/RSV hospitalizations and
          ICU patients
Update:   Weekly (typically Wednesdays for the prior week)
History:  November 2024 onward (replaces HHS Protect which closed May 2024)

This is the only public machine-readable source for Wisconsin hospital
capacity following the closure of HHS Protect.  The WI DHS / WHA
Information Center holds richer county-level and facility-level data,
but those feeds require formal HERC partner agreements and are not
publicly accessible.

Granularity note: NHSN HRD is jurisdiction-level (state).  Wisconsin
ICU occupancy and respiratory hospitalization counts are statewide
totals applied uniformly to all 72 counties as a statewide healthcare
system strain signal, not a county-specific capacity reading.

References:
  https://www.cdc.gov/nhsn/
  https://data.cdc.gov/Public-Health-Surveillance/
  Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

NHSN_ENDPOINT = "https://data.cdc.gov/resource/ua7e-t2fy.json"
NHSN_DATASET_URL = (
    "https://data.cdc.gov/Public-Health-Surveillance/"
    "Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy"
)
NHSN_CACHE_KEY = "nhsn_wi_hospital_v1"
NHSN_CACHE_DAYS = 7

_SCRAPER_UA = "CARA-WI-PublicHealth/1.0 (contact: github.com/jdn63)"

# How many recent weeks to pull for trend analysis (current + 3 prior).
_LOOKBACK_WEEKS = 4


def _to_float(value: Any) -> float:
    """Coerce NHSN numeric fields to float, returning 0.0 on missing/invalid."""
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _safe_pct(numerator: float, denominator: float) -> Optional[float]:
    """Return numerator/denominator as a fraction in [0,1], or None if denominator is 0."""
    if denominator <= 0:
        return None
    return max(0.0, min(1.0, numerator / denominator))


def _trend(current: float, prior: float) -> str:
    if prior <= 0:
        return "stable"
    change = (current - prior) / prior * 100
    if change >= 15:
        return "increasing"
    if change <= -15:
        return "decreasing"
    return "stable"


def fetch_nhsn_wi_hospital() -> Dict[str, Any]:
    """
    Fetch Wisconsin hospital respiratory capacity data from CDC NHSN HRD.

    Returns a structured dict with:
      - current_week: ICU beds, ICU occupancy %, current C19/Flu/RSV
        hospitalized patients, ICU patients, weekly new admissions
      - prior_week: same fields for the immediately prior week
      - trends: per-pathogen trend direction (increasing/stable/decreasing)
      - risk_indicators: normalized 0-1 scores for ICU strain and
        respiratory hospitalization burden
      - report_date / last_updated / data_source provenance fields

    Results are cached for 7 days (NHSN publishes weekly).
    On any error, returns a fallback dict with available=False.

    GRANULARITY: All values are statewide Wisconsin totals.  Applying them
    to a specific county represents a statewide healthcare-system signal,
    not a local capacity reading.
    """
    cached = get_from_persistent_cache(NHSN_CACHE_KEY, max_age_days=NHSN_CACHE_DAYS)
    if cached:
        logger.info(
            f"NHSN hospital data loaded from cache "
            f"(week: {cached.get('report_date', 'unknown')})"
        )
        return cached

    # Cache-only enforcement: live HTTP is forbidden in the user dashboard
    # request path. The scheduler job refresh_all_cdc_nhsn_hospital must
    # warm the cache. See utils/request_context.py.
    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("cdc_nhsn_hospital")
        return _fallback()

    try:
        from utils.http_client import fetch_json, CircuitOpenError
        try:
            rows = fetch_json(
                source_id='cdc_nhsn',
                url=NHSN_ENDPOINT,
                params={
                    "jurisdiction": "WI",
                    "$order": "weekendingdate DESC",
                    "$limit": _LOOKBACK_WEEKS,
                },
                headers={"User-Agent": _SCRAPER_UA},
                timeout=20,
            )
        except CircuitOpenError as exc:
            logger.warning(f"NHSN fetch refused by circuit breaker: {exc}")
            return _fallback()

        if not isinstance(rows, list) or not rows:
            logger.warning("NHSN API: empty or invalid response for WI")
            return _fallback()

        current = rows[0]
        prior = rows[1] if len(rows) > 1 else current

        week_end = (current.get("weekendingdate") or "").split("T")[0]

        # Current week capacity metrics
        icu_beds = _to_float(current.get("numicubeds"))
        icu_occ = _to_float(current.get("numicubedsocc"))
        icu_occ_pct = _safe_pct(icu_occ, icu_beds)

        # Respiratory hospitalization counts (current census)
        c19_hosp = _to_float(current.get("totalconfc19hosppats"))
        flu_hosp = _to_float(current.get("totalconffluhosppats"))
        rsv_hosp = _to_float(current.get("totalconfrsvhosppats"))
        total_resp_hosp = c19_hosp + flu_hosp + rsv_hosp

        # Respiratory ICU patients (current census)
        c19_icu = _to_float(current.get("totalconfc19icupats"))
        flu_icu = _to_float(current.get("totalconffluicupats"))
        rsv_icu = _to_float(current.get("totalconfrsvicupats"))
        total_resp_icu = c19_icu + flu_icu + rsv_icu

        # Weekly new admissions
        c19_newadm = _to_float(current.get("totalconfc19newadm"))
        flu_newadm = _to_float(current.get("totalconfflunewadm"))
        rsv_newadm = _to_float(current.get("totalconfrsvnewadm"))
        total_newadm = c19_newadm + flu_newadm + rsv_newadm

        # Prior-week values for trend
        prior_c19_newadm = _to_float(prior.get("totalconfc19newadm"))
        prior_flu_newadm = _to_float(prior.get("totalconfflunewadm"))
        prior_rsv_newadm = _to_float(prior.get("totalconfrsvnewadm"))
        prior_total_newadm = prior_c19_newadm + prior_flu_newadm + prior_rsv_newadm
        prior_icu_occ_pct = _safe_pct(
            _to_float(prior.get("numicubedsocc")),
            _to_float(prior.get("numicubeds")),
        )

        # Risk indicators normalized 0-1
        # ICU strain: occupancy above 75% is strained, above 90% is critical
        if icu_occ_pct is None:
            icu_strain = 0.0
        elif icu_occ_pct < 0.60:
            icu_strain = icu_occ_pct / 0.60 * 0.4
        elif icu_occ_pct < 0.75:
            icu_strain = 0.4 + (icu_occ_pct - 0.60) / 0.15 * 0.2
        elif icu_occ_pct < 0.90:
            icu_strain = 0.6 + (icu_occ_pct - 0.75) / 0.15 * 0.3
        else:
            icu_strain = min(1.0, 0.9 + (icu_occ_pct - 0.90) / 0.10 * 0.1)

        # Respiratory admission burden: scale against historical WI weekly
        # peaks (~600 combined respiratory new admissions during severe
        # flu/RSV/COVID surges per HHS Protect archives).
        admission_burden = min(1.0, total_newadm / 600.0)

        result = {
            "report_url": NHSN_DATASET_URL,
            "report_date": week_end,
            "last_updated": datetime.now().isoformat(),
            "data_source": "cdc_nhsn_hrd",
            "data_source_label": "CDC NHSN Hospital Respiratory Data (data.cdc.gov/resource/ua7e-t2fy)",
            "granularity_note": (
                "State-level Wisconsin totals. Applied statewide to all "
                "72 counties; not a county-specific capacity reading."
            ),
            "current_week": {
                "week_ending": week_end,
                "icu_beds_total": int(icu_beds),
                "icu_beds_occupied": int(icu_occ),
                "icu_occupancy_pct": round(icu_occ_pct, 3) if icu_occ_pct is not None else None,
                "covid19_hospitalized": int(c19_hosp),
                "influenza_hospitalized": int(flu_hosp),
                "rsv_hospitalized": int(rsv_hosp),
                "total_respiratory_hospitalized": int(total_resp_hosp),
                "covid19_icu": int(c19_icu),
                "influenza_icu": int(flu_icu),
                "rsv_icu": int(rsv_icu),
                "total_respiratory_icu": int(total_resp_icu),
                "covid19_new_admissions": int(c19_newadm),
                "influenza_new_admissions": int(flu_newadm),
                "rsv_new_admissions": int(rsv_newadm),
                "total_respiratory_new_admissions": int(total_newadm),
            },
            "prior_week": {
                "total_respiratory_new_admissions": int(prior_total_newadm),
                "icu_occupancy_pct": round(prior_icu_occ_pct, 3) if prior_icu_occ_pct is not None else None,
            },
            "trends": {
                "covid19_admissions": _trend(c19_newadm, prior_c19_newadm),
                "influenza_admissions": _trend(flu_newadm, prior_flu_newadm),
                "rsv_admissions": _trend(rsv_newadm, prior_rsv_newadm),
                "total_respiratory_admissions": _trend(total_newadm, prior_total_newadm),
                "icu_occupancy": _trend(
                    icu_occ_pct or 0.0, prior_icu_occ_pct or 0.0
                ),
            },
            "risk_indicators": {
                "icu_strain": round(icu_strain, 3),
                "respiratory_admission_burden": round(admission_burden, 3),
                "combined_strain": round(min(1.0, icu_strain * 0.6 + admission_burden * 0.4), 3),
                "confidence": 0.85,
            },
        }

        logger.info(
            f"NHSN fetched week {week_end}: "
            f"ICU {icu_occ_pct*100:.1f}% occupied ({int(icu_occ)}/{int(icu_beds)}) "
            f"[{result['trends']['icu_occupancy']}], "
            f"resp admissions {int(total_newadm)}/wk "
            f"(C19={int(c19_newadm)}, Flu={int(flu_newadm)}, RSV={int(rsv_newadm)}) "
            f"[{result['trends']['total_respiratory_admissions']}]"
            if icu_occ_pct is not None else
            f"NHSN fetched week {week_end}: ICU data missing; "
            f"resp admissions {int(total_newadm)}/wk"
        )
        set_in_persistent_cache(NHSN_CACHE_KEY, result, expiry_days=NHSN_CACHE_DAYS)
        return result

    except Exception as exc:
        logger.error(f"Error fetching NHSN hospital data: {exc}")
        return _fallback()


def _fallback() -> Dict[str, Any]:
    """Conservative fallback when the NHSN API is unreachable."""
    return {
        "report_url": NHSN_DATASET_URL,
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().isoformat(),
        "data_source": "cdc_nhsn_fallback",
        "data_source_label": "CDC NHSN HRD (fallback - API unavailable)",
        "granularity_note": (
            "State-level Wisconsin totals (fallback - data unavailable)."
        ),
        "current_week": {
            "week_ending": None,
            "icu_beds_total": 0,
            "icu_beds_occupied": 0,
            "icu_occupancy_pct": None,
            "covid19_hospitalized": 0,
            "influenza_hospitalized": 0,
            "rsv_hospitalized": 0,
            "total_respiratory_hospitalized": 0,
            "covid19_icu": 0,
            "influenza_icu": 0,
            "rsv_icu": 0,
            "total_respiratory_icu": 0,
            "covid19_new_admissions": 0,
            "influenza_new_admissions": 0,
            "rsv_new_admissions": 0,
            "total_respiratory_new_admissions": 0,
        },
        "prior_week": {
            "total_respiratory_new_admissions": 0,
            "icu_occupancy_pct": None,
        },
        "trends": {
            "covid19_admissions": "stable",
            "influenza_admissions": "stable",
            "rsv_admissions": "stable",
            "total_respiratory_admissions": "stable",
            "icu_occupancy": "stable",
        },
        "risk_indicators": {
            "icu_strain": 0.4,
            "respiratory_admission_burden": 0.3,
            "combined_strain": 0.36,
            "confidence": 0.30,
        },
    }
