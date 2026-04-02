import os
import sys
import logging


# ─────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ─────────────────────────────────────────────────────────────
# LOGGING — safe setup with fallback to console-only
# ─────────────────────────────────────────────────────────────
def setup_logging():
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler("logs/run.log"))
    except Exception:
        pass  # If file logging fails, console logging still works

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
    )

setup_logging()
logger = logging.getLogger(__name__)


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

INTERVAL_MINUTES = 30


def job_listener(event):
    if event.exception:
        logger.error(f"[SCHEDULER] Pipeline job FAILED: {event.exception}")
    else:
        logger.info("[SCHEDULER] Pipeline job completed successfully.")


def start_background_scheduler():
    logger.info("[SCHEDULER] Starting background scheduler...")

    from backend.db import init_db
    from backend.pipeline import run_pipeline

    
    try:
        init_db()
        logger.info("[SCHEDULER] Database initialised.")
    except Exception as e:
        logger.error(f"[SCHEDULER] DB init failed: {e}")

    
    try:
        result = run_pipeline()
        logger.info(f"[SCHEDULER] Startup pipeline complete: {result}")
    except Exception as e:
        logger.error(f"[SCHEDULER] Startup pipeline failed: {e}")

    from backend.pipeline import run_pipeline as _rp

    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(
        func=_rp,
        trigger="interval",
        minutes=INTERVAL_MINUTES,
        id="cybersec_pipeline",
        name="CyberSec: fetch + tag + alert",
        misfire_grace_time=120,
        coalesce=True,
    )
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()

    logger.info(
        f"[SCHEDULER] Background scheduler running — "
        f"next run in {INTERVAL_MINUTES} minutes."
    )
    return scheduler


# ─────────────────────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────────────────────
from backend.api import app  # noqa: E402

try:
    _scheduler = start_background_scheduler()
except Exception as e:
    logger.error(f"[SCHEDULER] Failed to start scheduler: {e}")
    logger.warning("[SCHEDULER] API will still serve — scheduler disabled.")
