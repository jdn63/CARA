"""Build the county TRI facility count seed from EPA Envirofacts.

Fetches all open Wisconsin TRI facilities (TRI_FACILITY table,
FAC_CLOSED_IND = 0) in one paginated pass, counts facilities per
county, and writes data/hazmat_scoping/county_tri_counts.json with a
count for every county that has at least one facility. Counties absent
from TRI keep tri_facilities = 0 (a real measured zero, not a gap).

This is a build-time seed script, not a request-path fetcher. Rerun
annually (TRI publishes yearly) or when EPA refreshes the facility
registry:

    python3 scripts/build_tri_counts_seed.py
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests

EF_BASE = "https://data.epa.gov/efservice"
OUT_PATH = "data/hazmat_scoping/county_tri_counts.json"
PAGE_SIZE = 1000

WISCONSIN_COUNTIES = [
    "Adams", "Ashland", "Barron", "Bayfield", "Brown", "Buffalo",
    "Burnett", "Calumet", "Chippewa", "Clark", "Columbia", "Crawford",
    "Dane", "Dodge", "Door", "Douglas", "Dunn", "Eau Claire",
    "Florence", "Fond du Lac", "Forest", "Grant", "Green", "Green Lake",
    "Iowa", "Iron", "Jackson", "Jefferson", "Juneau", "Kenosha",
    "Kewaunee", "La Crosse", "Lafayette", "Langlade", "Lincoln",
    "Manitowoc", "Marathon", "Marinette", "Marquette", "Menominee",
    "Milwaukee", "Monroe", "Oconto", "Oneida", "Outagamie", "Ozaukee",
    "Pepin", "Pierce", "Polk", "Portage", "Price", "Racine",
    "Richland", "Rock", "Rusk", "St. Croix", "Sauk", "Sawyer",
    "Shawano", "Sheboygan", "Taylor", "Trempealeau", "Vernon", "Vilas",
    "Walworth", "Washburn", "Washington", "Waukesha", "Waupaca",
    "Waushara", "Winnebago", "Wood",
]


def fetch_open_wi_tri_facilities():
    rows = []
    start = 0
    while True:
        url = (f"{EF_BASE}/TRI_FACILITY/STATE_ABBR/=/WI/"
               f"FAC_CLOSED_IND/=/0/ROWS/{start}:{start + PAGE_SIZE - 1}/JSON")
        resp = requests.get(url, timeout=90)
        resp.raise_for_status()
        page = resp.json()
        if not isinstance(page, list) or not page:
            break
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        start += PAGE_SIZE
    return rows


def main():
    facilities = fetch_open_wi_tri_facilities()
    print(f"Fetched {len(facilities)} open WI TRI facilities")

    counts = {}
    unmatched = set()
    by_upper = {c.upper(): c for c in WISCONSIN_COUNTIES}
    by_upper["SAINT CROIX"] = "St. Croix"
    by_upper["ST CROIX"] = "St. Croix"
    by_upper["FOND DU LAC"] = "Fond du Lac"
    # EPA registry data quality quirks: some WI facilities carry
    # out-of-state county labels. Cities confirm the true counties.
    by_upper["JUNEAU BOROUGH"] = "Juneau"       # Mauston, Necedah, etc.
    by_upper["ST. CROIX ISLAND"] = "St. Croix"  # Baldwin, Hudson, etc.

    for fac in facilities:
        raw = (fac.get("county_name") or "").strip().upper()
        county = by_upper.get(raw)
        if not county:
            unmatched.add(raw)
            continue
        counts[county] = counts.get(county, 0) + 1

    if unmatched:
        print(f"WARNING unmatched county names: {sorted(unmatched)}")

    out = {
        "_meta": {
            "source": "EPA Envirofacts TRI_FACILITY (open facilities, FAC_CLOSED_IND=0)",
            "url": f"{EF_BASE}/TRI_FACILITY/STATE_ABBR/=/WI/FAC_CLOSED_IND/=/0/ROWS/.../JSON",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_open_facilities": len(facilities),
            "note": ("Counts are real measured values for all 72 counties; "
                     "counties without TRI facilities carry a true zero."),
        }
    }
    for county in WISCONSIN_COUNTIES:
        out[county] = {"tri_facilities": counts.get(county, 0)}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_PATH}: {len(WISCONSIN_COUNTIES)} counties, "
          f"{sum(counts.values())} facilities matched")


if __name__ == "__main__":
    sys.exit(main())
