"""
Persistent cache module for long-term data caching.

This module provides a key/value persistent cache for infrequently changing
datasets (e.g. County Health Rankings, CDC PLACES, SVI, disease surveillance,
the v6 dashboard context).

Storage backend: the cache is stored in the Postgres `persistent_kv_cache`
table (model: models.PersistentKvCache). Postgres is shared by the web
service and the scheduler worker, so refreshes performed by the scheduler are
immediately visible to user requests, and the cache survives routine
redeploys.

File fallback: when no Flask application/database context is available (for
example a stand-alone script run outside the app), the module transparently
falls back to the legacy file-based cache under ./data/cache so local tooling
keeps working. In the deployed app both the web and scheduler processes run
inside an app context, so they both use Postgres.

Public API (unchanged):
    get_from_persistent_cache(key, max_age_days)
    set_in_persistent_cache(key, value, expiry_days)
    clear_cache_by_prefix(prefix)
    clear_all_cache()
    get_cache_stats()
    PersistentCache  (class wrapper)
"""

import os
import pickle
import logging
import hashlib
import glob
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Constants
CACHE_DIR = "./data/cache"  # Directory used only by the file fallback
MAX_CACHE_FILE_AGE = 30  # Default maximum age in days for cache entries

# Ensure the fallback cache directory exists (harmless when DB is used)
os.makedirs(CACHE_DIR, exist_ok=True)


def _get_cache_key_hash(key: str) -> str:
    """
    Generate a stable hash for the cache key.

    Used as the Postgres primary key and as the file fallback filename, so a
    given key maps to the same slot regardless of backend.
    """
    return hashlib.md5(key.encode()).hexdigest()


