"""fill_excel.py — write passport records into the template (deliverable #1).

Opens AMP_Passport_Template.xlsx, preserves the header and the three provided
EXAMPLE rows, and writes our records from config.DATA_START_ROW downward into
the GREEN (and, when present, AMBER) columns only — GREY columns are left
blank on purpose. Values are placed by column letter via config.COLUMN_MAP so
the layout can never drift from the schema.

Public API
----------
write_passport(records, template, out_path) -> Path
"""
from __future__ import annotations

from pathlib import Path

from . import config


def write_passport(
    records: list[dict],
    template: Path = config.TEMPLATE_XLSX,
    out_path: Path = config.FILLED_XLSX,
) -> Path:
    """Fill the template with *records* and save to *out_path*; return it."""
    raise NotImplementedError  # TODO: implement in the fill_excel step
