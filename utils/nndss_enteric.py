"""
CDC NNDSS Wisconsin Enteric + Legionella Surveillance

Pulls Wisconsin weekly case counts for enteric/waterborne reportable
diseases plus legionellosis from the CDC NNDSS Socrata API. Produces
two outbreak-flag dicts consumed by utils/disease_surveillance.py:

    get_enteric_outbreak_flags()    - composite GI cluster signal
    get_legionella_outbreak_flags() - building-water cluster signal

Tracked agents (enteric composite):
    - Salmonellosis (excluding Salmonella Typhi infection)
    - Shiga toxin-producing Escherichia coli (STEC)
    - Shigellosis
    - Campylobacteriosis
    - Cryptosporidiosis
    - Giardiasis

Norovirus is folded into the enteric composite per design decision (#3):
NNDSS does not list norovirus as an individually nationally notifiable
condition, so the composite signal is the practical proxy. A future
extension could add NoroSTAT regional data here.

Legionellosis is reported separately because the PHEP response posture
(building water management, cooling tower investigation) differs from
foodborne/waterborne enteric response.

Granularity: statewide Wisconsin per design decision (#2).

Cache-only invariant: request-path callers must never trigger live HTTP.
Live fetches occur exclusively in scheduler job refresh_all_nndss_enteric.

Endpoint: https://data.cdc.gov/resource/x9gk-5huc.json (same Socrata
dataset used by utils/nndss_communicable.py for measles/pertussis).
"""

from __future__ import annotations

import logging
import requests
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from utils.persistent_cache import get_from_persistent_cache, set_in_persistent_cache

logger = logging.getLogger(__name__)

NNDSS_ENDPOINT = "https://data.cdc.gov/resource/x9gk-5huc.json"
CACHE_KEY = "nndss_enteric_wi_v1"
CACHE_DAYS = 7
HTTP_TIMEOUT = 30
_UA = "CARA-WI-PublicHealth/1.0 (contact: github.com/jdn63)"

# Enteric agents tracked in the composite. NNDSS condition labels are
# case-sensitive and have changed wording over the years; prefixes are
# matched defensively against the label field. If CDC renames a
# condition, update the key here and the scheduler will repopulate the
# cache on its next run.
_ENTERIC_LABELS = {
    "salmonellosis": "Salmonellosis",
    "stec": "Shiga toxin-producing Escherichia coli (STEC)",
    "shigellosis": "Shigellosis",
    "campylobacteriosis": "Campylobacteriosis",
    "cryptosporidiosis": "Cryptosporidiosis",
    "giardiasis": "Giardiasis",
}
_LEGIONELLA_LABEL = "Legionellosis"

_DEFAULT_THRESHOLDS = {
    "enteric": {
        "agent_elevated_multiplier": 1.5,   # 4-week count vs 5-year weekly median * 4
        "cluster_min_elevated_agents": 2,
        "tier_boosts": {"none": 0.0, "elevated": 0.10, "cluster": 0.25},
    },
    "legionella": {
        "elevated_multiplier": 2.0,         # 4-week count vs 5-year weekly median * 4
        "min_cases_floor": 4,
        "tier_boosts": {"none": 0.0, "active": 0.20},
    },
}


