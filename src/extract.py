"""extract.py — vision extraction of BoQ line items from the scan.

Why vision: the quantities are HANDWRITTEN and the printed text is dot-matrix
on a degraded scan, so classical OCR (tesseract) is unreliable. We send each
rendered page image to Claude Vision and ask for structured line items.

The extractor is the rerunnable method of record, but its output is committed
to data/boq_items.json so the downstream pipeline runs fully offline and in
under five minutes without an API key.

Raw item shape (one dict per BoQ line)::

    {
      "item_no": 6,                      # scan column 1 (Sl.No.)
      "description": "Providing and laying cement concrete ...",
      "quantity": 8.0,                   # handwritten column 3 (None if blank)
      "unit": "Cu.m",                    # scan column 5, verbatim
      "dsr_code": "4.5.10",              # scan column 7 (DSR 1989 code)
      "page": 2
    }

Public API
----------
extract_items(...) -> list[dict]     # all 64 line items
extract_building_meta(...) -> dict   # Page-1 metadata (bonus B3)
load_items(path) -> list[dict]       # read the committed data/boq_items.json
"""
from __future__ import annotations

from pathlib import Path

from . import config

VISION_MODEL = "claude-opus-4-8"  # multimodal; reads dot-matrix + handwriting


def extract_items(
    pdf_path: Path = config.SOURCE_PDF,
    out_json: Path = config.BOQ_ITEMS_JSON,
    model: str = VISION_MODEL,
) -> list[dict]:
    """Render pages, ask Claude Vision for line items, write & return them."""
    raise NotImplementedError  # TODO: implement in the extract step


def extract_building_meta(
    pdf_path: Path = config.SOURCE_PDF,
    out_json: Path = config.BUILDING_META_JSON,
    model: str = VISION_MODEL,
) -> dict:
    """Extract the Page-1 metadata block (Depth of Foundation, Plinth ...)."""
    raise NotImplementedError  # TODO: implement in the extract step


def load_items(path: Path = config.BOQ_ITEMS_JSON) -> list[dict]:
    """Load the committed vision-extracted items (offline fast path)."""
    raise NotImplementedError  # TODO: implement in the extract step
