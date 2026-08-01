"""Build the baked NOAA nClimDiv county climate-trend snapshot.

One-time acquisition script (same pattern as the USDA RUCC snapshot):
fetches observed annual precipitation and average temperature for all 72
Wisconsin counties from NOAA's Climate at a Glance county time-series
API (nClimDiv dataset), computes a documented recent-vs-baseline trend
for each county, and writes data/climate/nclimdiv_county_climate_trends.json.

Method (disclosed in output metadata and on the methodology page):
- Baseline period: 1951-2000 mean (50 years).
- Recent period: 2011-2025 mean (15 years).
- Trend ratio = recent mean / baseline mean, plus percent change.

The runtime app never calls NOAA for this; it reads the baked snapshot.
Rerun this script to refresh (annual cadence is plenty; nClimDiv updates
monthly but county climate trends move slowly).

Usage: python scripts/build_nclimdiv_snapshot.py
Fails loudly (exit 1) if any county cannot be fetched, so a partial
snapshot can never silently ship.
"""
import json
import os
import sys
import time
from datetime import date

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openfema_data import WI_COUNTY_FIPS_3DIGIT  # noqa: E402

BASE_URL = "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series"
BASELINE_START, BASELINE_END = 1951, 2000
RECENT_START, RECENT_END = 2011, 2025
VARIABLES = {"pcp": "precipitation (inches)", "tavg": "average temperature (deg F)"}
OUTPUT_PATH = os.path.join("data", "climate", "nclimdiv_county_climate_trends.json")
HEADERS = {"User-Agent": "CARA-Wisconsin-risk-tool/1.0 (public health preparedness; one-time snapshot build)"}


def fetch_series(fips3: str, variable: str) -> dict:
    """Fetch one county/variable annual series. Returns {year: value}."""
    url = (f"{BASE_URL}/WI-{fips3}/{variable}/12/12/"
           f"{BASELINE_START}-{RECENT_END}.json")
    last_err = None
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=30, headers=HEADERS)
            resp.raise_for_status()
            payload = resp.json()
            data = payload.get("data", {})
            series = {}
            for key, entry in data.items():
                # keys look like "195112" (year + ending month 12)
                year = int(str(key)[:4])
                value = entry.get("value")
                if value is None:
                    continue
                value = float(value)
                if value < -90:  # nClimDiv missing-value sentinel
                    continue
                series[year] = value
            if not series:
                raise ValueError(f"empty series for WI-{fips3}/{variable}")
            return series
        except Exception as e:  # noqa: BLE001 - deliberate: retry then report
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"WI-{fips3}/{variable} failed after retries: {last_err}")


def summarize(series: dict) -> dict:
    baseline = [v for y, v in series.items() if BASELINE_START <= y <= BASELINE_END]
    recent = [v for y, v in series.items() if RECENT_START <= y <= RECENT_END]
    if len(baseline) < 40 or len(recent) < 12:
        raise ValueError(f"insufficient coverage: baseline n={len(baseline)}, recent n={len(recent)}")
    baseline_mean = sum(baseline) / len(baseline)
    recent_mean = sum(recent) / len(recent)
    ratio = recent_mean / baseline_mean if baseline_mean else None
    return {
        "baseline_mean": round(baseline_mean, 2),
        "recent_mean": round(recent_mean, 2),
        "ratio": round(ratio, 4) if ratio is not None else None,
        "pct_change": round((ratio - 1.0) * 100, 1) if ratio is not None else None,
        "n_baseline_years": len(baseline),
        "n_recent_years": len(recent),
    }


def main() -> int:
    counties = {}
    failures = []
    total = len(WI_COUNTY_FIPS_3DIGIT)
    for i, (county, fips3) in enumerate(sorted(WI_COUNTY_FIPS_3DIGIT.items()), 1):
        entry = {}
        for variable in VARIABLES:
            try:
                series = fetch_series(fips3, variable)
                entry[variable] = summarize(series)
            except Exception as e:  # noqa: BLE001
                failures.append(f"{county}/{variable}: {e}")
            time.sleep(0.2)
        counties[county] = entry
        if i % 12 == 0:
            print(f"  {i}/{total} counties fetched")

    if failures:
        print("FAILED - snapshot NOT written. Missing series:")
        for f in failures:
            print("  " + f)
        return 1

    snapshot = {
        "metadata": {
            "source": "NOAA NCEI nClimDiv county time series (Climate at a Glance county tool)",
            "source_url": f"{BASE_URL}/WI-<fips>/<var>/12/12/{BASELINE_START}-{RECENT_END}.json",
            "dataset_reference": "NOAA Monthly U.S. Climate Divisional Database (nClimDiv), county aggregation",
            "method": (
                f"Observed annual county values. Trend = mean of {RECENT_START}-{RECENT_END} "
                f"divided by mean of {BASELINE_START}-{BASELINE_END}. No modeling, no projection: "
                "these are measured values from the same dataset WICCI uses for its published "
                "Wisconsin trend maps."
            ),
            "variables": VARIABLES,
            "baseline_period": f"{BASELINE_START}-{BASELINE_END}",
            "recent_period": f"{RECENT_START}-{RECENT_END}",
            "generated": date.today().isoformat(),
            "counties": len(counties),
        },
        "counties": counties,
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(snapshot, f, indent=2, sort_keys=True)
    print(f"Wrote {OUTPUT_PATH} ({len(counties)} counties)")
    ratios = [c["pcp"]["ratio"] for c in counties.values() if c.get("pcp", {}).get("ratio")]
    print(f"Precip ratio range: {min(ratios):.3f} to {max(ratios):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
