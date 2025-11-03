"""Tests for the pipeline orchestration."""

from __future__ import annotations

from pathlib import Path

import news_crawler.pipeline as pipeline
from news_crawler.schemas import ArticleRecord, ArticleSentiment, RawArticle
from news_crawler.settings import Settings


def test_deduplicate_removes_duplicate_links():
    article_a = RawArticle(
        source="Reuters",
        title="Stocks rally",
        link="https://example.com/a",
        summary=None,
        published_at=None,
    )
    article_b = article_a.model_copy()
    deduped = pipeline._deduplicate([article_a, article_b])
    assert len(deduped) == 1
    assert deduped[0].link == article_a.link


def test_run_pipeline_happy_path(monkeypatch, tmp_path):
    settings = Settings(
        reuters_feed_url="https://example.com/reuters.xml",
        cnbc_feed_url="https://example.com/cnbc.xml",
        output_path=tmp_path / "latest.json",
        database_url=f"sqlite:///{tmp_path / 'news.db'}",
    )

    sample_articles = [
        RawArticle(
            source="Reuters",
            title="Markets open higher",
            link="https://example.com/1",
            summary="Summary",
            published_at=None,
        ),
        RawArticle(
            source="CNBC",
            title="Markets open higher",
            link="https://example.com/1",
            summary="Duplicate",
            published_at=None,
        ),
    ]

    async def fake_fetch_feeds(_settings):
        return sample_articles

    def fake_annotate_sentiment(_settings, articles):
        return [
            (
                article,
                ArticleSentiment(label="POSITIVE", score=0.9),
            )
            for article in articles
        ]

    persisted: dict[str, list[ArticleRecord]] = {}

    def fake_persist(_settings, records):
        persisted["records"] = list(records)

    exported: dict[str, Path | list[ArticleRecord]] = {}

    def fake_write_json(path, records):
        exported["path"] = path
        exported["records"] = list(records)

    monkeypatch.setattr(pipeline, "fetch_feeds", fake_fetch_feeds)
    monkeypatch.setattr(pipeline, "annotate_sentiment", fake_annotate_sentiment)
    monkeypatch.setattr(pipeline, "_persist", fake_persist)
    monkeypatch.setattr(pipeline, "write_json", fake_write_json)

    records = pipeline.run_pipeline(settings)

    assert len(records) == 1
    record = records[0]
    assert isinstance(record, ArticleRecord)
    assert record.sentiment_label == "POSITIVE"
    assert exported["path"] == settings.output_path
    assert len(exported["records"]) == 1
    assert persisted["records"][0].link == record.link
