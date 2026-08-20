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

import re


def extract_mix_ratio(text: str) -> str | None:
    """Return a mix ratio like '1:5:10', '1:2:4', '1:6', etc. if present in *text*."""
    if not text:
        return None
    # 3-part ratios (e.g. 1:5:10, 1:2:4, 1:4:8, 1:3:6, 3:1:7)
    m3 = re.search(r"\b(\d+:\d+:\d+)\b", text)
    if m3:
        return m3.group(1)
    # 2-part ratios in mortar context (e.g. 1:6, 1:3, 1:4, 1:2, 3:1)
    m2 = re.search(r"\b(1:[1-9]\b|3:1|4:7)\b", text)
    if m2:
        return m2.group(1)
    return None


def extract_grade(text: str) -> str | None:
    """Return a grade token like 'M-15', 'Fe-500D', '75' (brick class), etc."""
    if not text:
        return None
    # Concrete grade like M-15, M20, M25
    m_grade = re.search(r"\b(M-?\d+)\b", text, re.IGNORECASE)
    if m_grade:
        return m_grade.group(1).upper()

    # Steel grade like Fe-500D, Fe-415, Mild steel
    fe_grade = re.search(r"\b(Fe-?\d+[A-Z]?)\b", text, re.IGNORECASE)
    if fe_grade:
        return fe_grade.group(1)

    # Brick class designation (e.g. class designation 75, 100)
    brick_class = re.search(r"class\s+designation\s+(\d+)", text, re.IGNORECASE)
    if brick_class:
        return f"Class {brick_class.group(1)}"

    # Bitumen grade (e.g. penetration 80/100)
    bitumen = re.search(r"penetration\s+(80/100)", text, re.IGNORECASE)
    if bitumen:
        return f"Penetration {bitumen.group(1)}"

    return None


def extract_dimensions(text: str) -> dict[str, float | None]:
    """Return {length_mm, width_mm, height_mm, thickness_mm, depth_mm, diameter_mm} in mm."""
    dims: dict[str, float | None] = {
        "length_mm": None,
        "width_mm": None,
        "height_mm": None,
        "thickness_mm": None,
        "depth_mm": None,
        "diameter_mm": None,
    }
    if not text:
        return dims

    # Thickness (e.g., 40 mm thick, 15 cm deep, 25 mm thick, 12 mm layer)
    m_thick_mm = re.search(r"(\d+(?:\.\d+)?)\s*mm\s*thick", text, re.IGNORECASE)
    if m_thick_mm:
        dims["thickness_mm"] = float(m_thick_mm.group(1))
    else:
        m_thick_cm = re.search(r"(\d+(?:\.\d+)?)\s*cm\s*thick", text, re.IGNORECASE)
        if m_thick_cm:
            dims["thickness_mm"] = float(m_thick_cm.group(1)) * 10.0

    # Diameter (e.g., 100 mm diameter, 16 mm dia, 100 mm dia)
    m_dia = re.search(r"(\d+(?:\.\d+)?)\s*mm\s*(?:diameter|dia)", text, re.IGNORECASE)
    if m_dia:
        dims["diameter_mm"] = float(m_dia.group(1))

    # Length/Width/Height from patterns like 300 x 16 mm, 50x50x50 mm, 250x250x25 mm, 15x15 cm, 45 x 45 cm
    m_3d = re.search(r"(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*(mm|cm)", text, re.IGNORECASE)
    if m_3d:
        mult = 10.0 if m_3d.group(4).lower() == "cm" else 1.0
        dims["length_mm"] = float(m_3d.group(1)) * mult
        dims["width_mm"] = float(m_3d.group(2)) * mult
        dims["height_mm"] = float(m_3d.group(3)) * mult
    else:
        m_2d = re.search(r"(\d+)\s*x\s*(\d+)\s*(mm|cm)", text, re.IGNORECASE)
        if m_2d:
            mult = 10.0 if m_2d.group(3).lower() == "cm" else 1.0
            dims["length_mm"] = float(m_2d.group(1)) * mult
            dims["width_mm"] = float(m_2d.group(2)) * mult

    # Depth (e.g. 15 cm deep, 1.5 m depth)
    m_depth_cm = re.search(r"(\d+(?:\.\d+)?)\s*cm\s*deep", text, re.IGNORECASE)
    if m_depth_cm:
        dims["depth_mm"] = float(m_depth_cm.group(1)) * 10.0

    return dims


