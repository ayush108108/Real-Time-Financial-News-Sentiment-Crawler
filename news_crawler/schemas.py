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
            
        # Common RSS date formats to try
        formats = [
            # Standard RSS format with timezone
            "%a, %d %b %Y %H:%M:%S %z",
            # ISO 8601 with timezone
            "%Y-%m-%dT%H:%M:%S%z",
            # ISO 8601 with Zulu time
            "%Y-%m-%dT%H:%M:%SZ",
            # Date only
            "%Y-%m-%d",
            # Common web format
            "%Y-%m-%d %H:%M:%S",
            # With timezone offset without colon
            "%Y-%m-%d %H:%M:%S%z",
            # RFC 822/1123 format
            "%a, %d %b %Y %H:%M:%S %Z",
            # CNBC format (if different)
            "%a, %d %b %Y %H:%M:%S %z",
            # Fallback for dates like '2023-04-15T12:34:56.789Z'
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ]
        
        for fmt in formats:
            try:
                # Try with the format as-is
                return datetime.strptime(value, fmt)
            except ValueError:
                # Try stripping whitespace and trying again
                try:
                    return datetime.strptime(value.strip(), fmt)
                except (ValueError, AttributeError):
                    continue
        
        # If we get here, log the unparsable date for debugging
        print(f"Warning: Could not parse date: {value}")
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
