"""classify.py — taxonomy, material category, and DSR classification.

Turns parsed attributes into the CLASSIFICATION columns:
  * Material Category (Concrete / Reinf / Masonry / Steel / Wood / Finishes / ...)
  * All Materials Detected + a Material Confidence score
  * Schedule (DSR/SOR)  -> "DSR 1989"  (from the scan header)
  * Schedule Item Code  -> the DSR code carried on each line
  * Standard / Code Reference -> "CPWD DSR 1989"
  * Classification (Matched) -> a "A > B > C" taxonomy path like the examples

Public API
----------
classify_item(item) -> dict
"""
from __future__ import annotations

from typing import Any
from . import config


def all_materials_detected(text: str) -> list[str]:
    """Return every construction material mentioned in *text*."""
    if not text:
        return []
    txt = text.lower()
    mats = []
    keywords = [
        ("cement", "Cement"),
        ("sand", "Sand"),
        ("aggregate", "Stone Aggregate"),
        ("brick", "Bricks"),
        ("steel", "Steel"),
        ("wood", "Wood / Timber"),
        ("teak", "Teak Wood"),
        ("bitumen", "Bitumen"),
        ("lime", "Lime"),
        ("glass", "Glass"),
        ("aluminium", "Aluminium"),
        ("paint", "Paint"),
        ("primer", "Primer"),
        ("chemical", "Chemical emulsion"),
        ("pvc", "PVC"),
        ("marble", "Marble chips"),
    ]
    for kw, label in keywords:
        if kw in txt:
            mats.append(label)
    return mats


def material_category(text: str, material_product: str | None) -> tuple[str, float]:
    """Return (category, confidence 0-1) for the given description/material."""
    if not text:
        return "General", 0.5

    txt = text.lower()

    if "earth work" in txt or "excavation" in txt or "filling" in txt or "surface dressing" in txt or "anti termite" in txt:
        return "Earthwork", 0.95

    if "reinforcement" in txt or "twisted bars" in txt or "steel bars" in txt:
        return "Reinf", 0.95

    if "concrete" in txt or "rcc" in txt or "damp-proof course" in txt or "dpc" in txt or "shuttering" in txt:
        return "Concrete", 0.90

    if "brick work" in txt or "brick masonry" in txt or "half brick" in txt or "burnt clay" in txt:
        return "Masonry", 0.95

    if "wood work" in txt or "door shutters" in txt or "flush door" in txt or "teak" in txt:
        return "Wood", 0.90

    if "aluminium" in txt or "ms guard" in txt or "t - iron" in txt or "fan clamp" in txt or "hasp and staple" in txt:
        return "Metals / Hardware", 0.90

    if "plaster" in txt or "flooring" in txt or "skirting" in txt or "painting" in txt or "washing" in txt or "polishing" in txt or "terrazzo" in txt:
        return "Finishes", 0.90

    if "pipe" in txt or "holderbat" in txt or "rain water" in txt or "accessories for rain water" in txt:
        return "Plumbing", 0.90

    if "lime concrete terracing" in txt or "khurras" in txt or "gola" in txt:
        return "Roofing & Waterproofing", 0.90

    return "General", 0.70


def generate_classification_matched(text: str, cat: str, dsr_code: str | None) -> str:
    """Generate a taxonomy hierarchy matching CPWD/AMP-GEN standard style."""
    txt = text.lower()
    if cat == "Earthwork":
        return "Earthwork (excavation/filling/anti-termite) > Earthwork"
    if cat == "Concrete":
        if "1:5:10" in txt:
            return "Nominal-mix concrete > Cement concrete (nominal mix) > 1:5:10"
        if "1:4:8" in txt:
            return "Nominal-mix concrete > Cement concrete (nominal mix) > 1:4:8"
        if "1:2:4" in txt:
            return "Nominal-mix concrete > Cement concrete (nominal mix) > 1:2:4"
        return "Nominal-mix concrete > Cement concrete"
    if cat == "Reinf":
        if "twisted" in txt or "cold twisted" in txt:
            return "Reinforcement steel (TMT/rebar) > Mild steel round bar > Twisted steel/deformed TMT bars Fe-500D"
        return "Reinforcement steel (TMT/rebar) > Mild steel round bar"
    if cat == "Masonry":
        if "half brick" in txt:
            return "Brickwork > Half brick masonry > CM 1:4"
        return "Brickwork > Burnt clay bricks > Class 75"
    if cat == "Wood":
        return "Timber / Wood work > Doors & Windows > Teak / Hardwood"
    if cat == "Finishes":
        if "plaster" in txt:
            return "Plastering & Finishes > Cement Plaster"
        if "paint" in txt or "wash" in txt:
            return "Painting & Polishing > Wash / Enamel"
        return "Finishes & Flooring > Tiles / Skirting"
    return f"{cat} > General"


def classify_item(item: dict[str, Any]) -> dict[str, Any]:
    """Enrich *item* with material category, confidence, and DSR classification."""
    desc = item.get("description", "")
    mat_prod = item.get("material_product")
    dsr_code = item.get("dsr_code")

    cat, conf = material_category(desc, mat_prod)
    detected_mats = all_materials_detected(desc)

    item["material_category"] = cat
    item["material_confidence"] = conf
    item["all_materials_detected"] = ", ".join(detected_mats) if detected_mats else "General"
    item["schedule"] = config.DEFAULT_SCHEDULE
    item["schedule_item_code"] = dsr_code if dsr_code else "N.S.I."
    item["standard_ref"] = config.DEFAULT_STANDARD_REF
    item["classification_matched"] = generate_classification_matched(desc, cat, dsr_code)

    return item
