from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from backend.db import (
    get_articles_filtered,
    get_stats_last_24h,
    get_total_count,
    get_articles,
)
from backend.models import (
    ArticleOut,
    FeedResponse,
    StatsResponse,
    HealthResponse,
)

app = FastAPI(
    title="CyberSec News Feed API",
    description="AI-powered cybersecurity news aggregator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/feed", response_model=FeedResponse)
def get_feed(
    severity: Optional[str] = Query(
        default=None,
        description="Filter by severity: Critical, High, Medium, Low"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search in title and summary"
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    valid_severities = {"Critical", "High", "Medium", "Low"}
    if severity and severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity. Must be one of: {valid_severities}"
        )

    articles = get_articles_filtered(
        severity=severity,
        search=search,
        limit=limit,
        offset=offset,
    )
    total = get_total_count(severity=severity)

    return {
        "total":    total,
        "limit":    limit,
        "offset":   offset,
        "articles": articles,
    }


@app.get("/feed/critical", response_model=FeedResponse)
def get_critical_feed(limit: int = Query(default=20, ge=1, le=100)):
    articles = get_articles_filtered(severity="Critical", limit=limit)
    total    = get_total_count(severity="Critical")
    return {"total": total, "limit": limit, "offset": 0, "articles": articles}


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    return get_stats_last_24h()


@app.get("/articles/latest", response_model=list[ArticleOut])
def get_latest(limit: int = Query(default=10, ge=1, le=50)):
    return get_articles(limit=limit)
