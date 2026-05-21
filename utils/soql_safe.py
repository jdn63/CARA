"""Safe SoQL (Socrata Query Language) helpers.

Centralizes single-quote escaping for $where-clause interpolation. CDC
data.cdc.gov and other Socrata endpoints use single-quoted string
literals in $where; an embedded quote in a label or value must be
doubled per SoQL convention, the same way SQL '' escapes a single
quote.

CARA fetchers MUST go through these helpers when interpolating any
value into a $where clause, even when the value comes from an internal
allowlist. Defense in depth: if a future refactor lets the value
originate from config or user input, the escape is already in place
and no Socrata-injection path opens up.

Usage:

    from utils.soql_safe import safe_eq, safe_in

    params = {
        '$where': safe_eq('states', 'WI') + ' AND ' + safe_eq('label', label),
    }

    params = {
        '$where': safe_in('disease', allowed_diseases),
    }

These helpers do not validate that the field name is sane; callers
should pass only literal field names known at code-write time, never
strings sourced from config or input.
"""

from __future__ import annotations

from typing import Iterable


def _escape_value(value: str) -> str:
    """Escape a single SoQL string literal by doubling embedded quotes."""
    return str(value).replace("'", "''")


def safe_eq(field: str, value: str) -> str:
    """Return a `field='escaped_value'` SoQL equality clause."""
    return f"{field}='{_escape_value(value)}'"


def safe_in(field: str, values: Iterable[str]) -> str:
    """Return a `field IN ('a','b',...)` SoQL clause with each value escaped."""
    escaped = ",".join(f"'{_escape_value(v)}'" for v in values)
    return f"{field} IN ({escaped})"
