"""
Standalone scheduler-runner entrypoint.

Runs as a dedicated Render background worker service (see render.yaml,
service `cara-scheduler`). Does NOT pull in Flask, blueprints, error
handlers, or any request-handling code -- just enough to run the
data refresh loop and persist state to Postgres.

Boot sequence:

  1. Configure logging to stdout (Render captures stdout as service logs).
  2. Try to acquire the Postgres advisory lock that elects the single
     scheduler-runner across the whole deployment. If another process
     already holds it (deploy overlap, accidental worker scale-up,
     local dev with embedded mode still running), exit cleanly with
     code 0 -- the other process will keep the refreshes going.
  3. Install SIGTERM/SIGINT handlers so Render's graceful-shutdown
     signal on deploy stops the loop cleanly instead of leaving a
     half-finished refresh in 'in_progress' state.
  4. Initialize the in-memory scheduler config and call scheduler_loop()
     on the main thread. The loop itself writes heartbeats and
     per-source status to Postgres on every tick.

Run locally for testing:
    DATABASE_URL=postgres://... python -m utils.run_scheduler
"""

import logging
import os
import signal
import sys
import threading

# Logging setup BEFORE importing any utils that grab a logger, so the
# basicConfig call actually wins.
logging.basicConfig(
    level=os.environ.get("SCHEDULER_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("scheduler_runner")


def _install_signal_handlers(stop_event: threading.Event) -> None:
    """Translate SIGTERM/SIGINT into a graceful stop. Render sends
    SIGTERM on deploy and gives ~30 seconds before SIGKILL."""

    def _handler(signum, frame):
        logger.info("Received signal %s; requesting scheduler stop", signum)
        # Flip the data_refresh_scheduler's running flag so the loop
        # exits at the top of its next iteration. Imported lazily so a
        # signal that arrives during boot doesn't NameError.
        try:
            from utils import data_refresh_scheduler as drs
            drs._scheduler_running = False
            # Wake the loop out of Event.wait(timeout=300) so it exits
            # within Render's SIGTERM grace window. Without this the
            # process would sleep up to 5 minutes before noticing the
            # flag flipped, well past the SIGKILL deadline.
            drs._scheduler_wakeup.set()
        except Exception as e:
            logger.warning("Could not flip scheduler_running on signal: %s", e)
        stop_event.set()

    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)


def main() -> int:
    logger.info("=== CARA scheduler-runner starting ===")

    # Verify required env. Fail loudly rather than silently no-op.
    if not os.environ.get("DATABASE_URL"):
        logger.critical("DATABASE_URL is required; exiting")
        return 2

    from utils import scheduler_state_store as store

    # Single-runner election via Postgres advisory lock. None means
    # another process already owns it (healthy redundancy, exit 0).
    # An exception means we could not even query Postgres -- that is
    # a real failure and we exit non-zero so Render restarts us.
    try:
        lock_conn = store.try_acquire_runner_lock()
    except Exception as e:
        logger.critical("Could not query scheduler lock: %s", e, exc_info=True)
        return 1
    if lock_conn is None:
        logger.info(
            "Another scheduler-runner holds the advisory lock; "
            "exiting cleanly so Render does not flag this as a crash"
        )
        return 0

    stop_event = threading.Event()
    _install_signal_handlers(stop_event)

    try:
        from utils.data_refresh_scheduler import (
            initialize,
            start_scheduler,
        )

        logger.info("Initializing scheduler config and status")
        initialize()

        # Run the loop on the MAIN thread, not a background thread.
        # The runner process has no other job -- main-thread execution
        # means a fatal exception surfaces as a non-zero exit and
        # Render restarts the service, which is exactly what we want.
        logger.info("Starting scheduler loop on main thread")
        start_scheduler(run_in_background=False)

        logger.info("Scheduler loop exited cleanly")
        return 0

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt; shutting down")
        return 0
    except Exception as e:
        logger.critical("Scheduler-runner crashed: %s", e, exc_info=True)
        return 1
    finally:
        store.release_runner_lock(lock_conn)


if __name__ == "__main__":
    sys.exit(main())
