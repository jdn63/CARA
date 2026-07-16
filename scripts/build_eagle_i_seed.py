"""
Build the EAGLE-I electrical outage seed artifact for CARA.

Downloads the DOE/ORNL EAGLE-I recorded outage dataset (county level,
15-minute resolution) from the public figshare repository backing the
Nature Scientific Data 2024 paper "A dataset of recorded electricity
outages by United States county 2014-2022" (updated annually through
2025), filters to Wisconsin counties, and aggregates to per-county
annual outage metrics. Output:

    data/electrical/eagle_i_county_outages.json

Metrics per county:
  - customer_hours_out_per_year: mean annual sum of customer-hours out
    (customers_out x 0.25h per 15-min interval)
  - hours_per_customer_per_year: the above divided by the county's
    modeled customer count (MCC.csv)
  - outage_interval_count_per_year: mean annual count of 15-min
    intervals with any customers out (a duration/frequency blend)
  - peak_customers_out: max simultaneous customers out across all years
  - years_covered

Exposure scoring: hours_per_customer_per_year mapped to a 0-1 score by
rank percentile among Wisconsin's 72 counties (0.15-0.95 range so no
county is scored as zero-risk or certainty).

Usage:
    python3 scripts/build_eagle_i_seed.py [--from-dir /tmp/eaglei]

With --from-dir, uses pre-filtered wi_<year>.csv files instead of
streaming the full national files (each 0.6-1.4 GB).

This is an offline build script. It is never imported by the app and
never runs on the request path.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import date

FIGSHARE_FILES = {
    2014: 42547717, 2015: 42547822, 2016: 42547825, 2017: 42547828,
    2018: 42547879, 2019: 42547885, 2020: 42547894, 2021: 42547891,
    2022: 42547897, 2023: 44574907, 2024: 53581661, 2025: 62164877,
}
MCC_FILE_ID = 42547708
FIGSHARE_URL = "https://ndownloader.figshare.com/files/{}"
DOI = "https://doi.org/10.6084/m9.figshare.24237376"

OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "electrical", "eagle_i_county_outages.json")


def stream_year_to_wi_csv(year: int, dest: str) -> None:
    """Stream one national year file, keeping only Wisconsin rows."""
    url = FIGSHARE_URL.format(FIGSHARE_FILES[year])
    curl = subprocess.Popen(["curl", "-sL", url], stdout=subprocess.PIPE,
                            text=True)
    assert curl.stdout is not None
    reader = csv.reader(curl.stdout)
    header = next(reader)
    fi = header.index("fips_code")
    with open(dest, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for row in reader:
            if row[fi].startswith("55") and len(row[fi]) == 5:
                writer.writerow(row)
    curl.wait()


def load_mcc(path: str) -> dict:
    counts = {}
    with open(path, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            fips = row["County_FIPS"].zfill(5)
            if fips.startswith("55"):
                counts[fips] = int(row["Customers"])
    return counts


def aggregate(from_dir: str) -> dict:
    per_county_year_hours = defaultdict(lambda: defaultdict(float))
    per_county_year_intervals = defaultdict(lambda: defaultdict(int))
    peak = defaultdict(int)
    names = {}
    years = []
    for year in sorted(FIGSHARE_FILES):
        path = os.path.join(from_dir, f"wi_{year}.csv")
        if not os.path.exists(path):
            stream_year_to_wi_csv(year, path)
        years.append(year)
        with open(path) as fh:
            for row in csv.DictReader(fh):
                fips = row["fips_code"]
                # 2023 file names the outage column "sum"
                raw = row.get("customers_out", row.get("sum")) or 0
                try:
                    out = float(raw)
                except ValueError:
                    continue
                names[fips] = row["county"]
                per_county_year_hours[fips][year] += out * 0.25
                per_county_year_intervals[fips][year] += 1
                if out > peak[fips]:
                    peak[fips] = int(out)
    return {
        "hours": per_county_year_hours,
        "intervals": per_county_year_intervals,
        "peak": peak, "names": names, "years": years,
    }


def build(from_dir: str) -> None:
    mcc_path = os.path.join(from_dir, "MCC.csv")
    if not os.path.exists(mcc_path):
        subprocess.run(["curl", "-sL", FIGSHARE_URL.format(MCC_FILE_ID),
                        "-o", mcc_path], check=True)
    mcc = load_mcc(mcc_path)
    agg = aggregate(from_dir)
    years = agg["years"]
    # 2025 file covers a partial year at build time; exclude the current
    # calendar year from per-year averages but keep it for peaks.
    current_year = date.today().year
    avg_years = [y for y in years if y != current_year]

    counties = {}
    for fips, name in sorted(agg["names"].items()):
        hours_by_year = agg["hours"][fips]
        mean_hours = (sum(hours_by_year.get(y, 0.0) for y in avg_years)
                      / len(avg_years))
        mean_intervals = (sum(agg["intervals"][fips].get(y, 0)
                              for y in avg_years) / len(avg_years))
        customers = mcc.get(fips)
        counties[name] = {
            "fips": fips,
            "customer_hours_out_per_year": round(mean_hours, 1),
            "modeled_customers": customers,
            "hours_per_customer_per_year": (
                round(mean_hours / customers, 3) if customers else None),
            "outage_interval_count_per_year": round(mean_intervals, 1),
            "peak_customers_out": agg["peak"][fips],
        }

    # Rank-percentile exposure score among counties with a normalized rate
    rated = [(n, c["hours_per_customer_per_year"])
             for n, c in counties.items()
             if c["hours_per_customer_per_year"] is not None]
    rated.sort(key=lambda t: t[1])
    n = len(rated)
    for rank, (name, _val) in enumerate(rated):
        pct = rank / (n - 1) if n > 1 else 0.5
        counties[name]["exposure_score"] = round(0.15 + 0.80 * pct, 3)

    payload = {
        "metadata": {
            "source": ("DOE/ORNL EAGLE-I recorded electricity outages, "
                       "county level, 15-minute resolution"),
            "source_doi": DOI,
            "years_covered": [y for y in years],
            "annual_average_years": avg_years,
            "build_date": date.today().isoformat(),
            "notes": (
                "Wisconsin rows filtered from national files. "
                "hours_per_customer_per_year = mean annual customer-hours "
                "out divided by ORNL modeled customer count (MCC). "
                "exposure_score is the rank percentile among Wisconsin "
                "counties scaled to 0.15-0.95. EAGLE-I covers roughly 92 "
                "percent of US customers; small municipal or cooperative "
                "utilities may be under-represented in early years. The "
                "current partial calendar year is excluded from annual "
                "averages."),
        },
        "counties": counties,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    print(f"Wrote {OUT_PATH}: {len(counties)} counties, "
          f"years {years[0]}-{years[-1]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-dir", default="/tmp/eaglei",
                    help="Directory holding pre-filtered wi_<year>.csv")
    args = ap.parse_args()
    build(args.from_dir)
