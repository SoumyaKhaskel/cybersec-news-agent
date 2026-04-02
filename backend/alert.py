import os
import logging
import requests
from dotenv import load_dotenv
from backend.db import get_connection

load_dotenv()
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_API_URL   = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_telegram_message(text):
    """
    Send a plain text message to your Telegram chat.
    Returns True if sent successfully, False otherwise.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("[ALERT] Telegram credentials missing in .env — skipping alert.")
        return False

    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
        if response.status_code == 200:
            logger.info("[ALERT] Telegram message sent successfully.")
            return True
        else:
            logger.error(
                f"[ALERT] Telegram send failed: {response.status_code} — {response.text}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"[ALERT] Telegram request error: {e}")
        return False


def format_alert_message(article):
    """
    Format a single article into a readable Telegram alert message.
    """
    severity    = article.get("severity",    "Unknown")
    title       = article.get("title",       "No title")
    source      = article.get("source",      "Unknown source")
    attack_type = article.get("attack_type", "Unknown")
    ai_summary  = article.get("ai_summary",  "No summary available.")
    url         = article.get("url",         "")

    severity_emoji = {
        "Critical": "🚨",
        "High":     "🔴",
        "Medium":   "🟡",
        "Low":      "🟢",
    }.get(severity, "⚪")

    message = (
        f"{severity_emoji} [{severity.upper()}] CYBERSEC ALERT\n\n"
        f"Title: {title}\n\n"
        f"Source: {source}\n"
        f"Type: {attack_type}\n\n"
        f"Summary:\n{ai_summary}\n\n"
        f"Read more: {url}"
    )
    return message


def mark_as_alerted(url_hash):
    """
    Mark an article as alerted in the DB so we never send duplicate alerts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE articles SET alerted = 1 WHERE url_hash = ?",
        (url_hash,)
    )
    conn.commit()
    conn.close()


def get_unalerted_critical_articles():
    """
    Fetch all Critical articles that have not been alerted yet.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT url_hash, title, source, url, ai_summary,
               severity, attack_type
        FROM   articles
        WHERE  severity = 'Critical'
          AND  alerted  = 0
          AND  ai_summary IS NOT NULL
        ORDER  BY fetched_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def run_alerts():
    """
    Main function: find all un-alerted Critical articles and send Telegram messages.
    Call this after every pipeline run.
    """
    articles = get_unalerted_critical_articles()

    if not articles:
        logger.info("[ALERT] No new Critical articles to alert.")
        return 0

    logger.info(f"[ALERT] Found {len(articles)} unalerted Critical articles.")
    sent_count = 0

    for article in articles:
        message = format_alert_message(article)
        success = send_telegram_message(message)

        if success:
            mark_as_alerted(article["url_hash"])
            sent_count += 1
            logger.info(
                f"[ALERT] Sent alert for: {article['title'][:60]}..."
            )
        else:
            logger.error(
                f"[ALERT] Failed to send alert for: {article['title'][:60]}..."
            )

    logger.info(f"[ALERT] {sent_count} alerts sent.")
    return sent_count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    run_alerts()