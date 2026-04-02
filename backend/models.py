from pydantic import BaseModel
from typing import Optional, List


class ArticleOut(BaseModel):
    id:           int
    title:        str
    source:       str
    url:          str
    ai_summary:   Optional[str] = None
    severity:     Optional[str] = None
    attack_type:  Optional[str] = None
    iocs:         Optional[str] = None
    published_at: Optional[str] = None
    fetched_at:   Optional[str] = None

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    total:    int
    limit:    int
    offset:   int
    articles: List[ArticleOut]


class StatsResponse(BaseModel):
    Critical: int
    High:     int
    Medium:   int
    Low:      int
    total:    int


class HealthResponse(BaseModel):
    status:  str
    version: str