def _thresholds() -> Dict[str, Any]:
    out = {
        "enteric": dict(_DEFAULT_THRESHOLDS["enteric"]),
        "legionella": dict(_DEFAULT_THRESHOLDS["legionella"]),
    }
    out["enteric"]["tier_boosts"] = dict(_DEFAULT_THRESHOLDS["enteric"]["tier_boosts"])
    out["legionella"]["tier_boosts"] = dict(_DEFAULT_THRESHOLDS["legionella"]["tier_boosts"])
    try:
        from utils.config_manager import get_config_manager
        cfg = get_config_manager().config or {}
        block = (cfg.get("disease_alert_thresholds") or {})
        ent = block.get("enteric") or {}
        leg = block.get("legionella") or {}
        for k in ("agent_elevated_multiplier",):
            v = ent.get(k)
            if isinstance(v, (int, float)) and v > 0:
                out["enteric"][k] = float(v)
        for k in ("cluster_min_elevated_agents",):
            v = ent.get(k)
            if isinstance(v, int) and v > 0:
                out["enteric"][k] = int(v)
        ent_boosts = ent.get("tier_boosts") or {}
        for k in out["enteric"]["tier_boosts"]:
            v = ent_boosts.get(k)
            if isinstance(v, (int, float)) and 0.0 <= float(v) <= 0.40:
                out["enteric"]["tier_boosts"][k] = float(v)
        for k in ("elevated_multiplier",):
            v = leg.get(k)
            if isinstance(v, (int, float)) and v > 0:
                out["legionella"][k] = float(v)
        for k in ("min_cases_floor",):
            v = leg.get(k)
            if isinstance(v, int) and v >= 0:
                out["legionella"][k] = int(v)
        leg_boosts = leg.get("tier_boosts") or {}
        for k in out["legionella"]["tier_boosts"]:
            v = leg_boosts.get(k)
            if isinstance(v, (int, float)) and 0.0 <= float(v) <= 0.40:
                out["legionella"]["tier_boosts"][k] = float(v)
    except Exception as exc:
        logger.warning(f"enteric/legionella thresholds: config unavailable, using defaults ({exc})")
    return out


def _to_int(v: Any) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def _fetch_disease(label: str) -> List[Dict[str, Any]]:
    """Fetch most-recent NNDSS rows for one disease label (Wisconsin only)."""
    params = {
        "$where": f"states='WI' AND label='{label}'",
        "$order": "year DESC, week DESC",
        "$limit": 10,
    }
    try:
        r = requests.get(
            NNDSS_ENDPOINT,
            params=params,
            timeout=HTTP_TIMEOUT,
            headers={"User-Agent": _UA, "Accept": "application/json"},
        )
        if r.status_code != 200:
            logger.warning(f"NNDSS enteric: HTTP {r.status_code} for {label}")
            return []
        rows = r.json()
        return rows if isinstance(rows, list) else []
    except Exception as exc:
        logger.warning(f"NNDSS enteric fetch failed for {label}: {exc}")
        return []


