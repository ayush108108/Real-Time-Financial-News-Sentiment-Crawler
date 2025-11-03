"""Tests for RSS fetching utilities."""

from __future__ import annotations

from typing import Iterable

import aiohttp
import pytest

from news_crawler import fetcher
from news_crawler.schemas import RawArticle
from news_crawler.settings import Settings


def test_parse_rss_extracts_articles():
    xml = """
    <rss>
        <channel>
            <item>
                <title>Title A</title>
                <link>https://example.com/a</link>
                <description>Summary A</description>
            </item>
            <item>
                <title>Title B</title>
                <link href="https://example.com/b" />
                <summary>Summary B</summary>
            </item>
        </channel>
    </rss>
    """
    articles = fetcher._parse_rss(xml, "Test")
    assert len(articles) == 2
    assert articles[0].title == "Title A"
    assert str(articles[1].link) == "https://example.com/b"


@pytest.mark.asyncio
async def test_fetch_feeds_handles_errors(monkeypatch):
    settings = Settings(
        reuters_feed_url="https://example.com/a",
        cnbc_feed_url="https://example.com/b",
    )

    class FakeResponse:
        def __init__(self, text: str, status: int = 200):
            self._text = text
            self.status = status

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def text(self):  # pragma: no cover - simple passthrough
            return self._text

        def raise_for_status(self):
            if self.status >= 400:
                raise aiohttp.ClientResponseError(None, (), status=self.status)

    class FakeSession:
        def __init__(self, responses: Iterable[FakeResponse]):
            self.responses = list(responses)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):  # pragma: no cover - deterministic responses
            return self.responses.pop(0)

    responses = [
        FakeResponse("<rss><channel></channel></rss>"),
        FakeResponse("error", status=500),
    ]

    monkeypatch.setattr(aiohttp, "ClientSession", lambda *args, **kwargs: FakeSession(responses))

    articles = await fetcher.fetch_feeds(settings)

    assert len(articles) == 0
