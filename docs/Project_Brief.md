# Project Brief — CyberSec News Feed Agent

## Problem
I currently search multiple cybersecurity sites manually.

## Goal
AI agent that fetches, summarises, tags, and displays cybersec news.

## Tech stack
Python 3.11, feedparser, SQLite, FastAPI, APScheduler, Claude API

## Phase 1 success criteria
- RSS fetcher from 4+ sources
- Deduplication working
- Articles in SQLite
- Log file writing

## PHASE 2
Groq → works → return result
     ↓ fails
Retry (3 times)
     ↓ still fails
Gemini fallback → works → return result
     ↓ fails
Return default safe output


## Phase 3 
FastAPI auto generates interactive API docs at http://127.0.0.1:8000/docs everyendpoint test in browser UI possible.

uvicorn is the server that runs FastAPI app. The --reload flag makes it auto-restart when you save any .py file  essential during development so you don't have to restart manually after every change.

## Phase 4&5
 The frontend talks to your local API at localhost:8000. Once it works locally, deployment just means changing the API URL to your Railway URL — nothing else changes.

## Status
Phase 2: COMPLETE TODAY 31-3-2026
