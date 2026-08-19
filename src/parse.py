"""parse.py — mine the BoQ description text for structured attributes.

Descriptions are dense CPWD-style prose that embed the material, grade, mix
ratio, and nominal dimensions, e.g.:

    "... plain cement concrete ... M-15 grade ... 1:4:8 ..."
    "... graded stone aggregate 40 mm nominal size ..."

This module turns that prose into fields, without touching quantities/units
(that is normalize.py) or taxonomy (classify.py).

Public API
----------
parse_item(item) -> dict   # adds: material_product, grade, mix_ratio, dimensions{}, discipline
"""
from __future__ import annotations


def parse_item(item: dict) -> dict:
    """Enrich *item* in place with parsed material/grade/mix/dimension fields."""
    raise NotImplementedError  # TODO: implement in the parse step


def extract_mix_ratio(text: str) -> str | None:
    """Return a mix ratio like '1:4:8' or '1:2:4' if present in *text*."""
    raise NotImplementedError  # TODO


def extract_grade(text: str) -> str | None:
    """Return a grade token like 'M-15', 'Fe-500D', 'M20' if present."""
    raise NotImplementedError  # TODO


def extract_dimensions(text: str) -> dict:
    """Return {length_mm, width_mm, height_mm, thickness_mm, depth_mm, diameter_mm}."""
    raise NotImplementedError  # TODO


def infer_discipline(text: str) -> str:
    """Map description -> Discipline (Civil & Sitework / Structural / ...)."""
    raise NotImplementedError  # TODO
