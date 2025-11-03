"""Async RSS fetching utilities."""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable, List

import aiohttp
from bs4 import BeautifulSoup, FeatureNotFound


try:  # pragma: no cover - optional dependency for fallback parsing
    import xml.etree.ElementTree as ET
except ImportError:  # pragma: no cover
    ET = None

from .schemas import RawArticle
from .settings import Settings


logger = logging.getLogger(__name__)


async def _fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


def _parse_rss(xml: str, source: str) -> List[RawArticle]:
    items = []
    try:
        soup = BeautifulSoup(xml, "xml")
        items = soup.find_all("item") or soup.find_all("entry")
    except FeatureNotFound:
        soup = None

    if not items and ET is not None:
        try:
            root = ET.fromstring(xml)
            items = root.findall(".//item") or root.findall(".//entry")

            def _get_text(element, name: str) -> str | None:
                child = element.find(name)
                if child is None:
                    return None
                text = child.text or ""
                return text.strip() or None

            records: list[RawArticle] = []
            for item in items:
                title = _get_text(item, "title")
                link_element = item.find("link")
                link = None
                if link_element is not None:
                    link = link_element.attrib.get("href") or (link_element.text or "").strip() or None
                summary = _get_text(item, "description") or _get_text(item, "summary")
                published = (
                    _get_text(item, "pubDate")
                    or _get_text(item, "published")
                    or _get_text(item, "updated")
                )
                if not title or not link:
                    continue
                records.append(
                    RawArticle(
                        source=source,
                        title=title,
                        link=link,
                        summary=summary,
                        published_at=published,
                    )
                )
            if records:
                return records
        except ET.ParseError:
            pass

    if soup is None:
        soup = BeautifulSoup(xml, "html.parser")
        items = soup.find_all("item") or soup.find_all("entry")

    articles: list[RawArticle] = []
    for item in items:
        title_tag = item.find("title")
        link_tag = item.find("link")
        summary_tag = item.find("description") or item.find("summary")
        published_tag = (
            item.find("pubDate")
            or item.find("published")
            or item.find("updated")
        )
        link = None
        if link_tag:
            link = link_tag.get_text(strip=True) or None
            if hasattr(link_tag, "attrs"):
                link = link or link_tag.attrs.get("href")
        if link_tag and link_tag.has_attr("href"):
            link = link_tag["href"]
        if not title_tag or not link:
            continue
        articles.append(
            RawArticle(
                source=source,
                title=title_tag.get_text(strip=True),
                link=link,
                summary=summary_tag.get_text(strip=True) if summary_tag else None,
                published_at=published_tag.get_text(strip=True) if published_tag else None,
            )
        )
    return articles


async def fetch_feeds(settings: Settings) -> list[RawArticle]:
    feeds: Iterable[tuple[str, str]] = (
        ("Reuters", settings.reuters_feed_url),
        ("CNBC", settings.cnbc_feed_url),
    )
    timeout = aiohttp.ClientTimeout(total=settings.http_timeout_seconds)
    connector = aiohttp.TCPConnector(ssl=False)
    headers = {"User-Agent": settings.user_agent}

    async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers) as session:
        tasks = [
            asyncio.create_task(_fetch(session, url))
            for _, url in feeds
        ]
        xml_payloads = await asyncio.gather(*tasks, return_exceptions=True)

    articles: list[RawArticle] = []
    for (source, url), payload in zip(feeds, xml_payloads, strict=False):
        if isinstance(payload, Exception):
            logger.warning("Failed to fetch feed %s (%s): %s", source, url, payload)
            continue
        articles.extend(_parse_rss(payload, source))
    return articles
