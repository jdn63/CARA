"""Loader for the discipline-aware action plan content layer.

Reads `data/action_plans/*.yaml` and returns the structured content
that the action plan template needs to render a domain block.

Design points:
- Content lives in YAML (not Python) so subject-matter-expert reviewers
  can edit it without touching code.
- Every activity carries exactly one `source_id` that must resolve to
  an entry in `_sources.yaml`. Unknown source ids degrade gracefully
  to a plain text-only activity instead of raising.
- The loader is cheap; YAML files are small. Cached in-process so the
  request path stays fast.
- The loader is the only public surface; the template consumes the
  return value of `get_domain_action_plan(domain, discipline)`.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml


logger = logging.getLogger(__name__)

_ACTION_PLAN_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "action_plans",
)

VALID_DISCIPLINES = ("public_health", "em")
TIER_ORDER = ("pre_season", "this_year", "multi_year")
TIER_LABELS = {
    "pre_season": "Annual baseline (refresh each planning year)",
    "this_year": "Current planning cycle (3 to 12 months)",
    "multi_year": "Multi-year capacity building (1 to 3 years)",
}


@lru_cache(maxsize=1)
def _load_sources() -> Dict[str, Dict[str, Any]]:
    path = os.path.join(_ACTION_PLAN_DIR, "_sources.yaml")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("sources", {}) or {}
    except FileNotFoundError:
        logger.warning(f"Action plan sources file not found at {path}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load action plan sources from {path}: {e}")
        return {}


@lru_cache(maxsize=16)
def _load_domain(domain: str) -> Dict[str, Any]:
    path = os.path.join(_ACTION_PLAN_DIR, f"{domain}.yaml")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get(domain, {}) or {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Failed to load action plan domain {domain} from {path}: {e}")
        return {}


def _normalize_discipline(discipline: Optional[str]) -> str:
    if discipline == "em":
        return "em"
    return "public_health"


def _resolve_activity(item: Any, sources: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    # Defensive: a corrupted YAML could give us a string, None, or a list
    # here. Skip anything that isn't a dict instead of raising.
    if not isinstance(item, dict):
        logger.warning(f"Action plan activity is not a dict, skipping: {item!r}")
        return None
    text = str(item.get("text", "")).strip()
    if not text:
        return None
    source_id = item.get("source_id")
    source = sources.get(source_id) if isinstance(source_id, str) else None
    if source_id and not source:
        logger.warning(f"Action plan activity references unknown source_id={source_id!r}")
    if source is not None and not isinstance(source, dict):
        source = None
    return {
        "text": text,
        "source": source,
        "source_id": source_id if isinstance(source_id, str) else None,
    }


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def get_domain_action_plan(domain: str, discipline: Optional[str]) -> Dict[str, Any]:
    """Return a template-ready structure for a single domain.

    Shape:
        {
          'has_content': bool,
          'framework_capabilities': {'label': str, 'items': [str, ...]} or None,
          'tiers': [
            {'key': 'pre_season', 'label': '...',
             'activities': [{'text': str, 'source': {...} or None}, ...]},
            ...
          ],
          'discipline': 'public_health' | 'em',
        }

    `has_content` is False when no YAML exists for the domain or the
    discipline branch is empty; callers should fall back to the legacy
    inline template content in that case.
    """
    discipline = _normalize_discipline(discipline)
    try:
        domain_data = _safe_dict(_load_domain(domain))
        if not domain_data:
            return {"has_content": False, "discipline": discipline}

        sources = _safe_dict(_load_sources())

        fc_block = _safe_dict(_safe_dict(domain_data.get("framework_capabilities")).get(discipline))
        framework_capabilities = None
        fc_items = fc_block.get("items")
        if isinstance(fc_items, list) and fc_items:
            framework_capabilities = {
                "label": str(fc_block.get("label", "")),
                "items": [str(x) for x in fc_items if x],
            }

        activities_block = _safe_dict(_safe_dict(domain_data.get("activities")).get(discipline))
        tiers: List[Dict[str, Any]] = []
        for tier_key in TIER_ORDER:
            items = activities_block.get(tier_key)
            if not isinstance(items, list) or not items:
                continue
            resolved = [a for a in (_resolve_activity(it, sources) for it in items) if a]
            if not resolved:
                continue
            tiers.append({
                "key": tier_key,
                "label": TIER_LABELS.get(tier_key, tier_key.replace("_", " ").title()),
                "activities": resolved,
            })

        return {
            "has_content": bool(tiers) or framework_capabilities is not None,
            "framework_capabilities": framework_capabilities,
            "tiers": tiers,
            "discipline": discipline,
        }
    except Exception as e:
        # Never break the request path over malformed YAML. The template
        # falls back to its inline copy when has_content is False.
        logger.error(f"get_domain_action_plan({domain!r}, {discipline!r}) failed; falling back to inline content: {e}")
        return {"has_content": False, "discipline": discipline}


def reset_cache() -> None:
    """Test/dev helper: drop the cached YAML so a re-edit takes effect
    without a full process restart."""
    _load_sources.cache_clear()
    _load_domain.cache_clear()
