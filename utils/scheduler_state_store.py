"""
Scheduler state store.

Persists per-source scheduler state and a runner heartbeat to Postgres
so the web service (which no longer runs the scheduler under B1) can
read what the dedicated Render background worker is doing.

Design notes:

- Raw SQL via SQLAlchemy core, NOT the Flask-SQLAlchemy ORM. The
  standalone worker (utils/run_scheduler.py) must not pull in Flask,
  blueprints, error handlers, the dashboard warmer, etc. — it only
  needs DB access. Raw SQL keeps the worker boot cheap and the
  dependency graph honest.

- Schema mirrors models.SchedulerSourceStatus and models.SchedulerHeartbeat
  exactly. The web service still runs db.create_all() at boot which
  creates the same tables via the ORM declarations; this module's
  CREATE TABLE IF NOT EXISTS is a safety net for the worker-boots-first
  case on a fresh deploy.

- The advisory-lock helper (try_acquire_runner_lock) is the
  belt-and-suspenders that protects against deploy-overlap windows
  where the old worker is still finishing while the new worker boots,
  or accidental scale-up of the worker service to >1 instance.
"""

import logging
import os
import socket
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Arbitrary 64-bit constant used as the pg_advisory_lock key. Stable
# across deploys so a new runner trying to start while an old one is
# still alive will fail to acquire and exit cleanly.
SCHEDULER_RUNNER_LOCK_KEY = 8746362981037461001  # "CARA-SCHED" mnemonic

# Heartbeat is a single-row table; we always reference id=1.
HEARTBEAT_ROW_ID = 1

_engine = None
_engine_lock = threading.Lock()
_bootstrap_done = False


def _get_engine():
    """Lazy-build a NullPool engine. NullPool matches core.py so the
    worker process holds no idle connections between its 5-minute
    sleeps."""
    global _engine, _bootstrap_done
    if _engine is not None:
        return _engine
    with _engine_lock:
        if _engine is None:
            url = os.environ.get("DATABASE_URL")
            if not url:
                raise RuntimeError(
                    "DATABASE_URL not set; scheduler_state_store cannot operate"
                )
            _engine = create_engine(url, poolclass=NullPool, pool_pre_ping=True)
        if not _bootstrap_done:
            _ensure_tables(_engine)
            _bootstrap_done = True
    return _engine


