import logging
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from backend.pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

INTERVAL_MINUTES = 30


def job_listener(event):
    if event.exception:
        logger.error(f"[SCHEDULER] Job FAILED: {event.exception}")
    else:
        logger.info("[SCHEDULER] Pipeline run completed successfully.")


def start_background_scheduler():
    """
    Starts the scheduler in the background so FastAPI can run in the main thread.
    Used when deploying to Railway / Render.
    """
    logger.info("[SCHEDULER] Starting background scheduler...")

    # Run once on startup
    try:
        result = run_pipeline()
        logger.info(f"[SCHEDULER] Startup pipeline: {result}")
    except Exception as e:
        logger.error(f"[SCHEDULER] Startup pipeline failed: {e}")

    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(
        func=run_pipeline,
        trigger="interval",
        minutes=INTERVAL_MINUTES,
        id="cybersec_pipeline",
        misfire_grace_time=60,
        coalesce=True,
    )
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()
    logger.info(
        f"[SCHEDULER] Background scheduler running — "
        f"next run in {INTERVAL_MINUTES} minutes."
    )
    return scheduler


# This is imported by uvicorn when deploying
from backend.api import app  # noqa: E402

# Start the scheduler when this module is loaded
_scheduler = start_background_scheduler()