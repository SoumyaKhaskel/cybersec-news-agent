# CyberSec News Feed Agent

An autonomous AI-powered cybersecurity threat intelligence agent that fetches, summarises, severity-tags, and displays the latest cybersecurity news — with instant Telegram alerts for Critical threats.

**Live dashboard:** https://YOUR_VERCEL_URL.vercel.app  
**Live API:** https://YOUR_RAILWAY_URL.up.railway.app/docs

---

## What it does

- Fetches cybersecurity news every 30 minutes from CISA, TheHackerNews, Krebs on Security, and BleepingComputer
- Deduplicates articles using SHA-256 URL hashing so no story appears twice
- Sends each article to an AI model (Groq / Llama 3.1 8B) for a 2-sentence summary, severity tag, and attack type classification
- Stores everything in SQLite with full schema
- Serves the data via a FastAPI REST API with filtering, search, and pagination
- Displays articles on a dark-themed dashboard with severity colour coding
- Sends instant Telegram alerts when a Critical severity article is detected
- Runs fully autonomously in the cloud — no manual input required

---

## Screenshot

![Dashboard Screenshot](docs/screenshot.png)

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| AI summarisation | Groq API — Llama 3.1 8B (free tier) |
| Data sources | CISA RSS, TheHackerNews RSS, Krebs RSS, BleepingComputer RSS |
| Database | SQLite |
| Backend API | FastAPI + Uvicorn |
| Scheduler | APScheduler |
| Alerts | Telegram Bot API |
| Frontend | Vanilla HTML + CSS + JavaScript |
| Backend deploy | Railway (free tier) |
| Frontend deploy | Vercel (free tier) |

**Total running cost: $0**

---

## Project structure

```
cybersec-news-agent/
├── main.py                  Entry point — starts API + scheduler together
├── Procfile                 Railway start command
├── railway.json             Railway deploy config
├── requirements.txt
│
├── backend/
│   ├── fetcher.py           RSS fetch + deduplication
│   ├── ai_tagger.py         Groq API summarisation + tagging
│   ├── tagger_runner.py     Batch tags all untagged articles
│   ├── pipeline.py          Orchestrates fetch → tag → alert
│   ├── scheduler.py         Standalone scheduler (for local use)
│   ├── alert.py             Telegram bot alerts
│   ├── api.py               FastAPI endpoints
│   ├── db.py                SQLite database layer
│   └── models.py            Pydantic response models
│
├── frontend/
│   ├── index.html           Dashboard UI
│   ├── style.css            Dark theme styling
│   └── app.js               API calls + card rendering
│
└── docs/                    Full project documentation
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Server health check |
| GET | /feed | Paginated feed with severity + search filters |
| GET | /feed/critical | Critical articles only |
| GET | /stats | Article counts by severity (last 24h) |
| GET | /docs | Interactive API documentation (Swagger) |

---

## Run locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_GITHUB_USERNAME/cybersec-news-agent.git
cd cybersec-news-agent

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your keys
# See .env.example for required variables

# 5. Start the app (API + scheduler together)
uvicorn main:app --reload --port 8000

# 6. Open the dashboard
# Open frontend/index.html in your browser
```

---

## Environment variables

Create a `.env` file in the root folder:

```
GROQ_API_KEY=your_groq_key_here
NEWS_API_KEY=your_newsapi_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

- **Groq API key** — free at console.groq.com
- **NewsAPI key** — free at newsapi.org
- **Telegram bot** — create via @BotFather on Telegram

---

## Built in 5 phases

| Phase | What was built | Hours |
|---|---|---|
| 1 | RSS fetcher, deduplication, SQLite DB | ~6 hrs |
| 2 | Groq AI summarisation + severity tagging | ~4 hrs |
| 3 | FastAPI backend with filters and pagination | ~4 hrs |
| 4 | APScheduler automation + Telegram alerts | ~3 hrs |
| 5 | Frontend dashboard + Railway/Vercel deploy | ~4 hrs |

**Total: ~21 hours**

---

## Future improvements

- IOC extractor — pull CVE IDs, IPs, domains from articles
- Personal watchlist — filter by keywords relevant to your stack
- Weekly AI digest — auto-generate Monday briefing
- Inline URL/file scanner tab — VirusTotal integration
- Chrome extension — right-click any link to scan

---

*Built by Soumya — BlaZeFury | Completed: [2.04.26]*
