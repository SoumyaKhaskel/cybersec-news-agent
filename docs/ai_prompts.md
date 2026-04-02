# AI Prompts — CyberSec News Feed Agent

## Provider: Groq (free tier)
## Model: llama-3.1-8b-instant
## Cost: $0 — 14,400 requests/day free

## Fallback provider: Google Gemini 1.5 Flash
## Fallback cost: $0 — 1,500 requests/day free

## Why Groq over Anthropic?
No credit card required. 14,400 free req/day.
Sufficient for: 50 articles x 48 runs/day = 2,400 tags/day max.

## System prompt
You are a cybersecurity analyst. Return ONLY valid JSON.
No explanation. No markdown fences.

## Severity scale
Critical : active exploitation, zero-day in the wild, nation-state
High     : unpatched CVE with PoC, major breach confirmed
Medium   : patched vulnerability, advisory, general warning
Low      : research, general news, no active threat

## Temperature: 0.1 (keeps output deterministic)
## Max tokens: 400 (enough for full JSON response)

## Phase 2 completed: [31.03.26]