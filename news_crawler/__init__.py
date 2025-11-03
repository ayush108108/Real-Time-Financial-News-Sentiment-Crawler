"""Real-Time Financial News Sentiment Crawler package."""

from importlib import metadata


def get_version() -> str:
    """Return the installed package version or ``0.1.0-dev`` when unavailable."""
    try:
        return metadata.version("news_crawler")
    except metadata.PackageNotFoundError:
        return "0.1.0-dev"


__all__ = ["get_version"]
