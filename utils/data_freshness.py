"""Data freshness helpers.

Centralizes the logic for translating cached data timestamps into user-facing
freshness indicators. Used by domain calculators and the dashboard so that
"stale but real" cached data is always preferred over synthetic fallbacks,
with a clear "data is N days old" flag.

Conventions:
- A cache entry is "fresh" if its age is at or below the source-specific
  expectation (e.g. 7 days for weekly feeds, 30 days for monthly).
- A cache entry is "stale" if older than that but still within an absolute
  hard cap (default 180 days). Stale entries are still real data and should
  still be used; the dashboard simply surfaces the staleness.
- If no cache entry exists at all, the domain is "unavailable" - it must
  not be silently replaced with a synthetic value. Callers should drop
  the domain so the PHRAT composite is renormalized over the remaining
  available domains.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default freshness expectations per source type, expressed in days.
# Derived from utils.source_registry so the freshness table can never
# disagree with the scheduler or the cache about how stale is too stale.
# Callers may still pass an explicit expected_max_age_days override.
#
# Legacy alias keys are kept side-by-side with the canonical IDs so that
# cache rows written before the H16 rename still resolve to a sensible
# expectation during the transitional window. The startup assertion in
# utils.source_registry.validate_all_namespaces requires every key in
# this dict to map to a canonical ID.
from utils.source_registry import CANONICAL_SOURCES as _CANON, _ALIAS_TO_CANONICAL as _ALIAS

DEFAULT_FRESHNESS_DAYS: Dict[str, int] = {
    cid: spec.freshness_max_age_days for cid, spec in _CANON.items()
}
for _alias, _cid in _ALIAS.items():
    DEFAULT_FRESHNESS_DAYS.setdefault(_alias, _CANON[_cid].freshness_max_age_days)

# Absolute upper bound on cache age. Beyond this, even "stale-but-real" is
# considered too old to use; the domain should be marked unavailable.
ABSOLUTE_STALE_LIMIT_DAYS = 180


@dataclass
class FreshnessReport:
    """Structured freshness verdict for a cache entry."""
    available: bool          # True if any real data is available at all
    fresh: bool              # True if within source-specific expected window
    stale: bool              # True if available but older than expected
    age_days: Optional[float]
    fetched_at: Optional[datetime]
    expected_max_age_days: int
    label: str               # short human-readable string for UI badges
    detail: str              # longer human-readable explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            'available': self.available,
            'fresh': self.fresh,
            'stale': self.stale,
            'age_days': round(self.age_days, 1) if self.age_days is not None else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'expected_max_age_days': self.expected_max_age_days,
            'label': self.label,
            'detail': self.detail,
        }


def _coerce_datetime(value: Any) -> Optional[datetime]:
    """Best-effort conversion to a timezone-naive UTC datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(value))
        except (OSError, OverflowError, ValueError):
            return None
    if isinstance(value, str):
        try:
            cleaned = value.replace('Z', '+00:00')
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is not None:
                return dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except ValueError:
            return None
    return None


