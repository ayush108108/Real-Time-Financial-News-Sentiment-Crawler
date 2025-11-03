"""Pydantic schemas for structured crawler data."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator
from pydantic.config import ConfigDict


class RawArticle(BaseModel):
    """Intermediate representation parsed from RSS feeds."""

    source: str
    title: str
    link: HttpUrl
    summary: Optional[str]
    published_at: Optional[datetime]

    @field_validator("published_at", mode="before")
    @classmethod
    def _parse_datetime(cls, value: Optional[str]) -> Optional[datetime]:
        if value is None or isinstance(value, datetime):
            return value
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None


class ArticleSentiment(BaseModel):
    """Sentiment annotation for a news article title."""

    label: str
    score: float


class ArticleRecord(BaseModel):
    """Full record stored in persistence layer and exported."""

    source: str
    title: str
    link: HttpUrl
    summary: Optional[str]
    published_at: Optional[datetime]
    sentiment_label: str
    sentiment_score: float

    model_config = ConfigDict(from_attributes=True)
