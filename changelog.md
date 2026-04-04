# Changelog — CyberSec News Feed Agent

## [1.0.0] — [DATE]

### Phase 1 — Foundation
- RSS fetcher for CISA, TheHackerNews, Krebs, BleepingComputer
- SHA-256 URL deduplication
- SQLite database with full article schema
- Run logging to logs/run.log

### Phase 2 — AI Brain
- Groq API integration (Llama 3.1 8B, free tier)
- AI summarisation — 2-sentence plain English summaries
- Severity tagging: Critical / High / Medium / Low
- Attack type classification: Ransomware / Phishing / Zero-day etc
- Structured JSON output with validation and retry logic

### Phase 3 — API Layer
- FastAPI backend with 4 endpoints
- Filtering by severity and keyword search
- Pagination support
- Pydantic response models
- CORS enabled for frontend access

### Phase 4 — Automation and Alerts
- APScheduler running pipeline every 30 minutes
- Telegram bot alerts for Critical severity articles
- Duplicate alert prevention via alerted flag in DB
- main.py combining API + scheduler for single-command startup

### Phase 5 — Frontend and Deployment
- Vanilla JS dashboard with severity-coded article cards
- Stats bar, filter buttons, search, auto-refresh
- Backend deployed to Railway (free tier)
- Frontend deployed to Vercel (free tier)
- Full project documentation complete