def _get_db_session():
    """
    Return the SQLAlchemy session if a Flask app context is active, else None.

    Mirrors utils.data_cache_manager.get_db_session so cache reads/writes only
    touch Postgres when it is safe to do so. Returns None on any failure so
    callers fall back to the file cache.
    """
    try:
        from flask import has_app_context
        if not has_app_context():
            return None
        from core import db
        return db.session
    except Exception as e:  # pragma: no cover - defensive
        logger.debug(f"persistent_cache: no DB session available: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API (Postgres-first, file fallback)
# ---------------------------------------------------------------------------

def get_from_persistent_cache(key: str, max_age_days: int = MAX_CACHE_FILE_AGE) -> Optional[Any]:
    """
    Get a value from the persistent cache.

    Args:
        key: The cache key
        max_age_days: Maximum age in days for the entry to be considered valid

    Returns:
        The cached value, or None if not found or expired.
    """
    session = _get_db_session()
    if session is None:
        # No app/DB context (e.g. a stand-alone script). Use the file cache.
        return _file_get(key, max_age_days)

    # In app context, Postgres is the single source of truth. On a DB error we
    # return a cache miss rather than reading the per-container file cache,
    # which would reintroduce web/scheduler split-brain and mask DB failures.
    try:
        from models import PersistentKvCache

        key_hash = _get_cache_key_hash(key)
        row = session.get(PersistentKvCache, key_hash)
        if row is None:
            return None

        now = datetime.utcnow()
        if row.created_at and (now - row.created_at) > timedelta(days=max_age_days):
            logger.info(
                f"Cache for key '{key}' is older than {max_age_days} days, considering invalid"
            )
            return None
        if row.expires_at and now > row.expires_at:
            logger.info(f"Cache for key '{key}' has expired at {row.expires_at}")
            return None

        return pickle.loads(row.value)
    except Exception as e:
        logger.error(f"Error reading DB cache for key '{key}': {e}")
        try:
            session.rollback()
        except Exception:
            pass
        return None


def set_in_persistent_cache(key: str, value: Any, expiry_days: int = MAX_CACHE_FILE_AGE) -> bool:
    """
    Set a value in the persistent cache.

    Args:
        key: The cache key
        value: The value to cache (any picklable Python object)
        expiry_days: Number of days before the cache expires

    Returns:
        True if successfully cached, False otherwise.
    """
    session = _get_db_session()
    if session is None:
        # No app/DB context (e.g. a stand-alone script). Use the file cache.
        return _file_set(key, value, expiry_days)

    key_hash = _get_cache_key_hash(key)
    now = datetime.utcnow()
    expires_at = now + timedelta(days=expiry_days)
    try:
        blob = pickle.dumps(value)
    except Exception as e:
        logger.error(f"Error pickling value for cache key '{key}': {e}")
        return False

    try:
        from models import PersistentKvCache

        row = session.get(PersistentKvCache, key_hash)
        if row is not None:
            row.cache_key = key
            row.value = blob
            row.created_at = now
            row.expires_at = expires_at
        else:
            session.add(PersistentKvCache(
                key_hash=key_hash,
                cache_key=key,
                value=blob,
                created_at=now,
                expires_at=expires_at,
            ))
        session.commit()
        logger.info(f"Cached data for key '{key}' with expiry in {expiry_days} days")
        return True
    except Exception as e:
        # Likely a concurrent insert race between gunicorn workers / the
        # scheduler. Roll back and retry once as an update. On any failure we
        # return False rather than writing the per-container file cache.
        logger.warning(f"DB cache write for key '{key}' failed ({e}); retrying as update")
        try:
            session.rollback()
            from models import PersistentKvCache
            row = session.get(PersistentKvCache, key_hash)
            if row is not None:
                row.cache_key = key
                row.value = blob
                row.created_at = now
                row.expires_at = expires_at
                session.commit()
                return True
        except Exception as e2:
            logger.error(f"DB cache write retry for key '{key}' failed: {e2}")
            try:
                session.rollback()
            except Exception:
                pass
        return False


def clear_cache_by_prefix(prefix: str) -> int:
    """
    Clear all cache entries whose original key starts with the given prefix.

    Returns:
        Number of entries cleared.
    """
    session = _get_db_session()
    if session is None:
        # No app/DB context (e.g. a stand-alone script). Use the file cache.
        return _file_clear_by_prefix(prefix)

    try:
        from models import PersistentKvCache

        # Escape LIKE wildcards so the match is an exact startswith on the
        # literal prefix (cache keys legitimately contain underscores).
        escaped = prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = escaped + "%"
        rows = (
            session.query(PersistentKvCache)
            .filter(PersistentKvCache.cache_key.like(pattern, escape="\\"))
            .all()
        )
        count = 0
        for row in rows:
            session.delete(row)
            count += 1
        session.commit()
        logger.info(f"Cleared {count} cache entries with prefix '{prefix}'")
        return count
    except Exception as e:
        logger.error(f"Error clearing DB cache with prefix '{prefix}': {e}")
        try:
            session.rollback()
        except Exception:
            pass
        return 0


def clear_all_cache() -> int:
    """
    Clear all persistent cache entries.

    Returns:
        Number of entries cleared.
    """
    session = _get_db_session()
    if session is None:
        # No app/DB context (e.g. a stand-alone script). Use the file cache.
        return _file_clear_all()

    try:
        from models import PersistentKvCache

        count = session.query(PersistentKvCache).delete()
        session.commit()
        logger.info(f"Cleared all {count} persistent cache entries")
        return int(count or 0)
    except Exception as e:
        logger.error(f"Error clearing all DB cache: {e}")
        try:
            session.rollback()
        except Exception:
            pass
        return 0


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the persistent cache.

    Returns:
        Dictionary with cache statistics.
    """
    session = _get_db_session()
    if session is None:
        # No app/DB context (e.g. a stand-alone script). Use the file cache.
        return _file_stats()

    stats: Dict[str, Any] = {
        'backend': 'postgres',
        'total_entries': 0,
        'total_size_bytes': 0,
        'expired_entries': 0,
        'categories': {},
    }
    try:
        from models import PersistentKvCache

        now = datetime.utcnow()
        rows = session.query(PersistentKvCache).all()
        stats['total_entries'] = len(rows)
        for row in rows:
            size = len(row.value) if row.value is not None else 0
            stats['total_size_bytes'] += size
            if row.expires_at and now > row.expires_at:
                stats['expired_entries'] += 1
            category = row.cache_key.split('_')[0] if '_' in row.cache_key else 'unknown'
            bucket = stats['categories'].setdefault(category, {'count': 0, 'size_bytes': 0})
            bucket['count'] += 1
            bucket['size_bytes'] += size
        return stats
    except Exception as e:
        logger.error(f"Error getting DB cache stats: {e}")
        try:
            session.rollback()
        except Exception:
            pass
        return stats


class PersistentCache:
    """Class-based persistent cache for backward compatibility."""

    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, key: str, max_age_days: int = MAX_CACHE_FILE_AGE) -> Optional[Any]:
        return get_from_persistent_cache(key, max_age_days)

    def set(self, key: str, value: Any, max_age_days: int = MAX_CACHE_FILE_AGE) -> bool:
        return set_in_persistent_cache(key, value, max_age_days)

    def clear(self, prefix: str = "") -> int:
        return clear_cache_by_prefix(prefix)


# ---------------------------------------------------------------------------
# File fallback (legacy behavior, used only without an app/DB context)
# ---------------------------------------------------------------------------

def _file_get(key: str, max_age_days: int = MAX_CACHE_FILE_AGE) -> Optional[Any]:
    key_hash = _get_cache_key_hash(key)
    cache_path = os.path.join(CACHE_DIR, f"{key_hash}.cache")

    if not os.path.exists(cache_path):
        return None

    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
    if file_age > timedelta(days=max_age_days):
        logger.info(
            f"Cache file for key '{key}' is {file_age.days} days old (max: {max_age_days}), considering invalid"
        )
        return None

    try:
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
            expiry_time = data.get('expiry')
            if expiry_time and datetime.now() > expiry_time:
                logger.info(f"Cache for key '{key}' has expired at {expiry_time}")
                return None
            return data.get('value')
    except Exception as e:
        logger.error(f"Error reading file cache for key '{key}': {str(e)}")
        return None


def _file_set(key: str, value: Any, expiry_days: int = MAX_CACHE_FILE_AGE) -> bool:
    try:
        key_hash = _get_cache_key_hash(key)
        cache_path = os.path.join(CACHE_DIR, f"{key_hash}.cache")
        expiry_time = datetime.now() + timedelta(days=expiry_days)
        data = {
            'key': key,
            'value': value,
            'created': datetime.now(),
            'expiry': expiry_time,
        }
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Cached data (file) for key '{key}' with expiry in {expiry_days} days")
        return True
    except Exception as e:
        logger.error(f"Error writing file cache for key '{key}': {str(e)}")
        return False


def _file_clear_by_prefix(prefix: str) -> int:
    count = 0
    try:
        cache_files = glob.glob(os.path.join(CACHE_DIR, "*.cache"))
        for cache_path in cache_files:
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                    key = data.get('key', '')
                    if key.startswith(prefix):
                        os.remove(cache_path)
                        count += 1
            except Exception as e:
                logger.error(f"Error checking/removing cache file {cache_path}: {str(e)}")
                continue
        logger.info(f"Cleared {count} file cache entries with prefix '{prefix}'")
        return count
    except Exception as e:
        logger.error(f"Error clearing file cache with prefix '{prefix}': {str(e)}")
        return count


def _file_clear_all() -> int:
    count = 0
    try:
        cache_files = glob.glob(os.path.join(CACHE_DIR, "*.cache"))
        for cache_path in cache_files:
            try:
                os.remove(cache_path)
                count += 1
            except Exception as e:
                logger.error(f"Error removing cache file {cache_path}: {str(e)}")
                continue
        logger.info(f"Cleared all {count} file cache entries")
        return count
    except Exception as e:
        logger.error(f"Error clearing all file cache: {str(e)}")
        return count


def _file_stats() -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        'backend': 'file',
        'total_entries': 0,
        'total_size_bytes': 0,
        'average_age_days': 0,
        'oldest_entry_days': 0,
        'newest_entry_days': 0,
        'categories': {},
    }

    try:
        cache_files = glob.glob(os.path.join(CACHE_DIR, "*.cache"))
        stats['total_entries'] = len(cache_files)
        if not cache_files:
            return stats

        total_size = 0
        total_age_days = 0
        oldest_age = 0
        newest_age = float('inf')
        categories: Dict[str, Dict[str, int]] = {}
        now = datetime.now()

        for cache_path in cache_files:
            size = os.path.getsize(cache_path)
            total_size += size
            modified_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            age_days = (now - modified_time).days
            total_age_days += age_days
            oldest_age = max(oldest_age, age_days)
            newest_age = min(newest_age, age_days)
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                    key = data.get('key', '')
                    category = key.split('_')[0] if '_' in key else 'unknown'
                    bucket = categories.setdefault(category, {'count': 0, 'size_bytes': 0})
                    bucket['count'] += 1
                    bucket['size_bytes'] += size
            except Exception as _meta_exc:
                logger.debug(f"Skipping metadata analysis for cache file: {_meta_exc}")

        stats['total_size_bytes'] = total_size
        stats['average_age_days'] = total_age_days / len(cache_files) if cache_files else 0
        stats['oldest_entry_days'] = oldest_age
        stats['newest_entry_days'] = newest_age if newest_age != float('inf') else 0
        stats['categories'] = categories
        return stats
    except Exception as e:
        logger.error(f"Error getting file cache stats: {str(e)}")
        return stats
