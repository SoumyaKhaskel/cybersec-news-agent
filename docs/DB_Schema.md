Phase 1 — Architecture diagram
Data flow (fetch → dedupe → AI → DB → API → UI → alert) as a diagram. DONE
Phase 1 — DB schema doc

DB schema (what gets stored per article)
Column	Type	Purpose
id	INTEGER PK	Auto-increment
url_hash	TEXT UNIQUE	Dedup key — SHA-256 of URL
title	TEXT	Original article headline
source	TEXT	CISA / Krebs / THN etc.
url	TEXT	Link to original article
ai_summary	TEXT	2-sentence AI-generated summary
severity	TEXT	Critical / High / Medium / Low
attack_type	TEXT	Ransomware / Phishing etc.
iocs	JSON	Extracted IPs, CVEs, domains, hashes
published_at	DATETIME	Original article publish time
fetched_at	DATETIME	When your pipeline grabbed it
alerted	BOOLEAN	Whether Telegram alert was sent


Phase 2 — AI prompt doc (PENDING NEXT)
