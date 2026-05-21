"""
Quarterly source URL re-verification for CARA Action Plan citations.

Walks data/action_plans/_sources.yaml, fetches each cited URL, and reports:
  - HTTP status (or network error)
  - Final URL after redirects
  - Content hash, compared against the last stored hash to detect drift

Usage from the project root:

  python scripts/verify_action_plan_sources.py
      Read-only check. Prints a per-source table and a summary. Exits 0 if
      every source returned HTTP 200; exits 1 otherwise.

  python scripts/verify_action_plan_sources.py --bump
      For every source that returned HTTP 200, update the `verified` date
      in _sources.yaml to today. Existing hash baselines are refreshed only
      when the URL passed; on drift the previous hash is kept so the next
      reviewer sees the same drift signal until they ack it.

  python scripts/verify_action_plan_sources.py --log
      Append a dated round-summary section to _research_log.md.

  python scripts/verify_action_plan_sources.py --bump --log
      Standard quarterly run when every URL is healthy: bumps verified
      dates and writes the log entry in one pass.

Design notes:
  - This script never imports the Flask app. It is safe to run from a
    plain shell or from a scheduler hook without touching the cache or
    the request path.
  - URL fetches use a 20-second timeout, a descriptive User-Agent, and
    follow up to 5 redirects. The script does not retry; transient
    failures should be re-run by the operator.
  - Content hashes are stored alongside the data, in
    data/action_plans/_source_hashes.json, so drift detection survives
    across runs without needing a database.
  - Hash drift is reported as a soft signal, not a failure. Government
    landing pages frequently swap minor surrounding content (news
    callouts, footer dates) without changing the substantive guidance.
    A human reviewer decides whether drift warrants re-reading the page.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import yaml

try:
    import requests
except ImportError:
    print("ERROR: 'requests' is required. Install with: pip install requests")
    sys.exit(2)


ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "data" / "action_plans" / "_sources.yaml"
HASHES_PATH = ROOT / "data" / "action_plans" / "_source_hashes.json"
RESEARCH_LOG_PATH = ROOT / "data" / "action_plans" / "_research_log.md"

USER_AGENT = (
    "CARA-SourceVerifier/1.0 (+Wisconsin public-health risk assessment; "
    "quarterly citation re-verification)"
)
TIMEOUT_SECONDS = 20
MAX_REDIRECTS = 5


def load_sources() -> dict:
    with SOURCES_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_hashes() -> dict:
    if not HASHES_PATH.exists():
        return {}
    with HASHES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_hashes(hashes: dict) -> None:
    HASHES_PATH.write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def fetch(url: str) -> dict:
    headers = {"User-Agent": USER_AGENT}
    try:
        session = requests.Session()
        session.max_redirects = MAX_REDIRECTS
        resp = session.get(
            url,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=True,
        )
        body = resp.content or b""
        return {
            "ok": resp.status_code == 200,
            "status": resp.status_code,
            "final_url": resp.url,
            "hash": hashlib.sha256(body).hexdigest(),
            "error": None,
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status": None,
            "final_url": None,
            "hash": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _verify_one(item: tuple) -> dict:
    source_id, entry, prior = item
    url = entry.get("url")
    if not url:
        return {
            "id": source_id,
            "url": None,
            "ok": False,
            "status": None,
            "final_url": None,
            "hash": None,
            "error": "missing url field",
            "drift": False,
            "prior_hash": prior,
        }
    result = fetch(url)
    result["id"] = source_id
    result["url"] = url
    result["prior_hash"] = prior
    result["drift"] = bool(prior and result["hash"] and prior != result["hash"])
    return result


def verify_all(sources: dict, max_workers: int = 10) -> list:
    prior_hashes = load_hashes()
    items = [
        (sid, entry, prior_hashes.get(sid))
        for sid, entry in sources.items()
    ]
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(_verify_one, items))
    order = {sid: i for i, sid in enumerate(sources.keys())}
    results.sort(key=lambda r: order[r["id"]])
    return results


def print_report(results: list) -> None:
    print()
    print(f"{'SOURCE_ID':<32} {'STATUS':<8} {'DRIFT':<6} URL")
    print("-" * 100)
    for r in results:
        status = str(r["status"]) if r["status"] is not None else "ERR"
        drift = "yes" if r["drift"] else "no" if r["hash"] else "-"
        url = r["url"] or "(missing)"
        print(f"{r['id']:<32} {status:<8} {drift:<6} {url}")
        if r["error"]:
            print(f"    error: {r['error']}")
        if r["final_url"] and r["url"] and r["final_url"] != r["url"]:
            print(f"    redirected to: {r['final_url']}")
    print()
    ok = sum(1 for r in results if r["ok"])
    drift = sum(1 for r in results if r["drift"])
    failed = sum(1 for r in results if not r["ok"])
    print(
        f"Summary: {ok} ok, {failed} failed, {drift} with content drift, "
        f"{len(results)} total."
    )


def bump_verified_dates(results: list, today: str) -> int:
    raw = SOURCES_PATH.read_text(encoding="utf-8")
    lines = raw.splitlines()
    sources = load_sources().get("sources", {})

    ok_ids = {r["id"] for r in results if r["ok"]}
    if not ok_ids:
        return 0

    source_keys = list(sources.keys())
    bumped = 0
    current_source = None
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if (
            indent == 2
            and stripped.endswith(":")
            and stripped[:-1] in source_keys
        ):
            current_source = stripped[:-1]
            continue
        if current_source in ok_ids and stripped.startswith("verified:"):
            prefix = line[: len(line) - len(stripped)]
            lines[i] = f'{prefix}verified: "{today}"'
            bumped += 1
    SOURCES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return bumped


def update_hash_store(results: list) -> None:
    prior = load_hashes()
    for r in results:
        if r["ok"] and r["hash"]:
            if r["id"] not in prior or not r["drift"]:
                prior[r["id"]] = r["hash"]
    save_hashes(prior)


def append_research_log(results: list, today: str) -> None:
    ok = sum(1 for r in results if r["ok"])
    drift = [r for r in results if r["drift"]]
    failed = [r for r in results if not r["ok"]]

    section = []
    section.append("")
    section.append(f"## {today} quarterly re-verification round")
    section.append("")
    section.append(
        f"Ran `scripts/verify_action_plan_sources.py` against "
        f"{len(results)} sources. Result: {ok} returned HTTP 200, "
        f"{len(failed)} failed, {len(drift)} showed content drift since "
        f"the previous round."
    )
    section.append("")
    if failed:
        section.append("Failed URLs requiring reviewer action:")
        section.append("")
        for r in failed:
            err = r["error"] or f"HTTP {r['status']}"
            section.append(f"- {r['id']}: {err} ({r['url']})")
        section.append("")
    if drift:
        section.append(
            "Content drift detected (substantive review recommended; "
            "page body changed since the last recorded hash):"
        )
        section.append("")
        for r in drift:
            section.append(f"- {r['id']}: {r['url']}")
        section.append("")
    if not failed and not drift:
        section.append(
            "All cited URLs resolved with HTTP 200 and no content drift "
            "since the previous round. Verified dates in `_sources.yaml` "
            "bumped to today."
        )
        section.append("")

    with RESEARCH_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write("\n".join(section).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bump",
        action="store_true",
        help="Update verified dates in _sources.yaml for sources that "
             "returned HTTP 200.",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Append a round-summary section to _research_log.md.",
    )
    parser.add_argument(
        "--source",
        help="Verify only the given source id (useful for spot checks).",
    )
    args = parser.parse_args()

    raw = load_sources()
    sources = raw.get("sources") or {}
    if not sources:
        print("ERROR: no sources found in _sources.yaml", file=sys.stderr)
        return 2

    if args.source:
        if args.source not in sources:
            print(
                f"ERROR: source id '{args.source}' not found",
                file=sys.stderr,
            )
            return 2
        sources = {args.source: sources[args.source]}

    print(f"Verifying {len(sources)} action-plan source URL(s)...")
    results = verify_all(sources)
    print_report(results)

    today = date.today().isoformat()

    if args.bump:
        bumped = bump_verified_dates(results, today)
        update_hash_store(results)
        print(f"Bumped verified date to {today} for {bumped} source(s).")

    if args.log:
        append_research_log(results, today)
        print(f"Appended round summary to {RESEARCH_LOG_PATH.name}.")

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
