"""classify.py — taxonomy, material category, and DSR classification.

Turns parsed attributes into the CLASSIFICATION columns:
  * Material Category (Concrete / Reinf / Masonry / Steel / Wood / Finishes / ...)
  * All Materials Detected + a Material Confidence score
  * Schedule (DSR/SOR)  -> "DSR 1989"  (from the scan header)
  * Schedule Item Code  -> the DSR code carried on each line
  * Standard / Code Reference -> "CPWD DSR 1989"
  * Classification (Matched) -> a "A > B > C" taxonomy path like the examples

Keyword maps may be backed by data/reference/ files as they grow.

Public API
----------
classify_item(item) -> dict
"""
from __future__ import annotations

from . import config


def classify_item(item: dict) -> dict:
    """Enrich *item* with material category, confidence, and DSR classification."""
    raise NotImplementedError  # TODO: implement in the classify step


def material_category(text: str, material_product: str | None) -> tuple[str, float]:
    """Return (category, confidence 0-1) for the given description/material."""
    raise NotImplementedError  # TODO


def all_materials_detected(text: str) -> list[str]:
    """Return every construction material mentioned in *text*."""
    raise NotImplementedError  # TODO
