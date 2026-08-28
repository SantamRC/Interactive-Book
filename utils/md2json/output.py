"""Writing view documents to disk."""

from __future__ import annotations

import json
from pathlib import Path

from .config import OUTPUT_PATH


def dumps(document: dict) -> str:
    return json.dumps(document, indent=4, ensure_ascii=False) + "\n"


def write_document(path: Path, document: dict) -> None:
    """Write one document, overwriting whatever was there."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(document), encoding="utf-8")
    print(f"[write] {path.relative_to(OUTPUT_PATH)}")
