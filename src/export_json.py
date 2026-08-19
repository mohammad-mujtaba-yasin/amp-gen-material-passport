"""export_json.py — export passport records to JSON (deliverable #2).

Writes output/passport.json as one JSON object per BoQ row, using the template
header names as keys (so the JSON and the spreadsheet are the same data in two
shapes). Numbers stay numeric; empty GREY/optional fields are omitted or null.

Public API
----------
write_json(records, out_path) -> Path
"""
from __future__ import annotations

from pathlib import Path

from . import config


def write_json(
    records: list[dict],
    out_path: Path = config.PASSPORT_JSON,
) -> Path:
    """Serialise *records* to output/passport.json; return the path."""
    raise NotImplementedError  # TODO: implement in the export step
