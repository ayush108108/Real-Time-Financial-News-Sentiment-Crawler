"""End-to-end orchestration for the news sentiment crawler."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, List

from sqlalchemy.orm import Session

from .database import init_db, upsert_articles
from .exporter import write_json
from .fetcher import fetch_feeds
from .schemas import ArticleRecord, RawArticle
from .sentiment import annotate_sentiment
from .settings import Settings, get_settings


def _deduplicate(articles: Iterable[RawArticle]) -> List[RawArticle]:
    seen_links: set[str] = set()
    deduped: list[RawArticle] = []
    for article in articles:
        link = str(article.link)
        if link in seen_links:
            continue
        seen_links.add(link)
        deduped.append(article)
    return deduped


async def _run_async(settings: Settings) -> list[ArticleRecord]:
    raw_articles = await fetch_feeds(settings)
    deduped = _deduplicate(raw_articles)
    annotated = annotate_sentiment(settings, deduped)
    records = [
        ArticleRecord(
            source=raw.source,
            title=raw.title,
            link=raw.link,
            summary=raw.summary,
            published_at=raw.published_at,
            sentiment_label=sentiment.label,
            sentiment_score=sentiment.score,
        )
        for raw, sentiment in annotated
    ]
    return records


def run_pipeline(settings: Settings | None = None) -> list[ArticleRecord]:
    """Execute crawler pipeline and return article records."""

    settings = settings or get_settings()
    records = asyncio.run(_run_async(settings))
    _persist(settings, records)
    write_json(settings.output_path, records)
    return records


def _persist(settings: Settings, records: Iterable[ArticleRecord]) -> None:
    if settings.database_url.startswith("sqlite:///"):
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        if db_path.parent:
            db_path.parent.mkdir(parents=True, exist_ok=True)
    session: Session = init_db(settings.database_url)
    try:
        upsert_articles(session, records)
    finally:
        session.close()

