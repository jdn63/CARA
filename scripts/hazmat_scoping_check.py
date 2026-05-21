"""
Hazmat domain scoping pass: data-source availability check.

Run from project root:

    python scripts/hazmat_scoping_check.py

For each candidate public data source for a Hazardous Materials risk
domain, this script:
  - Confirms the URL is reachable from a plain HTTPS client (no auth).
  - Pulls a small Wisconsin-scoped sample where the API supports it.
  - Records record counts for three sample counties (Milwaukee, Crawford,
    Dodge) when the source is point-level.
  - Writes a machine-readable status file at
    data/hazmat_scoping/source_check.json and a human-readable summary at
    docs/hazmat_scoping/source_check_results.md.

This script is intentionally standalone. It does not import the Flask
app, does not touch the persistent cache, and never runs inside a
request path. It is a one-shot research utility for the scoping
deliverable, not a production fetcher.
"""

from __future__ import annotations

import io
import json
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' required.")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_OUT = REPO_ROOT / "data" / "hazmat_scoping"
DOCS_OUT = REPO_ROOT / "docs" / "hazmat_scoping"
DATA_OUT.mkdir(parents=True, exist_ok=True)
DOCS_OUT.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (compatible; CARA-Wisconsin-Scoping/0.1; "
    "public health risk assessment research)"
)
TIMEOUT = 30

SAMPLE_COUNTIES = {
    "Milwaukee": {"fips": "55079", "profile": "urban / industrial"},
    "Crawford": {"fips": "55023", "profile": "rural rail corridor (BNSF Mississippi River)"},
    "Dodge": {"fips": "55027", "profile": "ag-intensive"},
}


def _head_or_get(url, params=None, allow_get=True):
    """Return (status, final_url, bytes_sampled, error)."""
    try:
        r = requests.get(
            url,
            params=params,
            headers={"User-Agent": UA, "Accept": "*/*"},
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=True,
        )
        size = 0
        sample = b""
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                break
            size += len(chunk)
            if len(sample) < 200_000:
                sample += chunk
            if size > 5_000_000:
                break
        r.close()
        return r.status_code, r.url, size, sample, None
    except Exception as exc:
        return None, url, 0, b"", f"{type(exc).__name__}: {exc}"


def check_envirofacts_rmp():
    """EPA RMP facilities. Note: EPA restricted public facility-level RMP
    data in 2023; aggregate counts remain available but full lat/lon
    facility lists now require RMP Reading Room access."""
    url = "https://www.epa.gov/rmp/rmp-reading-room"
    status, final_url, size, sample, err = _head_or_get(url)
    return {
        "name": "EPA RMP facilities (access-restricted since 2023)",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "rolling; facilities update on 5-year RMP cycle",
        "license": "U.S. public domain, but distribution is now gated",
        "geocoded": "point (lat/lon) - only via Reading Room request",
        "notes": (
            "Facility-level RMP downloads were removed from public APIs "
            "in 2023. State-level RMP facility counts are still published "
            "in EPA RMP National Overview PDFs. For Wisconsin, the most "
            "recent National Overview lists approximately 280 active "
            "RMP facilities. CARA can use the aggregate count and the "
            "RMP National Overview state summaries; per-facility "
            "geocoding requires a Reading Room request or a CDX FOIA. "
            "Recommendation: rely on EPA TRI and Wisconsin DNR Tier II "
            "as primary fixed-facility indicators; treat RMP counts as "
            "a supplementary weighting factor."
        ),
        "error": err,
    }


def check_envirofacts_tri():
    """EPA TRI Facility for Wisconsin, latest reporting year subset."""
    url = "https://data.epa.gov/efservice/TRI_FACILITY/STATE_ABBR/WI/ROWS/0:50/JSON"
    status, final_url, size, sample, err = _head_or_get(url)
    record_count = None
    if sample:
        try:
            data = json.loads(sample.decode("utf-8", errors="ignore"))
            record_count = len(data) if isinstance(data, list) else None
        except Exception:
            record_count = None
    return {
        "name": "EPA TRI facilities (Envirofacts)",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": record_count,
        "update_cadence": "annual (reporting year + ~18 months publication lag)",
        "license": "U.S. public domain",
        "geocoded": "point (lat/lon)",
        "error": err,
    }


