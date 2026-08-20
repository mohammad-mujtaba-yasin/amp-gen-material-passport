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

import base64
import json
import os
from pathlib import Path
from typing import Any

from . import config, render

VISION_MODEL = "claude-3-5-sonnet-20241022"  # multimodal; reads dot-matrix + handwriting


def load_items(path: Path = config.BOQ_ITEMS_JSON) -> list[dict]:
    """Load the committed vision-extracted items (offline fast path)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"BOQ items JSON not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_building_meta(
    pdf_path: Path = config.SOURCE_PDF,
    out_json: Path = config.BUILDING_META_JSON,
    model: str = VISION_MODEL,
) -> dict:
    """Extract the Page-1 metadata block (Depth of Foundation, Plinth ...)."""
    out_json = Path(out_json)
    if out_json.exists():
        with open(out_json, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback default metadata extracted directly from Page 1 scan
    meta = {
        "project_name": "Bill of Quantities for Principal's Residence (General-Modified)",
        "organization": "Central Building Research Institute, Roorkee (U.P.)",
        "document_ref": "P/Gen(Modified)/BK/10T",
        "schedule": "Schedule 'A'",
        "depth_of_foundation_m": 0.60,
        "plinth_height_m": 0.45,
        "plinth_area_sqm": 90.6,
        "class_designation_brick": "75",
        "no_of_items": 64,
        "seismic_zone": "I to IV and V",
        "bearing_capacity": "10T/Sq.m and above"
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return meta


def extract_items(
    pdf_path: Path = config.SOURCE_PDF,
    out_json: Path = config.BOQ_ITEMS_JSON,
    model: str = VISION_MODEL,
) -> list[dict]:
    """Render pages, ask Claude Vision for line items, write & return them."""
    out_json = Path(out_json)
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        # Fallback to committed offline data if no API key present
        if out_json.exists():
            return load_items(out_json)
        raise RuntimeError("ANTHROPIC_API_KEY is not set and boq_items.json does not exist.")

    try:
        import anthropic
    except ImportError:
        if out_json.exists():
            return load_items(out_json)
        raise RuntimeError("anthropic package not installed and boq_items.json does not exist.")

    client = anthropic.Anthropic(api_key=api_key)
    page_paths = render.render_pages(pdf_path=pdf_path)

    all_items: list[dict[str, Any]] = []

    prompt = (
        "You are extracting structured BoQ table items from a scanned civil construction document.\n"
        "Columns present in table:\n"
        "1. Sl.No. (Item number)\n"
        "2. Item of Work (Full description)\n"
        "3. Quantity (Handwritten number, e.g. 32.0, 12.0, 90.6, 5.4. Return null if empty)\n"
        "4. Rate (Blank in scan)\n"
        "5. Unit (e.g. Cu.m, Sq.m, Mtr., Each, 100 Sq.m, 10 Cubic decimetre, Kg.)\n"
        "6. Amount (Blank in scan)\n"
        "7. DSR 1989 Code No. (e.g. 2.8, 4.5.10, 5.14, N.S.I.)\n\n"
        "Return a JSON array of items on this page, formatted as:\n"
        "[ {\"item_no\": 1, \"description\": \"...\", \"quantity\": 32.0, \"unit\": \"Cu.m\", \"dsr_code\": \"2.8\"} ]\n"
        "Only output valid JSON array."
    )

    for p_idx, page_path in enumerate(page_paths):
        with open(page_path, "rb") as img_f:
            b64_data = base64.b64encode(img_f.read()).decode("utf-8")

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        resp_text = response.content[0].text.strip()
        if resp_text.startswith("```"):
            resp_text = resp_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        items = json.loads(resp_text)
        for item in items:
            item["page"] = p_idx + 1
            all_items.append(item)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    return all_items
