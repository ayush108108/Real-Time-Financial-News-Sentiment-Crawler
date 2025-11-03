"""Database models and helpers using SQLAlchemy."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy import Column, DateTime, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .schemas import ArticleRecord


class Base(DeclarativeBase):
    pass


class Article(Base):
    """SQLAlchemy ORM model for stored articles."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    link: Mapped[str] = mapped_column(String(512), unique=True)
    summary: Mapped[str | None] = mapped_column(String(2048))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sentiment_label: Mapped[str] = mapped_column(String(32))
    sentiment_score: Mapped[float] = mapped_column(Float)


def init_db(database_url: str) -> Session:
    """Create engine, ensure tables exist, and return a session."""

    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def upsert_articles(session: Session, records: Iterable[ArticleRecord]) -> None:
    """Insert new articles, skipping existing links."""

    for record in records:
        existing = session.query(Article).filter(Article.link == str(record.link)).first()
        if existing:
            continue
        session.add(
            Article(
                source=record.source,
                title=record.title,
                link=str(record.link),
                summary=record.summary,
                published_at=record.published_at,
                sentiment_label=record.sentiment_label,
                sentiment_score=record.sentiment_score,
            )
        )
    session.commit()
