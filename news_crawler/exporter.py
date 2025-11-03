"""JSON export helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schemas import ArticleRecord


def write_json(path: Path, records: Iterable[ArticleRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [record.model_dump(mode="json") for record in records]
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
