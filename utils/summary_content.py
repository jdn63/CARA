"""Loader for the plain-language Summary page content layer.

Reads `data/summary_content/summary_content.yaml` and assembles the
ranked, plain-language risk cards the Summary page renders for
jurisdiction, EM county, and regional (HERC/WEM) views.

Design points:
- Content lives in YAML (not Python) so subject-matter-expert reviewers
  can edit the words without touching code.
- Nothing here changes any score, weight, or threshold. The numeric
  scores are produced by the risk model; this module only consumes them
  read-only and pairs each with authored plain-language copy.
- No network calls. This module only reads a local YAML file, so it is
  safe on the cache-only request path.
- The loader is cheap and cached in-process so the request path stays
  fast. It degrades gracefully (generic fallback copy) when the YAML is
  missing a domain or is malformed, and never raises into the request.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml

from utils.summary_signals import derive_local_signals


logger = logging.getLogger(__name__)

_CONTENT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "summary_content",
    "summary_content.yaml",
)

VALID_DISCIPLINES = ("public_health", "em")

# Risk-level thresholds, matched to the rest of the app (badge logic in
# the dashboard and prior summary templates): > 0.6 High, > 0.3 Moderate,
# otherwise Low.
_HIGH_THRESHOLD = 0.6
_MODERATE_THRESHOLD = 0.3

_FALLBACK_PAGE = {
    "purpose": (
        "This summary highlights the hazards that pose the greatest risk so "
        "your team can focus planning where it matters most."
    ),
    "scale_note": (
        "Each hazard is scored from 0.00 to 1.00. A score closer to 0 means "
        "lower relative risk; a score closer to 1 means higher relative risk."
    ),
    "draft_banner": (
        "Draft pending expert review. The plain-language descriptions below "
        "were drafted by the CARA team and are awaiting subject-matter-expert "
        "review. The numeric scores are produced by CARA's data model."
    ),
}


@lru_cache(maxsize=1)
def _load_content() -> Dict[str, Any]:
    try:
        with open(_CONTENT_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except FileNotFoundError:
        logger.warning(f"Summary content file not found at {_CONTENT_PATH}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load summary content from {_CONTENT_PATH}: {e}")
        return {}


def _normalize_discipline(discipline: Optional[str]) -> str:
    if discipline == "em":
        return "em"
    return "public_health"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def get_summary_page_meta(discipline: Optional[str]) -> Dict[str, str]:
    """Return page-level copy: purpose statement, scale note, draft banner."""
    discipline = _normalize_discipline(discipline)
    page = _safe_dict(_load_content().get("page"))
    if discipline == "em":
        purpose = page.get("purpose_em") or page.get("purpose_public_health")
    else:
        purpose = page.get("purpose_public_health") or page.get("purpose_em")
    return {
        "purpose": str(purpose).strip() if purpose else _FALLBACK_PAGE["purpose"],
        "scale_note": str(page.get("scale_note") or _FALLBACK_PAGE["scale_note"]).strip(),
        "draft_banner": str(page.get("draft_banner") or _FALLBACK_PAGE["draft_banner"]).strip(),
    }


def _resolve_domain_content(domain: str, discipline: str) -> Dict[str, Any]:
    """Merge shared defaults with the discipline override block for a domain."""
    domains = _safe_dict(_load_content().get("domains"))
    block = _safe_dict(domains.get(domain))

    label = str(block.get("label") or domain.replace("_", " ").title())
    note = block.get("note")

    why = block.get("why")
    impacts = block.get("impacts")
    populations = block.get("populations")

    override = _safe_dict(block.get(discipline))
    if override.get("why"):
        why = override.get("why")
    if override.get("impacts"):
        impacts = override.get("impacts")
    if isinstance(override.get("populations"), list) and override.get("populations"):
        populations = override.get("populations")

    if not isinstance(populations, list):
        populations = []

    return {
        "label": label,
        "note": str(note).strip() if note else None,
        "why": str(why).strip() if why else "",
        "impacts": str(impacts).strip() if impacts else "",
        "populations": [str(p).strip() for p in populations if p],
    }


def _level_for(score: float) -> Dict[str, str]:
    if score > _HIGH_THRESHOLD:
        return {"level": "High", "badge": "danger"}
    if score > _MODERATE_THRESHOLD:
        return {"level": "Moderate", "badge": "warning"}
    return {"level": "Low", "badge": "success"}


def build_top_risk_cards(
    scores: Dict[str, Any],
    discipline: Optional[str],
    limit: int = 5,
    risk_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Rank the supplied domain scores and return plain-language risk cards.

    Args:
        scores: mapping of domain_key -> numeric score (0-1). Non-numeric
            or null entries are ignored.
        discipline: 'public_health' or 'em' (anything else is treated as
            public health).
        limit: how many top-ranked hazards to return.
        risk_data: optional full jurisdiction or aggregated region risk_data
            dict. When supplied, each card is enriched with locally derived
            `drivers` (why it ranks here) and `local_populations` (groups the
            local data flags as most exposed). Read-only; never changes a
            score. When omitted, cards carry authored copy only.

    Returns:
        A list (highest score first) of template-ready dicts:
            {key, label, score, score_2dp, score_pct, level, badge,
             why, impacts, populations, note, drivers, local_populations}
    """
    discipline = _normalize_discipline(discipline)

    ranked = []
    for key, raw in (scores or {}).items():
        if isinstance(raw, bool):
            continue
        if not isinstance(raw, (int, float)):
            continue
        ranked.append((key, float(raw)))

    ranked.sort(key=lambda kv: kv[1], reverse=True)

    cards: List[Dict[str, Any]] = []
    for key, score in ranked[: max(0, limit)]:
        content = _resolve_domain_content(key, discipline)
        level = _level_for(score)
        drivers: List[str] = []
        local_populations: List[str] = []
        if isinstance(risk_data, dict):
            signals = derive_local_signals(key, risk_data)
            drivers = signals.get("drivers", [])
            local_populations = signals.get("populations", [])
        cards.append({
            "key": key,
            "label": content["label"],
            "score": score,
            "score_2dp": f"{score:.2f}",
            "score_pct": int(round(max(0.0, min(1.0, score)) * 100)),
            "level": level["level"],
            "badge": level["badge"],
            "why": content["why"],
            "impacts": content["impacts"],
            "populations": content["populations"],
            "note": content["note"],
            "drivers": drivers,
            "local_populations": local_populations,
        })
    return cards


# Canonical domains used to rank regional (HERC/WEM) risk. Each maps to a
# `{domain}_risk` field on the aggregated region risk_data. Supplementary
# proxy domains that are not surfaced on the jurisdiction summary (e.g.
# utilities) are intentionally omitted so the regional and local summaries
# stay consistent.
REGION_DOMAINS = (
    "flood", "tornado", "winter_storm", "thunderstorm", "straight_line_wind",
    "extreme_heat", "air_quality", "dam_failure", "vector_borne_disease",
    "health", "active_shooter",
)


def region_scores_from_risk_data(risk_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract a {domain: score} map from aggregated region risk_data.

    Reads the canonical `{domain}_risk` fields. Missing or non-numeric
    fields are skipped so build_top_risk_cards only ever sees real scores.
    """
    scores: Dict[str, float] = {}
    rd = risk_data or {}
    for domain in REGION_DOMAINS:
        value = rd.get(f"{domain}_risk")
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            scores[domain] = float(value)
    return scores


def reset_cache() -> None:
    """Test/dev helper: drop the cached YAML so a re-edit takes effect
    without a full process restart."""
    _load_content.cache_clear()
