"""
Loader for the DOE/ORNL EAGLE-I electrical outage seed artifact.

The artifact (data/electrical/eagle_i_county_outages.json) is built
offline by scripts/build_eagle_i_seed.py from the public EAGLE-I
county-level recorded outage dataset (15-minute resolution,
2014-present). This module only reads the local JSON file; it performs
no HTTP and is therefore safe on the cache-only request path.
"""

import json
import logging
import os
import threading
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_SEED_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "electrical", "eagle_i_county_outages.json")

_lock = threading.Lock()
_cache: Optional[Dict] = None
_load_failed = False


def _load() -> Optional[Dict]:
    global _cache, _load_failed
    if _cache is not None or _load_failed:
        return _cache
    with _lock:
        if _cache is not None or _load_failed:
            return _cache
        try:
            with open(_SEED_PATH) as fh:
                _cache = json.load(fh)
            logger.info(
                "Loaded EAGLE-I outage seed: %d counties, build %s",
                len(_cache.get("counties", {})),
                _cache.get("metadata", {}).get("build_date"))
        except Exception as exc:
            logger.warning("EAGLE-I outage seed unavailable: %s", exc)
            _load_failed = True
    return _cache


def get_outage_metrics(county_name: str) -> Optional[Dict]:
    """Return the EAGLE-I metrics dict for a county, or None."""
    data = _load()
    if not data:
        return None
    return data.get("counties", {}).get(county_name)


def get_metadata() -> Optional[Dict]:
    data = _load()
    return data.get("metadata") if data else None
