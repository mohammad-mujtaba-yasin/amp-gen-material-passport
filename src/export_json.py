"""export_json.py — export passport records to JSON (deliverable #2).

Writes output/passport.json as one JSON object per BoQ row, using the template
header names as keys (so the JSON and the spreadsheet are the same data in two
shapes). Numbers stay numeric; empty GREY/optional fields are omitted or null.

Public API
----------
write_json(records, out_path) -> Path
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config


def write_json(
    records: list[dict[str, Any]],
    out_path: Path = config.PASSPORT_JSON,
) -> Path:
    """Serialise *records* to output/passport.json; return the path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    return out_path
