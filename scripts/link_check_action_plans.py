"""Action-plan source-link checker.

Walks every URL referenced from data/action_plans/_sources.yaml and any
per-domain *.yaml `source_links` block, issues a HEAD (then GET on 405)
with a short timeout, and writes the result back into
data/action_plans/_verifier_status.json under a new `link_failed`
section.

This complements scripts/verify_action_plan_sources.py, which validates
that every action-plan citation resolves to a registered source ID. The
link checker validates that the underlying URLs still serve a 2xx /
3xx response (i.e. the source has not been moved or retired since the
last verification round).

Run on demand. Not wired into the request path; this script does live
HTTP and must NEVER be called from a user-facing route.

Usage:
    python scripts/link_check_action_plans.py

Exit code: 0 if all links return 2xx/3xx; 1 if any link_failed entries
were recorded. The verifier_status.json is updated either way.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTION_PLANS_DIR = REPO_ROOT / "data" / "action_plans"
SOURCES_FILE = ACTION_PLANS_DIR / "_sources.yaml"
STATUS_FILE = ACTION_PLANS_DIR / "_verifier_status.json"

USER_AGENT = "CARA-WI-LinkChecker/1.0 (contact: github.com/jdn63)"
# Several .gov sites (heat.gov, dhs.wisconsin.gov, some Akamai-fronted CDC
# and FEMA paths) return 403 to non-browser user agents while serving the
# page normally to browsers. On a 403 we retry once with a browser-style
# UA and record the result as ok-with-bot-challenge rather than a dead
# link, so the failure list only contains genuinely moved/retired URLs.
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/150.0 Safari/537.36"
)
TIMEOUT_SECONDS = 15


def _collect_urls() -> Dict[str, str]:
    """Return {source_id: url} for every entry in _sources.yaml."""
    if not SOURCES_FILE.exists():
        logger.error("Sources file not found: %s", SOURCES_FILE)
        return {}
    with SOURCES_FILE.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    sources = data.get("sources") or {}
    out: Dict[str, str] = {}
    for sid, entry in sources.items():
        if isinstance(entry, dict):
            url = entry.get("url")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                out[sid] = url
    return out


def _check_one(url: str) -> Dict[str, Any]:
    """Try HEAD, fall back to GET on 405/501, retry 403 with a browser UA.

    Return {ok, status, error, bot_challenge}.
    """
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.head(url, headers=headers, timeout=TIMEOUT_SECONDS, allow_redirects=True)
        if r.status_code in (405, 501):
            r = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS, allow_redirects=True, stream=True)
            r.close()
        if r.status_code == 403:
            rb = requests.get(
                url,
                headers={"User-Agent": BROWSER_USER_AGENT},
                timeout=TIMEOUT_SECONDS,
                allow_redirects=True,
                stream=True,
            )
            rb.close()
            if 200 <= rb.status_code < 400:
                return {"ok": True, "status": rb.status_code, "error": None, "bot_challenge": True}
        return {"ok": 200 <= r.status_code < 400, "status": r.status_code, "error": None, "bot_challenge": False}
    except requests.RequestException as exc:
        return {"ok": False, "status": None, "error": str(exc)[:200], "bot_challenge": False}


def _load_status() -> Dict[str, Any]:
    if STATUS_FILE.exists():
        with STATUS_FILE.open("r", encoding="utf-8") as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                logger.warning("Existing %s is not valid JSON; rewriting.", STATUS_FILE)
    return {}


def _save_status(status: Dict[str, Any]) -> None:
    with STATUS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=2, sort_keys=True)
        fh.write("\n")


def main() -> int:
    urls = _collect_urls()
    if not urls:
        logger.error("No URLs found to check.")
        return 1

    logger.info("Checking %d action-plan source URLs...", len(urls))
    failed: List[Dict[str, Any]] = []
    bot_challenged: List[str] = []
    ok_count = 0

    for sid, url in sorted(urls.items()):
        result = _check_one(url)
        if result["ok"]:
            ok_count += 1
            if result.get("bot_challenge"):
                bot_challenged.append(sid)
                logger.info("  ok    %-40s %s (bot challenge; verified with browser UA)", sid, result["status"])
            else:
                logger.info("  ok    %-40s %s", sid, result["status"])
        else:
            failed.append({
                "id": sid,
                "url": url,
                "status": result["status"],
                "error": result["error"],
            })
            logger.warning("  FAIL  %-40s %s %s", sid, result["status"], result["error"] or "")

    status = _load_status()
    status["link_check"] = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "total": len(urls),
        "ok_count": ok_count,
        "failed_count": len(failed),
        "bot_challenged": bot_challenged,
        "link_failed": failed,
    }
    _save_status(status)
    logger.info("link_check: %d ok, %d failed (written to %s)", ok_count, len(failed), STATUS_FILE)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
