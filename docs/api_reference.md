# API Reference — CyberSec News Feed

Base URL (local):  http://127.0.0.1:8000
Base URL (prod):   https://your-railway-url.up.railway.app
Interactive docs:  {base_url}/docs

## GET /health
Returns server status.

Response:
{
  "status": "ok",
  "version": "1.0.0"
}


## GET /feed
Returns paginated, filterable article feed.

Query parameters:
  severity  string   Filter by: Critical, High, Medium, Low
  search    string   Search in title and ai_summary
  limit     int      Articles per page. Default: 20. Max: 100
  offset    int      Pagination offset. Default: 0

Example:
  GET /feed?severity=Critical&limit=10
  GET /feed?search=ransomware&limit=5
  GET /feed?limit=20&offset=20

Response:
{
  "total":    58,
  "limit":    20,
  "offset":   0,
  "articles": [ { ArticleOut } ]
}


## GET /feed/critical
Shortcut for Critical severity articles only.

Example: GET /feed/critical?limit=10



## GET /stats
Returns article counts by severity for the last 24 hours.

Response:
{
  "Critical": 8,
  "High":     22,
  "Medium":   21,
  "Low":      7,
  "total":    58
}



## GET /articles/latest
Returns the N most recently fetched articles regardless of severity.

Example: GET /articles/latest?limit=10



## ArticleOut schema
{
  "id":           int,
  "title":        string,
  "source":       string,   // CISA / TheHackerNews / Krebs / BleepingComputer
  "url":          string,
  "ai_summary":   string | null,
  "severity":     string | null,   // Critical / High / Medium / Low
  "attack_type":  string | null,   // Ransomware / Phishing / Zero-day / etc
  "iocs":         string | null,   // JSON string: {cves: [], affected_products: []}
  "published_at": string | null,
  "fetched_at":   string
}



Phase 3 completed: [1.4.26]