def _ensure_tables(engine) -> None:
    """Create tables if they do not exist. Idempotent. Safety net for
    a worker process that boots before the web service has had a chance
    to run db.create_all() against a fresh database."""
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS scheduler_source_status (
            source_id VARCHAR(64) PRIMARY KEY,
            last_refresh TIMESTAMP NULL,
            next_refresh TIMESTAMP NULL,
            last_attempt TIMESTAMP NULL,
            status VARCHAR(16) NOT NULL DEFAULT 'pending',
            last_error TEXT NULL,
            refresh_count INTEGER NOT NULL DEFAULT 0,
            error_count INTEGER NOT NULL DEFAULT 0,
            in_progress BOOLEAN NOT NULL DEFAULT FALSE,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS scheduler_heartbeat (
            id INTEGER PRIMARY KEY,
            runner_id VARCHAR(128) NULL,
            last_beat_at TIMESTAMP NOT NULL DEFAULT NOW(),
            started_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """,
    ]
    with engine.begin() as conn:
        for stmt in ddl:
            conn.execute(text(stmt))


def runner_id() -> str:
    """hostname:pid — stable for the life of a process, changes on
    every deploy/restart so it correlates 1:1 with Render container
    rotations in logs."""
    try:
        return f"{socket.gethostname()}:{os.getpid()}"
    except Exception:
        return f"unknown:{os.getpid()}"


# ---------------------------------------------------------------------
# Status writes (called by the runner)
# ---------------------------------------------------------------------

def record_attempt_started(source_id: str) -> None:
    """Mark a source as in_progress and stamp last_attempt. Always
    advances last_attempt regardless of outcome, so a tight-retry loop
    on a persistently failing source is observable."""
    now = datetime.utcnow()
    # Provide ALL NOT NULL columns explicitly so this works whether
    # the table was created by alembic (with server defaults) or by
    # an older db.create_all() run that pre-dated the server_default
    # additions in the SQLAlchemy model.
    sql = text("""
        INSERT INTO scheduler_source_status
            (source_id, last_attempt, status, refresh_count,
             error_count, in_progress, updated_at)
        VALUES (:sid, :now, 'in_progress', 0, 0, TRUE, :now)
        ON CONFLICT (source_id) DO UPDATE SET
            last_attempt = EXCLUDED.last_attempt,
            status = 'in_progress',
            in_progress = TRUE,
            updated_at = EXCLUDED.updated_at
    """)
    try:
        with _get_engine().begin() as conn:
            conn.execute(sql, {"sid": source_id, "now": now})
    except Exception as e:
        logger.warning("record_attempt_started(%s) failed: %s", source_id, e)


def record_attempt_success(source_id: str, refresh_interval_hours: float) -> None:
    """Mark a source refresh as succeeded; advance both last_refresh
    and last_attempt, compute next_refresh, clear last_error,
    increment refresh_count."""
    now = datetime.utcnow()
    next_refresh = now + timedelta(hours=refresh_interval_hours)
    sql = text("""
        INSERT INTO scheduler_source_status
            (source_id, last_refresh, next_refresh, last_attempt,
             status, last_error, refresh_count, error_count,
             in_progress, updated_at)
        VALUES (:sid, :now, :nxt, :now, 'success', NULL, 1, 0, FALSE, :now)
        ON CONFLICT (source_id) DO UPDATE SET
            last_refresh = EXCLUDED.last_refresh,
            next_refresh = EXCLUDED.next_refresh,
            last_attempt = EXCLUDED.last_attempt,
            status = 'success',
            last_error = NULL,
            refresh_count = scheduler_source_status.refresh_count + 1,
            in_progress = FALSE,
            updated_at = EXCLUDED.updated_at
    """)
    try:
        with _get_engine().begin() as conn:
            conn.execute(sql, {"sid": source_id, "now": now, "nxt": next_refresh})
    except Exception as e:
        logger.warning("record_attempt_success(%s) failed: %s", source_id, e)


def record_attempt_failure(source_id: str, error: str) -> None:
    """Mark a refresh attempt as failed; last_refresh stays unchanged
    so the freshness reporting still shows the prior good value, but
    error_count and last_error advance so failures are visible."""
    now = datetime.utcnow()
    truncated = (error or "")[:2000]
    # All NOT NULL columns provided explicitly -- see comment in
    # record_attempt_started for rationale.
    sql = text("""
        INSERT INTO scheduler_source_status
            (source_id, last_attempt, status, last_error,
             refresh_count, error_count, in_progress, updated_at)
        VALUES (:sid, :now, 'error', :err, 0, 1, FALSE, :now)
        ON CONFLICT (source_id) DO UPDATE SET
            last_attempt = EXCLUDED.last_attempt,
            status = 'error',
            last_error = EXCLUDED.last_error,
            error_count = scheduler_source_status.error_count + 1,
            in_progress = FALSE,
            updated_at = EXCLUDED.updated_at
    """)
    try:
        with _get_engine().begin() as conn:
            conn.execute(sql, {"sid": source_id, "now": now, "err": truncated})
    except Exception as e:
        logger.warning("record_attempt_failure(%s) failed: %s", source_id, e)


# ---------------------------------------------------------------------
# Status reads (called by the web service via get_scheduler_status)
# ---------------------------------------------------------------------

def read_all_status() -> Dict[str, Dict[str, Any]]:
    """Return {source_id: {...status fields...}} for every row.
    Returns {} on DB error so callers can degrade gracefully to
    in-memory globals (legacy behavior)."""
    sql = text("""
        SELECT source_id, last_refresh, next_refresh, last_attempt,
               status, last_error, refresh_count, error_count,
               in_progress, updated_at
        FROM scheduler_source_status
    """)
    out: Dict[str, Dict[str, Any]] = {}
    try:
        with _get_engine().connect() as conn:
            for row in conn.execute(sql).mappings():
                out[row["source_id"]] = {
                    "last_refresh": row["last_refresh"].isoformat() if row["last_refresh"] else None,
                    "next_refresh": row["next_refresh"].isoformat() if row["next_refresh"] else None,
                    "last_attempt": row["last_attempt"].isoformat() if row["last_attempt"] else None,
                    "status": row["status"],
                    "last_error": row["last_error"],
                    "refresh_count": int(row["refresh_count"] or 0),
                    "error_count": int(row["error_count"] or 0),
                    "in_progress": bool(row["in_progress"]),
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                }
    except Exception as e:
        logger.warning("read_all_status failed, returning empty: %s", e)
    return out


# ---------------------------------------------------------------------
# Heartbeat
# ---------------------------------------------------------------------

def write_heartbeat() -> None:
    """Called by the runner on every loop tick. Web service reads this
    via read_heartbeat() to detect "scheduler-runner is down" without
    leaving the dashboard."""
    rid = runner_id()
    now = datetime.utcnow()
    sql = text("""
        INSERT INTO scheduler_heartbeat (id, runner_id, last_beat_at, started_at)
        VALUES (:id, :rid, :now, :now)
        ON CONFLICT (id) DO UPDATE SET
            runner_id = EXCLUDED.runner_id,
            last_beat_at = EXCLUDED.last_beat_at
    """)
    try:
        with _get_engine().begin() as conn:
            conn.execute(sql, {"id": HEARTBEAT_ROW_ID, "rid": rid, "now": now})
    except Exception as e:
        logger.warning("write_heartbeat failed: %s", e)


def read_heartbeat() -> Optional[Dict[str, Any]]:
    """Return the heartbeat row as a dict, or None if missing/error.
    Web service uses this to compute "seconds since last heartbeat"
    and surface it on the status endpoint."""
    sql = text("""
        SELECT runner_id, last_beat_at, started_at
        FROM scheduler_heartbeat WHERE id = :id
    """)
    try:
        with _get_engine().connect() as conn:
            row = conn.execute(sql, {"id": HEARTBEAT_ROW_ID}).mappings().first()
            if not row:
                return None
            now = datetime.utcnow()
            seconds_since = (now - row["last_beat_at"]).total_seconds() if row["last_beat_at"] else None
            return {
                "runner_id": row["runner_id"],
                "last_beat_at": row["last_beat_at"].isoformat() if row["last_beat_at"] else None,
                "started_at": row["started_at"].isoformat() if row["started_at"] else None,
                "seconds_since_last_beat": int(seconds_since) if seconds_since is not None else None,
            }
    except Exception as e:
        logger.warning("read_heartbeat failed: %s", e)
        return None


# ---------------------------------------------------------------------
# Advisory lock — single-runner election across processes
# ---------------------------------------------------------------------

def try_acquire_runner_lock():
    """Attempt to acquire the scheduler-runner advisory lock.

    Returns the held connection on success (caller MUST keep it alive
    for the full lifetime of the scheduler loop — releasing the
    connection releases the lock). Returns None when another process
    already owns the lock (healthy redundancy, not an error).

    Raises the underlying exception on DB connectivity / query errors
    so the caller can distinguish "lock is contended" (None, exit 0)
    from "we could not even ask Postgres" (raise, exit non-zero so
    Render surfaces a crash and restarts the worker).

    Postgres releases advisory locks automatically when the holding
    connection closes (including ungraceful exits), so crash recovery
    is built in.
    """
    # Use a raw DBAPI connection so we keep the SAME session for the
    # whole lock lifetime. SQLAlchemy's connection pooling would
    # otherwise return us to the pool and recycle the session.
    conn = _get_engine().raw_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT pg_try_advisory_lock(%s)", (SCHEDULER_RUNNER_LOCK_KEY,))
        got_it = cur.fetchone()[0]
        cur.close()
    except Exception as e:
        # Lock-query failure is NOT "lock contended". Surface as a
        # real error so the runner exits non-zero and Render restarts.
        try:
            conn.close()
        except Exception:
            pass
        logger.error("try_acquire_runner_lock query failed: %s", e, exc_info=True)
        raise

    if got_it:
        logger.info(
            "Acquired scheduler runner lock (key=%s, runner=%s)",
            SCHEDULER_RUNNER_LOCK_KEY, runner_id(),
        )
        return conn

    try:
        conn.close()
    except Exception:
        pass
    logger.info(
        "Another process holds the scheduler runner lock; exiting (runner=%s)",
        runner_id(),
    )
    return None


def release_runner_lock(conn) -> None:
    """Explicit release for graceful shutdown. Postgres would release
    on connection close anyway, but doing it explicitly makes intent
    clear in logs and lets us validate via pg_locks during shutdown."""
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_unlock(%s)", (SCHEDULER_RUNNER_LOCK_KEY,))
        cur.close()
        conn.close()
        logger.info("Released scheduler runner lock (runner=%s)", runner_id())
    except Exception as e:
        logger.warning("release_runner_lock failed: %s", e)