def assess_freshness(
    fetched_at: Any,
    source_type: Optional[str] = None,
    expected_max_age_days: Optional[int] = None,
) -> FreshnessReport:
    """Build a FreshnessReport for a cache entry.

    Args:
        fetched_at: When the cached data was fetched (datetime, ISO string,
            or unix timestamp). Pass None if no cache entry exists.
        source_type: Optional source key to look up the default expected age.
        expected_max_age_days: Explicit override for the expected age window.

    Returns:
        FreshnessReport describing availability, freshness and a UI label.
    """
    if expected_max_age_days is None:
        expected_max_age_days = DEFAULT_FRESHNESS_DAYS.get(source_type or '', 14)

    fetched_dt = _coerce_datetime(fetched_at)
    if fetched_dt is None:
        return FreshnessReport(
            available=False,
            fresh=False,
            stale=False,
            age_days=None,
            fetched_at=None,
            expected_max_age_days=expected_max_age_days,
            label='Data unavailable',
            detail='No cached data has been retrieved for this source yet.',
        )

    now = datetime.utcnow()
    age_seconds = max(0.0, (now - fetched_dt).total_seconds())
    age_days = age_seconds / 86400.0

    if age_days > ABSOLUTE_STALE_LIMIT_DAYS:
        return FreshnessReport(
            available=False,
            fresh=False,
            stale=True,
            age_days=age_days,
            fetched_at=fetched_dt,
            expected_max_age_days=expected_max_age_days,
            label=f'Data {int(age_days)} days old (too old to use)',
            detail=(
                f'Cached data is {int(age_days)} days old, exceeding the '
                f'{ABSOLUTE_STALE_LIMIT_DAYS}-day absolute limit. Treating '
                'this domain as unavailable until a successful refresh.'
            ),
        )

    if age_days <= expected_max_age_days:
        return FreshnessReport(
            available=True,
            fresh=True,
            stale=False,
            age_days=age_days,
            fetched_at=fetched_dt,
            expected_max_age_days=expected_max_age_days,
            label=f'Updated {_humanize_age(age_days)}',
            detail=(
                f'Data fetched {_humanize_age(age_days)}; within the '
                f'{expected_max_age_days}-day expected refresh window.'
            ),
        )

    return FreshnessReport(
        available=True,
        fresh=False,
        stale=True,
        age_days=age_days,
        fetched_at=fetched_dt,
        expected_max_age_days=expected_max_age_days,
        label=f'Data {int(age_days)} days old',
        detail=(
            f'Using cached real data from {_humanize_age(age_days)} ago; the '
            f'source has not refreshed within its expected {expected_max_age_days}-day '
            'window. Values are real but may not reflect the most current conditions.'
        ),
    )


def _humanize_age(age_days: float) -> str:
    """Return a short human-readable age string."""
    if age_days < 1:
        hours = max(1, int(age_days * 24))
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    if age_days < 14:
        days = max(1, int(round(age_days)))
        return f'{days} day{"s" if days != 1 else ""} ago'
    if age_days < 60:
        weeks = int(round(age_days / 7))
        return f'{weeks} weeks ago'
    months = int(round(age_days / 30))
    return f'{months} month{"s" if months != 1 else ""} ago'


def freshness_from_cache_entry(
    cache_entry: Optional[Dict[str, Any]],
    source_type: Optional[str] = None,
    expected_max_age_days: Optional[int] = None,
) -> FreshnessReport:
    """Convenience wrapper: assess freshness from a get_cached_data() result.

    The data_cache_manager.get_cached_data() function returns a dict with
    'fetched_at' (and optional 'age_hours'). This helper extracts the
    timestamp and builds the FreshnessReport.
    """
    if not cache_entry:
        return assess_freshness(None, source_type=source_type,
                                expected_max_age_days=expected_max_age_days)
    return assess_freshness(
        cache_entry.get('fetched_at'),
        source_type=source_type,
        expected_max_age_days=expected_max_age_days,
    )


def get_all_freshness_reports(
    canonical_only: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """Return a freshness report for every cached source in one DB query.

    Used by the dashboard data-quality payload so per-category freshness
    badges can be rendered without making 20 separate cache lookups
    during template render.

    Returns:
        Dict mapping canonical source_id -> FreshnessReport.to_dict().
        Sources with no cache row at all are included with
        ``available=False`` so the template can still render a
        "no data yet" badge if it wants to.
    """
    reports: Dict[str, Dict[str, Any]] = {}
    try:
        from core import db
        from models import DataSourceCache
        from sqlalchemy import func

        rows = (
            db.session.query(
                DataSourceCache.source_type,
                func.max(DataSourceCache.fetched_at),
            )
            .group_by(DataSourceCache.source_type)
            .all()
        )
        seen: Dict[str, Any] = {}
        for source_type, max_fetched in rows:
            canon = _ALIAS.get(source_type, source_type)
            prev = seen.get(canon)
            if prev is None or (max_fetched and max_fetched > prev):
                seen[canon] = max_fetched

        for canon, max_fetched in seen.items():
            if canonical_only and canon not in _CANON:
                continue
            reports[canon] = assess_freshness(
                max_fetched, source_type=canon
            ).to_dict()
    except Exception as exc:
        logger.warning(
            "get_all_freshness_reports: bulk query failed: %s", exc
        )
        return {}

    # Include known canonical sources that have no cache row at all so
    # the UI can still render an "unavailable" badge for them.
    if canonical_only:
        for canon in _CANON:
            reports.setdefault(
                canon,
                assess_freshness(None, source_type=canon).to_dict(),
            )

    return reports