def infer_discipline(text: str) -> str:
    """Map description -> Discipline (Civil & Sitework / Structural / Architectural / Finishes / Services / Plumbing)."""
    if not text:
        return "Civil & Sitework"
    txt = text.lower()
    if any(k in txt for k in ["earth work", "excavation", "filling", "plinth with fine sand", "surface dressing", "anti termite", "plinth protection", "khurras"]):
        return "Civil & Sitework"
    if any(k in txt for k in ["pipe", "rain water", "holderbat", "plain head", "plain shoe", "plain bend"]):
        return "Services / Plumbing"
    if any(k in txt for k in ["plaster", "painting", "white washing", "colour washing", "skirting", "flooring", "terrazzo", "polishing"]):
        return "Finishes"
    if any(k in txt for k in ["door", "window", "shutter", "ventilator", "flush door", "wood work", "aluminium", "butt hinges", "tower bolts", "handles", "stopper", "fastners", "casement"]):
        return "Architectural"
    if any(k in txt for k in ["concrete", "rcc", "reinforced", "lintels", "beams", "columns", "footings", "damp-proof", "brick work", "brick masonry", "reinforcement"]):
        return "Structural"
    return "Civil & Sitework"


def extract_material_product(text: str) -> str:
    """Extract succinct Material / Product summary from description text."""
    if not text:
        return "General Material"
    txt = text.lower()
    if "earth work" in txt or "excavation" in txt:
        return "Earthwork (excavation)"
    if "filling available excavated earth" in txt or "filling" in txt and "earth" in txt:
        return "Earthwork (filling)"
    if "filling the plinth with fine sand" in txt or "sand" in txt and "filling" in txt:
        return "Sand filling"
    if "surface dressing" in txt:
        return "Surface dressing"
    if "anti termite" in txt:
        return "Anti-termite chemical emulsion"
    if "damp-proof course" in txt:
        return "Damp-proof course (DPC)"
    if "reinforced cement concrete" in txt or "rcc" in txt:
        if "suspended floors" in txt or "roofs" in txt:
            return "RCC (suspended slab & beam)"
        if "columns" in txt:
            return "RCC (columns & posts)"
        if "lintels" in txt:
            return "RCC (lintels & beams)"
        if "shelves" in txt:
            return "RCC (shelves)"
        if "chajjas" in txt:
            return "RCC (chajjas & facias)"
        return "Reinforced cement concrete (RCC)"
    if "cement concrete" in txt:
        mix = extract_mix_ratio(text)
        return f"Cement concrete {mix}" if mix else "Cement concrete"
    if "reinforcement for rcc work" in txt or "twisted bars" in txt or "steel bars" in txt:
        return "Steel reinforcement (TMT/Mild steel)"
    if "centring and shuttering" in txt:
        return "Formwork / Shuttering"
    if "brick work" in txt or "brick masonry" in txt or "half brick" in txt:
        mix = extract_mix_ratio(text)
        return f"Brickwork in CM {mix}" if mix else "Brickwork"
    if "wood work" in txt or "door shutters" in txt or "flush door" in txt:
        return "Timber / Wood shutter"
    if "aluminium" in txt:
        return "Aluminium hardware / fittings"
    if "steel glazed doors" in txt or "t - iron frames" in txt or "guard flats" in txt or "ms fan clamp" in txt:
        return "Steel section / Hardware"
    if "flooring" in txt or "skirting" in txt:
        return "Flooring / Skirting"
    if "plaster" in txt or "plastering" in txt:
        return "Cement plaster"
    if "painting" in txt or "washing" in txt or "polishing" in txt:
        return "Paint / Wash finish"
    if "rain water pipe" in txt or "holderbat" in txt or "ci accessories" in txt:
        return "CI rainwater pipe & fittings"
    if "lime concrete terracing" in txt or "burnt clay tiles" in txt:
        return "Roofing terracing / Tiles"
    return text[:40] + "..." if len(text) > 40 else text


def parse_item(item: dict) -> dict:
    """Enrich *item* in place with parsed material/grade/mix/dimension fields."""
    desc = item.get("description", "")
    item["material_product"] = extract_material_product(desc)
    item["grade"] = extract_grade(desc)
    item["mix_ratio"] = extract_mix_ratio(desc)
    item["dimensions"] = extract_dimensions(desc)
    item["discipline"] = infer_discipline(desc)
    return item
