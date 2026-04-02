import logging
import time
from backend.db import get_untagged_articles, update_article_tags
from backend.ai_tagger import tag_article

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DELAY_BETWEEN_CALLS = 0.3

def run_tagging(batch_size=50):
    logger.info("=" * 50)
    logger.info("AI Tagging run started")

    articles = get_untagged_articles(limit=batch_size)

    if not articles:
        logger.info("No untagged articles — all up to date.")
        return 0

    logger.info(f"Found {len(articles)} untagged articles")
    tagged = 0

    for i, article in enumerate(articles, 1):
        logger.info(
            f"[{i}/{len(articles)}] {article['source']} | "
            f"{article['title'][:50]}..."
        )
        result = tag_article(
            title=article["title"],
            content=article.get("title", "")
        )
        update_article_tags(
            url_hash=article["url_hash"],
            summary=result["summary"],
            severity=result["severity"],
            attack_type=result["attack_type"],
            cves=result.get("cves", []),
            affected_products=result.get("affected_products", [])
        )
        tagged += 1
        time.sleep(DELAY_BETWEEN_CALLS)

    logger.info(f"Tagging complete — {tagged} articles tagged")
    logger.info("=" * 50)
    return tagged

if __name__ == "__main__":
    run_tagging()