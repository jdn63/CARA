"""Wisconsin counties for the Emergency Management discipline landing
surface.

CARA's Public Health discipline picks from 84 LHD jurisdictions; the
Emergency Management discipline operates at the 72-county level. This
module is the single source of truth for the EM county list and for the
slug used in /em-dashboard/<county_slug> URLs.

The county risk pipeline reuses the existing process_risk_data()
function with discipline='em'. To stay inside that contract without a
new entry point, each county is mapped to its canonical county-level
jurisdiction id (the same ids returned by
utils.data_processor.get_county_id). City LHDs (Milwaukee city, Madison
city, etc.) are intentionally ignored at this layer because EM planning
in Wisconsin is organized county-wide.

Tribal LHDs are not represented here because Tribal data sovereignty
is handled separately (see TRIBAL HIDE stopgap in
utils/data_processor.py) and Tribal lands are not WEM jurisdictions in
the sense used by county EM offices.
"""

from typing import Dict, List, Optional

from utils.dhs_data import WISCONSIN_COUNTIES
from utils.data_processor import get_county_id


def county_to_slug(county_name: str) -> str:
    """Convert a Wisconsin county name to a URL-safe slug.

    Examples:
        "Eau Claire" -> "eau-claire"
        "Fond du Lac" -> "fond-du-lac"
        "St. Croix" -> "st-croix"
        "La Crosse" -> "la-crosse"
    """
    return (
        county_name.lower()
        .replace('.', '')
        .replace(' ', '-')
    )


# Slug -> canonical county name lookup, built once at import time so
# /em-dashboard/<slug> resolution is O(1) and immune to county name
# normalization drift.
_SLUG_TO_COUNTY: Dict[str, str] = {
    county_to_slug(c): c for c in WISCONSIN_COUNTIES
}


def get_county_for_slug(slug: str) -> Optional[str]:
    """Reverse of county_to_slug. Returns None for unknown slugs."""
    if not slug:
        return None
    return _SLUG_TO_COUNTY.get(slug.strip().lower())


_JURISDICTION_ID_TO_SLUG: Dict[str, str] = {
    str(get_county_id(c)): county_to_slug(c) for c in WISCONSIN_COUNTIES
}


def get_slug_for_jurisdiction_id(jurisdiction_id) -> Optional[str]:
    """Reverse of get_county_id() composed with county_to_slug(): given a
    canonical county-level LHD jurisdiction id, return its EM URL slug,
    or None if the id is not a county-level LHD (e.g. a city LHD or a
    Tribal LHD). Used by the dashboard and print-summary views to build
    the Back-to-Dashboard link as /em-dashboard/<slug> in EM mode."""
    if jurisdiction_id is None:
        return None
    return _JURISDICTION_ID_TO_SLUG.get(str(jurisdiction_id))


def get_wi_counties_for_em() -> List[Dict[str, str]]:
    """Return all 72 Wisconsin counties for the EM dropdown.

    Each entry has:
      - id: slug used in /em-dashboard/<slug>
      - name: human-readable county name
      - jurisdiction_id: canonical county LHD jurisdiction id, used by
        the EM dashboard route to call process_risk_data().

    Sorted alphabetically by name.
    """
    out: List[Dict[str, str]] = []
    for county in sorted(WISCONSIN_COUNTIES):
        out.append({
            'id': county_to_slug(county),
            'name': county,
            'jurisdiction_id': get_county_id(county),
        })
    return out
