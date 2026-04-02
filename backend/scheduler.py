import logging
import time
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
)
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

# How often the pipeline runs (in minutes)
INTERVAL_MINUTES = 30


def job_listener(event):
    """
    Listens to scheduler events and logs success or failure for every run.
    """
    if event.exception:
        logger.error(
            f"[SCHEDULER] Pipeline run FAILED at "
            f"{event.scheduled_run_time} — {event.exception}"
        )
    else:
        logger.info(
            f"[SCHEDULER] Pipeline run completed successfully at "
            f"{event.scheduled_run_time}"
        )


def start_scheduler():
    logger.info("=" * 60)
    logger.info("[SCHEDULER] CyberSec News Feed Agent starting...")
    logger.info(f"[SCHEDULER] Pipeline will run every {INTERVAL_MINUTES} minutes.")
    logger.info("=" * 60)

    # Run the pipeline once immediately on startup
    logger.info("[SCHEDULER] Running initial pipeline on startup...")
    try:
        result = run_pipeline()
        logger.info(f"[SCHEDULER] Startup run complete: {result}")
    except Exception as e:
        logger.error(f"[SCHEDULER] Startup run failed: {e}")

    # Set up the scheduled job
    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    scheduler.add_job(
        func=run_pipeline,
        trigger="interval",
        minutes=INTERVAL_MINUTES,
        id="cybersec_pipeline",
        name="CyberSec pipeline: fetch + tag + alert",
        misfire_grace_time=60,
        coalesce=True,
    )

    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    logger.info(
        f"[SCHEDULER] Next run scheduled in {INTERVAL_MINUTES} minutes."
    )
    logger.info("[SCHEDULER] Press CTRL+C to stop.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("[SCHEDULER] Scheduler stopped by user.")
        scheduler.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    start_scheduler()