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
from typing import Any

import openpyxl
from openpyxl.utils import column_index_from_string

from . import config


def write_passport(
    records: list[dict[str, Any]],
    template: Path = config.TEMPLATE_XLSX,
    out_path: Path = config.FILLED_XLSX,
) -> Path:
    """Fill the template with *records* and save to *out_path*; return it."""
    template = Path(template)
    out_path = Path(out_path)

    if not template.exists():
        raise FileNotFoundError(f"Template file not found at {template}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.load_workbook(template)
    ws = wb["Material Passport"]

    start_row = config.DATA_START_ROW  # Row 7

    for i, rec in enumerate(records):
        row_idx = start_row + i

        for header, col_letter in config.COLUMN_MAP.items():
            if not col_letter:
                continue
            col_idx = column_index_from_string(col_letter)
            val = rec.get(header)
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.value = val

    wb.save(out_path)
    return out_path