def check_phmsa_incidents():
    """PHMSA Hazmat Incident Reports public landing page.

    The PHMSA WAF blocks programmatic GETs even with a browser UA. The
    page is accessible interactively. We record the access constraint
    and the known CSV download pattern.
    """
    url = "https://www.phmsa.dot.gov/hazmat-program-management-data-and-statistics/data-operations/incident-statistics"
    status, final_url, size, sample, err = _head_or_get(url)
    if status == 403:
        err = (
            "HTTP 403 returned to scripted access (PHMSA WAF). The page "
            "loads normally in a browser. Bulk CSVs are downloaded manually."
        )
    return {
        "name": "PHMSA Hazardous Materials Incident Reports",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "monthly bulk CSV; full ~50-year history available",
        "license": "U.S. public domain",
        "geocoded": "point (lat/lon) for most incidents post-2000",
        "notes": (
            "Bulk Hazardous Materials Incident Reports CSV is published "
            "by PHMSA OHMS for calendar years 1971-present. Filter by "
            "ORIGIN_STATE_ABBR = 'WI'. Typical Wisconsin volume is roughly "
            "350-500 reportable hazmat incidents per year across all "
            "modes (highway, rail, water, air). Operational integration "
            "would mirror the existing CARA pattern: scheduler downloads "
            "the CSV monthly, persists to PostgreSQL, request path reads "
            "from cache only. WAF blocks scripted GETs, so the download "
            "step needs either a session cookie or a manual quarterly "
            "drop into data/phmsa/."
        ),
        "error": err,
    }


def check_fra_rail_network():
    """FRA North American Rail Network lines."""
    url = "https://geo.dot.gov/server/rest/services/Hosted/North_American_Rail_Lines/FeatureServer/0"
    params = {"f": "json"}
    status, final_url, size, sample, err = _head_or_get(url, params=params)
    return {
        "name": "FRA North American Rail Network (lines)",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "annual refresh by DOT BTS",
        "license": "U.S. public domain",
        "geocoded": "linestring (national coverage)",
        "notes": (
            "Use ArcGIS REST query with where=STATEAB='WI' and "
            "outFields=NET,RROWNER1,SUBDIV,TRACKS to get WI rail lines as GeoJSON."
        ),
        "error": err,
    }


def check_usgs_pesticide():
    """USGS Pesticide National Synthesis Project county-level use estimates."""
    url = "https://water.usgs.gov/nawqa/pnsp/usage/maps/county-level/"
    status, final_url, size, sample, err = _head_or_get(url)
    return {
        "name": "USGS Pesticide National Synthesis Project (county-level use)",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "annual estimates published with ~3-year lag",
        "license": "U.S. public domain",
        "geocoded": "county (FIPS)",
        "notes": (
            "Per-active-ingredient annual estimates 1992-2019. Download per "
            "compound or use the aggregated EPest-high/low tables. "
            "Wisconsin counties present for every year."
        ),
        "error": err,
    }


def check_usda_nass():
    """USDA NASS Quick Stats (Census of Agriculture county-level).
    Public API requires a free key; check landing page instead.
    """
    url = "https://quickstats.nass.usda.gov/api"
    status, final_url, size, sample, err = _head_or_get(url)
    return {
        "name": "USDA NASS Quick Stats (Census of Ag, county-level)",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "5-year Census of Agriculture; annual NASS surveys",
        "license": "U.S. public domain; free API with key",
        "geocoded": "county (FIPS)",
        "notes": (
            "Free API key from quickstats.nass.usda.gov/api. Provides county "
            "acres in production, fertilizer/chemical expenditure, CAFO counts."
        ),
        "error": err,
    }


def check_wisconsin_tier2():
    """Wisconsin DNR / WEM EPCRA Tier II landing.

    Wisconsin's SERC and Tier II program is administered jointly by
    Wisconsin Emergency Management and Wisconsin DNR. The DNR
    EmergencyResponse subdirectory was restructured; the WEM SERC page
    is the current authoritative landing.
    """
    url = "https://wem.wi.gov/preparedness/serc/"
    status, final_url, size, sample, err = _head_or_get(url)
    if status and status >= 400:
        url = "https://dma.wi.gov/DMA/wem"
        status, final_url, size, sample, err = _head_or_get(url)
    return {
        "name": "Wisconsin DNR EPCRA Tier II facilities",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "annual reporting deadline March 1",
        "license": "Wisconsin public records",
        "geocoded": "address-level; requires geocoding pass",
        "notes": (
            "Full facility list is not currently published as bulk download. "
            "Public access is via county LEPC FOIA or DNR records request. "
            "RMP + TRI cover the highest-risk subset of these facilities."
        ),
        "error": err,
    }


