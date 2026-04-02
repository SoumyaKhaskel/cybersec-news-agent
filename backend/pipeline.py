import logging
from backend.fetcher       import run_fetch
from backend.tagger_runner import run_tagging
from backend.alert         import run_alerts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline():
    logger.info("=" * 60)
    logger.info(">>> PIPELINE START <<<")

    # Step 1 — Fetch new articles from all RSS sources
    new_count = run_fetch()
    logger.info(f"Fetch complete: {new_count} new articles added")

    # Step 2 — AI tag all untagged articles
    tagged = run_tagging()
    logger.info(f"Tagging complete: {tagged} articles tagged")

    # Step 3 — Send Telegram alerts for Critical articles
    alerted = run_alerts()
    logger.info(f"Alerts complete: {alerted} Telegram messages sent")

    logger.info(">>> PIPELINE END <<<")
    logger.info("=" * 60)
    return {"new": new_count, "tagged": tagged, "alerted": alerted}


if __name__ == "__main__":
    result = run_pipeline()
    print(f"\nPipeline result: {result}")