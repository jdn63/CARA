"""Build the county agricultural chemical intensity seed from USDA NASS.

Fetches four county-level series from the USDA NASS QuickStats API
(Census of Agriculture, domain TOTAL) and writes
data/hazmat_scoping/wi_county_ag_chemical.json with an
ag_chemical_intensity score (0-1) for every county:

  - CHEMICAL TOTALS - EXPENSE, MEASURED IN $
  - FERTILIZER TOTALS, INCL LIME & SOIL CONDITIONERS - EXPENSE, MEASURED IN $
  - AG LAND, CROPLAND, HARVESTED - ACRES
  - CATTLE, COWS, MILK - INVENTORY

Scoring: 0.5 * combined chemical+fertilizer expense norm
       + 0.25 * harvested cropland norm
       + 0.25 * milk cow inventory norm,
each normalized to the statewide 95th percentile and capped at 1.0,
with weights renormalized over the fields that are not census-suppressed.
Suppressed values "(D)" stay null (never fabricated). Counties with no
census record at all (Menominee) score 0.0 with data_status
no_census_record; the runtime scorer applies its own exposure floor.

This is a build-time seed script, not a request-path fetcher. Rerun when
a new Census of Agriculture is released (every 5 years; next is 2027
data published in 2029):

    NASS_QUICKSTATS_API_KEY=<key> python3 scripts/build_ag_chemical_seed.py

The API key is free from quickstats.nass.usda.gov/api and is needed only
at build time on the developer machine, never in production.
"""
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

API_BASE = "https://quickstats.nass.usda.gov/api/api_GET/"
OUT_PATH = "data/hazmat_scoping/wi_county_ag_chemical.json"
CENSUS_YEAR = "2022"

FIELDS = {
    "chemical_expense_usd": "CHEMICAL TOTALS - EXPENSE, MEASURED IN $",
    "fertilizer_expense_usd":
        "FERTILIZER TOTALS, INCL LIME & SOIL CONDITIONERS - EXPENSE, "
        "MEASURED IN $",
    "cropland_harvested_acres": "AG LAND, CROPLAND, HARVESTED - ACRES",
    "milk_cows_head": "CATTLE, COWS, MILK - INVENTORY",
}

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

# NASS county_name quirks vs canonical spellings
NAME_REMAP = {
    "Fond Du Lac": "Fond du Lac",
    "St Croix": "St. Croix",
    "St. Croix": "St. Croix",
    "La Crosse": "La Crosse",
}


def fetch(key, short_desc):
    """Fetch one county-level series. domain_desc=TOTAL is required:
    without it, QuickStats returns size-class breakdown rows that
    silently overwrite each other."""
    params = {
        "key": key, "source_desc": "CENSUS", "year": CENSUS_YEAR,
        "state_alpha": "WI", "agg_level_desc": "COUNTY",
        "domain_desc": "TOTAL",
        "short_desc": short_desc, "format": "JSON",
    }
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)["data"]


def canonical_county(raw_name):
    name = raw_name.strip().title()
    name = NAME_REMAP.get(name, name)
    return name if name in WISCONSIN_COUNTIES else None


def main():
    key = os.environ.get("NASS_QUICKSTATS_API_KEY")
    if not key:
        print("ERROR: set NASS_QUICKSTATS_API_KEY (free key from "
              "quickstats.nass.usda.gov/api)")
        return 1

    raw = {c: {f: None for f in FIELDS} for c in WISCONSIN_COUNTIES}
    unmatched = set()
    for field, short_desc in FIELDS.items():
        rows = fetch(key, short_desc)
        n_ok = n_supp = 0
        for row in rows:
            county = canonical_county(row.get("county_name", ""))
            if county is None:
                if row.get("county_name"):
                    unmatched.add(row["county_name"])
                continue
            val = row["Value"].replace(",", "").strip()
            if val.startswith("("):
                raw[county][field] = None
                n_supp += 1
            else:
                raw[county][field] = int(val)
                n_ok += 1
        print(f"{field}: rows={len(rows)} ok={n_ok} suppressed={n_supp}")
    if unmatched:
        print(f"WARNING unmatched county names: {sorted(unmatched)}")

    def p95(field):
        vals = sorted(v[field] for v in raw.values()
                      if v[field] is not None)
        return vals[int(0.95 * len(vals))]

    norms = {f: p95(f) for f in FIELDS}

    counties = {}
    for c, v in sorted(raw.items()):
        parts = {}
        if (v["chemical_expense_usd"] is not None
                and v["fertilizer_expense_usd"] is not None):
            parts["chem"] = min(1.0, (
                v["chemical_expense_usd"] + v["fertilizer_expense_usd"]) / (
                norms["chemical_expense_usd"]
                + norms["fertilizer_expense_usd"]))
        if v["cropland_harvested_acres"] is not None:
            parts["cropland"] = min(
                1.0, v["cropland_harvested_acres"]
                / norms["cropland_harvested_acres"])
        if v["milk_cows_head"] is not None:
            parts["milk"] = min(
                1.0, v["milk_cows_head"] / norms["milk_cows_head"])
        weights = {"chem": 0.5, "cropland": 0.25, "milk": 0.25}
        avail = {k: w for k, w in weights.items() if k in parts}
        if avail:
            tot = sum(avail.values())
            score = sum(parts[k] * w for k, w in avail.items()) / tot
            status = ("complete" if len(parts) == 3
                      else "partial_suppressed")
        else:
            score, status = 0.0, "no_census_record"
        counties[c] = dict(
            v, ag_chemical_intensity=round(score, 4), data_status=status)

    seed = {
        "_meta": {
            "source": ("USDA NASS Census of Agriculture "
                       f"{CENSUS_YEAR}, QuickStats API"),
            "retrieved": str(datetime.date.today()),
            "fields": {
                f: f"{sd} (domain TOTAL)" for f, sd in FIELDS.items()
            },
            "nulls": ("null = census disclosure-suppressed (D) or no "
                      "census record; never fabricated"),
            "ag_chemical_intensity": (
                "0-1 score: 0.5*(chem+fertilizer expense norm) + "
                "0.25*cropland norm + 0.25*milk cows norm, each capped "
                "at the statewide 95th percentile; weights renormalized "
                "over available fields"),
            "normalizers_p95": norms,
        },
        "counties": counties,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(seed, f, indent=1)

    top = sorted(counties.items(),
                 key=lambda kv: -kv[1]["ag_chemical_intensity"])[:5]
    bot = sorted(counties.items(),
                 key=lambda kv: kv[1]["ag_chemical_intensity"])[:5]
    print(f"Wrote {OUT_PATH}: {len(counties)} counties")
    print("top:", [(c, v["ag_chemical_intensity"]) for c, v in top])
    print("bottom:", [(c, v["ag_chemical_intensity"], v["data_status"])
                      for c, v in bot])
    return 0


if __name__ == "__main__":
    sys.exit(main())