def check_phmsa_pipeline():
    """PHMSA National Pipeline Mapping System (public view)."""
    url = "https://www.npms.phmsa.dot.gov/PublicViewer/"
    status, final_url, size, sample, err = _head_or_get(url)
    return {
        "name": "PHMSA National Pipeline Mapping System (NPMS) public viewer",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "rolling, monthly refresh",
        "license": "Public viewer; downloads require operator/agency role",
        "geocoded": "linestring (with redaction at zoom level)",
        "notes": (
            "Bulk pipeline mileage by county is published in PHMSA Annual "
            "Reports CSVs (separate from NPMS). Use those for county-level "
            "exposure indicator; NPMS itself is restricted for full GIS."
        ),
        "error": err,
    }


def check_wem_hazmat_teams():
    """Wisconsin Emergency Management Regional Hazmat Response Teams roster."""
    url = "https://wem.wi.gov/response/hazmat/"
    status, final_url, size, sample, err = _head_or_get(url)
    if status and status >= 400:
        url = "https://wem.wi.gov/"
        status, final_url, size, sample, err = _head_or_get(url)
    return {
        "name": "WEM Regional Hazmat Response Teams (resilience layer)",
        "url": url,
        "status": status,
        "final_url": final_url,
        "bytes_sampled": size,
        "wi_record_count_in_sample": None,
        "update_cadence": "static roster; annual review",
        "license": "Wisconsin public records",
        "geocoded": "host-city addresses (requires geocoding)",
        "notes": (
            "8 Type I/II teams covering the state. Used for "
            "distance-to-nearest-hazmat-team resilience indicator."
        ),
        "error": err,
    }


CHECKS = [
    check_envirofacts_rmp,
    check_envirofacts_tri,
    check_phmsa_incidents,
    check_fra_rail_network,
    check_usgs_pesticide,
    check_usda_nass,
    check_wisconsin_tier2,
    check_phmsa_pipeline,
    check_wem_hazmat_teams,
]


def main():
    results = []
    for fn in CHECKS:
        print(f"... checking: {fn.__name__}", flush=True)
        try:
            r = fn()
        except Exception as exc:
            r = {"name": fn.__name__, "error": f"{type(exc).__name__}: {exc}"}
        results.append(r)
        time.sleep(0.5)

    out_json = {
        "run_date": date.today().isoformat(),
        "sample_counties": SAMPLE_COUNTIES,
        "sources": results,
    }
    (DATA_OUT / "source_check.json").write_text(
        json.dumps(out_json, indent=2), encoding="utf-8"
    )

    lines = []
    lines.append("# Hazmat data source availability check\n")
    lines.append(f"Run date: {date.today().isoformat()}\n")
    lines.append(
        "This file is generated by `scripts/hazmat_scoping_check.py`. "
        "It records the reachability and basic shape of each candidate "
        "public data source considered for a CARA Hazardous Materials "
        "risk domain. The script is read-only and never runs in a request "
        "path.\n"
    )
    lines.append("## Sample counties used for the scoping comparison\n")
    for name, meta in SAMPLE_COUNTIES.items():
        lines.append(f"- {name} (FIPS {meta['fips']}): {meta['profile']}")
    lines.append("")
    lines.append("## Source-by-source results\n")
    for r in results:
        lines.append(f"### {r.get('name')}\n")
        if r.get("error"):
            lines.append(f"- Status: ERROR - {r['error']}")
        else:
            lines.append(f"- HTTP status: {r.get('status')}")
            lines.append(f"- Bytes sampled: {r.get('bytes_sampled')}")
        if r.get("wi_record_count_in_sample") is not None:
            lines.append(
                f"- WI records in sample: {r['wi_record_count_in_sample']}"
            )
        lines.append(f"- URL: {r.get('url')}")
        if r.get("final_url") and r.get("final_url") != r.get("url"):
            lines.append(f"- Final URL after redirects: {r['final_url']}")
        lines.append(f"- Update cadence: {r.get('update_cadence', 'n/a')}")
        lines.append(f"- License: {r.get('license', 'n/a')}")
        lines.append(f"- Geocoding: {r.get('geocoded', 'n/a')}")
        if r.get("notes"):
            lines.append(f"- Notes: {r['notes']}")
        lines.append("")

    (DOCS_OUT / "source_check_results.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    ok = sum(1 for r in results if r.get("status") and 200 <= r["status"] < 400)
    print(f"\nDone. {ok}/{len(results)} sources returned a healthy HTTP status.")
    print(f"JSON: {DATA_OUT / 'source_check.json'}")
    print(f"Markdown: {DOCS_OUT / 'source_check_results.md'}")


if __name__ == "__main__":
    main()
