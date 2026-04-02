import feedparser
import hashlib
import logging
import os
from datetime import datetime
from backend.db import init_db, article_exists, insert_article

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

RSS_SOURCES = [
    {
        'name': 'CISA',
        'url': 'https://www.cisa.gov/news.xml'
    },
    {
        'name': 'TheHackerNews',
        'url': 'https://feeds.feedburner.com/TheHackersNews'
    },
    {
        'name': 'KrebsOnSecurity',
        'url': 'https://krebsonsecurity.com/feed/'
    },
    {
        'name': 'BleepingComputer',
        'url': 'https://www.bleepingcomputer.com/feed/'
    },
]

def make_hash(url):
    return hashlib.sha256(url.strip().encode()).hexdigest()

def parse_date(entry):
    for attr in ['published', 'updated', 'created']:
        if hasattr(entry, attr):
            return str(getattr(entry, attr))
    return datetime.utcnow().isoformat()

def fetch_rss(source):
    logger.info(f"Fetching: {source['name']}")
    articles = []
    try:
        feed = feedparser.parse(source['url'])
        for entry in feed.entries:
            url = entry.get('link', '')
            if not url:
                continue
            articles.append({
                'title': entry.get('title', 'No title').strip(),
                'url': url.strip(),
                'source': source['name'],
                'published_at': parse_date(entry),
                'url_hash': make_hash(url)
            })
        logger.info(f"  -> {len(articles)} articles found from {source['name']}")
    except Exception as e:
        logger.error(f"  -> Failed to fetch {source['name']}: {e}")
    return articles

def run_fetch():
    logger.info("=" * 50)
    logger.info("Pipeline started")
    init_db()
    all_articles = []
    for source in RSS_SOURCES:
        all_articles.extend(fetch_rss(source))

    new_count = 0
    skip_count = 0
    for article in all_articles:
        if article_exists(article['url_hash']):
            skip_count += 1
            continue
        try:
            insert_article(article)
            new_count += 1
            logger.info(f"  [NEW] {article['source']}: {article['title'][:60]}...")
        except Exception as e:
            logger.error(f"  [ERROR] Insert failed: {e}")

    logger.info(f"Done — {new_count} new | {skip_count} duplicates skipped")
    logger.info("=" * 50)
    return new_count

if __name__ == '__main__':
    run_fetch()