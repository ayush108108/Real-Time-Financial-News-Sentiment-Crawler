"""Application configuration using Pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or defaults."""

    reuters_feed_url: str = Field(
        default="https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
        description="Reuters RSS feed providing business and finance headlines.",
    )
    cnbc_feed_url: str = Field(
        default="https://www.cnbc.com/id/100003114/device/rss/rss.html",
        description="CNBC RSS feed offering top business news.",
    )
    http_timeout_seconds: int = Field(default=15, ge=5, le=60)
    user_agent: str = Field(default="RealTimeFinancialNewsCrawler/0.1")
    sentiment_model_name: str = Field(
        default="distilbert-base-uncased-finetuned-sst-2-english",
        description="Hugging Face sentiment analysis model name.",
    )
    sentiment_device: Literal["cpu", "cuda"] | int | None = Field(
        default=None,
        description="Device identifier passed to transformers pipeline.",
    )
    database_url: str = Field(default="sqlite:///data/news.db")
    output_path: Path = Field(default=Path("output/latest.json"))

    model_config = SettingsConfigDict(
        env_prefix="CRAWLER_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
