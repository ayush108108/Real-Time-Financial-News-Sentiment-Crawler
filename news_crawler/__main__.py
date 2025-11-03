"""CLI entry point for running the news crawler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import run_pipeline
from .settings import Settings, get_settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the real-time financial news sentiment crawler")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to override the output JSON location",
    )
    parser.add_argument(
        "--database",
        type=str,
        help="Optional database URL override (e.g. sqlite:///data/news.db)",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    settings = get_settings()
    if args.output:
        settings = Settings(**{**settings.model_dump(), "output_path": args.output})
    if args.database:
        settings = Settings(**{**settings.model_dump(), "database_url": args.database})
    records = run_pipeline(settings)
    print(json.dumps([record.model_dump(mode="json") for record in records], indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
