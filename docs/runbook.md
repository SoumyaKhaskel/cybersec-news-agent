# Runbook — CyberSec News Feed Agent

## How to start (local development)

Activate virtual environment first (every new CMD window):
  Windows: venv\Scripts\activate
  Mac:     source venv/bin/activate

Option A — Run everything together (API + scheduler):
  uvicorn main:app --reload --port 8000

Option B — Run separately (better for debugging):
  Window 1: uvicorn backend.api:app --reload --port 8000
  Window 2: python -m backend.scheduler

## How to run pipeline manually (one-off)
  python -m backend.pipeline

## How to run only the fetcher (no AI tagging)
  python -m backend.fetcher

## How to run only AI tagging (on existing untagged articles)
  python -m backend.tagger_runner

## How to send pending Telegram alerts manually
  python -m backend.alert

## How to check logs
  Windows: type logs\run.log
  Last 50 lines: powershell Get-Content logs\run.log -Tail 50

## How to check database stats
  python -c "from backend.db import get_stats_last_24h; print(get_stats_last_24h())"

## How to add a new RSS source
  1. Open backend/fetcher.py
  2. Add a new dict to RSS_SOURCES list:
     {"name": "SourceName", "url": "https://rss-feed-url"}
  3. Save and the next pipeline run picks it up automatically.

## How to change the schedule interval
  1. Open backend/scheduler.py
  2. Change: INTERVAL_MINUTES = 30
  3. Also update in main.py: INTERVAL_MINUTES = 30
  4. Restart the scheduler.

## How to check if Telegram alerts are working
  python test_telegram.py (if you still have the file)
  OR: python -m backend.alert

## Environment variables required (.env)
  GROQ_API_KEY         — Groq free API key (groq.com)
  NEWS_API_KEY         — NewsAPI key (newsapi.org)
  TELEGRAM_BOT_TOKEN   — From @BotFather on Telegram
  TELEGRAM_CHAT_ID     — Your personal Telegram chat ID

## Phase 4 completed: [1.04.26]