def _summarise(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {
            "available": False,
            "current_week_cases": 0,
            "recent_4wk_cases": 0,
            "ytd_cases": 0,
            "five_year_median": 0,
            "latest_week": None,
            "latest_year": None,
        }
    current = rows[0]
    return {
        "available": True,
        "current_week_cases": _to_int(current.get("m1")),
        "recent_4wk_cases": sum(_to_int(r.get("m1")) for r in rows[:4]),
        "ytd_cases": _to_int(current.get("m2")),
        "five_year_median": _to_int(current.get("m4")),
        "latest_week": int(current.get("week", 0)) if current.get("week") else None,
        "latest_year": int(current.get("year", 0)) if current.get("year") else None,
    }


def fetch_nndss_enteric_wi() -> Dict[str, Any]:
    """Live fetch of WI enteric + legionellosis NNDSS rows. Scheduler only."""
    cached = get_from_persistent_cache(CACHE_KEY, max_age_days=CACHE_DAYS)
    if cached:
        logger.info(
            f"NNDSS enteric loaded from cache "
            f"(report={cached.get('report_date', 'unknown')})"
        )
        return cached

    from utils.request_context import is_cache_only_mode, record_blocked_fetch
    if is_cache_only_mode():
        record_blocked_fetch("nndss_enteric")
        return _fallback()

    agents: Dict[str, Dict[str, Any]] = {}
    latest_year: Optional[int] = None
    latest_week: Optional[int] = None
    any_success = False

    for key, label in _ENTERIC_LABELS.items():
        summary = _summarise(_fetch_disease(label))
        summary["disease"] = key
        summary["nndss_label"] = label
        agents[key] = summary
        if summary["available"]:
            any_success = True
            if summary["latest_year"] and summary["latest_week"]:
                yr, wk = summary["latest_year"], summary["latest_week"]
                if latest_year is None or (yr, wk) > (latest_year, latest_week or 0):
                    latest_year, latest_week = yr, wk

    legionella_summary = _summarise(_fetch_disease(_LEGIONELLA_LABEL))
    legionella_summary["disease"] = "legionellosis"
    legionella_summary["nndss_label"] = _LEGIONELLA_LABEL
    if legionella_summary["available"]:
        any_success = True

    if not any_success:
        logger.warning("NNDSS enteric: no agents returned data; using fallback")
        return _fallback()

    report_date = (
        f"{latest_year}-W{latest_week:02d}"
        if latest_year and latest_week
        else datetime.now(timezone.utc).strftime("%Y-W%U")
    )
    result = {
        "report_date": report_date,
        "latest_year": latest_year,
        "latest_week": latest_week,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "data_source": "cdc_nndss_enteric",
        "data_source_label": "CDC NNDSS Weekly Data (enteric + legionellosis subset)",
        "source_url": "https://data.cdc.gov/Public-Health-Surveillance/NNDSS-Weekly-Data/x9gk-5huc",
        "granularity_note": (
            "State-level Wisconsin counts. Applied statewide to all 72 counties; "
            "not a county-specific incidence rate."
        ),
        "enteric_agents": agents,
        "legionella": legionella_summary,
    }
    set_in_persistent_cache(CACHE_KEY, result, expiry_days=CACHE_DAYS)
    elevated_count = sum(
        1 for k, s in agents.items()
        if s["available"] and s["five_year_median"] > 0
        and s["recent_4wk_cases"] >= 1.5 * (s["five_year_median"] * 4)
    )
    logger.info(
        f"NNDSS enteric fetched {report_date}: {len(agents)} agents tracked, "
        f"{elevated_count} elevated; legionella 4wk={legionella_summary['recent_4wk_cases']} "
        f"(median {legionella_summary['five_year_median']})"
    )
    return result


def _fallback() -> Dict[str, Any]:
    empty = lambda key, label: {
        "disease": key,
        "nndss_label": label,
        "available": False,
        "current_week_cases": 0,
        "recent_4wk_cases": 0,
        "ytd_cases": 0,
        "five_year_median": 0,
        "latest_week": None,
        "latest_year": None,
    }
    return {
        "report_date": datetime.now(timezone.utc).strftime("%Y-W%U"),
        "latest_year": None,
        "latest_week": None,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "data_source": "cdc_nndss_enteric_fallback",
        "data_source_label": "CDC NNDSS enteric (fallback - data unavailable)",
        "source_url": "https://data.cdc.gov/Public-Health-Surveillance/NNDSS-Weekly-Data/x9gk-5huc",
        "granularity_note": "State-level Wisconsin counts (fallback - data unavailable).",
        "enteric_agents": {k: empty(k, lbl) for k, lbl in _ENTERIC_LABELS.items()},
        "legionella": empty("legionellosis", _LEGIONELLA_LABEL),
    }


def get_enteric_outbreak_flags() -> Dict[str, Any]:
    """
    Composite enteric/waterborne outbreak flag for the
    infectious_disease Acute path.

    Tier rule:
        none      - no individually elevated agent
        elevated  - at least 1 agent's 4-week count >= multiplier * (median * 4)
        cluster   - >= cluster_min_elevated_agents agents elevated concurrently

    Norovirus is folded into the composite per design decision (#3): a
    cluster of any enteric agent reflects the same PHEP response posture
    (foodborne/waterborne outbreak investigation) regardless of pathogen.
    """
    try:
        data = fetch_nndss_enteric_wi()
    except Exception as exc:
        logger.error(f"get_enteric_outbreak_flags failed: {exc}")
        data = _fallback()

    thr = _thresholds()["enteric"]
    agents_payload: Dict[str, Dict[str, Any]] = {}
    elevated: List[str] = []
    for key, summary in (data.get("enteric_agents") or {}).items():
        baseline_4wk = float(summary.get("five_year_median", 0)) * 4.0
        recent_4wk = int(summary.get("recent_4wk_cases", 0))
        is_elevated = bool(
            summary.get("available")
            and baseline_4wk > 0
            and recent_4wk >= thr["agent_elevated_multiplier"] * baseline_4wk
        )
        if is_elevated:
            elevated.append(key)
        agents_payload[key] = {
            "current_4wk": recent_4wk,
            "baseline_4wk": round(baseline_4wk, 1),
            "elevated": is_elevated,
            "available": bool(summary.get("available")),
        }

    if len(elevated) >= thr["cluster_min_elevated_agents"]:
        tier = "cluster"
    elif len(elevated) >= 1:
        tier = "elevated"
    else:
        tier = "none"

    boost = thr["tier_boosts"].get(tier, 0.0)
    detail_parts = []
    if elevated:
        detail_parts.append(f"Elevated agents ({len(elevated)}): " + ", ".join(elevated))
    else:
        detail_parts.append("All tracked enteric agents within baseline 4-week range")
    detail_parts.append("Norovirus folded into composite (no individual NNDSS feed)")

    return {
        "active": tier != "none",
        "tier": tier,
        "boost": boost,
        "agents_elevated": elevated,
        "agents": agents_payload,
        "source": data.get("data_source", "cdc_nndss_enteric"),
        "source_label": data.get(
            "data_source_label",
            "CDC NNDSS Weekly Data (enteric + legionellosis subset)",
        ),
        "source_url": data.get("source_url", ""),
        "detail": "; ".join(detail_parts),
        "signal_scope": "statewide_wisconsin",
        "last_updated": data.get("last_updated"),
        "report_date": data.get("report_date"),
    }


def get_legionella_outbreak_flags() -> Dict[str, Any]:
    """
    Legionellosis outbreak flag for the infectious_disease Acute path.

    Fires when WI 4-week case count exceeds elevated_multiplier *
    (5-year weekly median * 4) AND the count is at least
    min_cases_floor. The floor prevents the flag from firing on
    statistical noise when the median is near zero.
    """
    try:
        data = fetch_nndss_enteric_wi()
    except Exception as exc:
        logger.error(f"get_legionella_outbreak_flags failed: {exc}")
        data = _fallback()

    thr = _thresholds()["legionella"]
    leg = data.get("legionella") or {}
    recent_4wk = int(leg.get("recent_4wk_cases", 0))
    baseline_4wk = float(leg.get("five_year_median", 0)) * 4.0
    floor = int(thr["min_cases_floor"])

    active = bool(
        leg.get("available")
        and baseline_4wk > 0
        and recent_4wk >= floor
        and recent_4wk >= thr["elevated_multiplier"] * baseline_4wk
    )
    tier = "active" if active else "none"
    boost = thr["tier_boosts"].get(tier, 0.0)

    detail = (
        f"WI 4-week legionellosis cases: {recent_4wk} "
        f"(baseline 4-week {baseline_4wk:.1f}, "
        f"trigger >= {thr['elevated_multiplier']}x baseline with floor {floor})"
    )

    return {
        "active": active,
        "tier": tier,
        "boost": boost,
        "wi_recent_4wk_cases": recent_4wk,
        "wi_baseline_4wk": round(baseline_4wk, 1),
        "elevated_multiplier": thr["elevated_multiplier"],
        "min_cases_floor": floor,
        "source": "cdc_nndss_legionellosis",
        "source_label": "CDC NNDSS Weekly Data (Legionellosis)",
        "source_url": data.get("source_url", ""),
        "detail": detail,
        "signal_scope": "statewide_wisconsin",
        "last_updated": data.get("last_updated"),
        "report_date": data.get("report_date"),
    }
