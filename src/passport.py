"""passport.py — assemble enriched items into full passport records.

A "record" is a dict keyed by the template header names in config.COLUMN_MAP
(e.g. record["Description"], record["Volume (m3)"]). This is the single shape
consumed by fill_excel, export_json, and visualize, so the mapping to columns
lives in exactly one place.

Public API
----------
build_record(item, index) -> dict     # one enriched item -> one passport record
build_records(items) -> list[dict]    # run parse->normalize->classify->carbon for all
"""
from __future__ import annotations

from typing import Any

from . import carbon, classify, config, normalize, parse


def build_record(item: dict[str, Any], index: int) -> dict[str, Any]:
    """Map a fully-enriched item onto the template's header-keyed record."""
    gmap_id = f"AMP-{index + 1:03d}"
    item_no_str = str(item.get("sub_item_no") or item.get("item_no") or (index + 1))

    # Basic fields
    rec: dict[str, Any] = {
        "GMAP Id": gmap_id,
        "BOQ Item No.": item_no_str,
        "Article Number": None,
        "External DB Id": None,
        "Description": item.get("description"),
        "Floor / Section": f"Page {item.get('page', 1)} - Schedule A",
        "Discipline": item.get("discipline"),
        "Material / Product": item.get("material_product"),
        "All Materials Detected": item.get("all_materials_detected"),
        "Material Category": item.get("material_category"),
        "Original Quantity": item.get("quantity"),
        "Original Unit": item.get("original_unit"),
        "Volume (m³)": None,
        "Area (m²)": None,
        "Length (m)": None,
        "Weight (kg)": None,
        "Count (Nos)": None,
        "Derived Quantity": item.get("derived_quantity"),
        "Derived Quantity Unit": item.get("derived_quantity_unit"),
        "Derived Quantity Basis": item.get("derived_quantity_basis"),
        "Density (kg/m³)": item.get("density_kg_m3"),
        "Embodied Carbon A1-A3 (kg CO₂e)": item.get("embodied_carbon_a1_a3"),
        "GWP / kg (kg CO₂e/kg)": item.get("gwp_per_kg"),
        "Material Confidence": item.get("material_confidence"),
        "Schedule (DSR/SOR)": item.get("schedule"),
        "Schedule Item Code": item.get("schedule_item_code"),
        "Standard / Code Reference": item.get("standard_ref"),
        "Classification (Matched)": item.get("classification_matched"),
        "Grade / Specification": item.get("grade"),
        "Mix Ratio": item.get("mix_ratio"),
        "Comment": item.get("comment"),
    }

    # Route canonical quantity to the specific quantity column
    col_letter = item.get("qty_column")
    norm_qty = item.get("normalized_quantity")

    if col_letter == "P":
        rec["Volume (m³)" ] = norm_qty
    elif col_letter == "Q":
        rec["Area (m²)"] = norm_qty
    elif col_letter == "R":
        rec["Length (m)"] = norm_qty
    elif col_letter == "S":
        rec["Weight (kg)"] = norm_qty
    elif col_letter == "T":
        rec["Count (Nos)"] = norm_qty

    # Dimensions
    dims = item.get("dimensions") or {}
    rec["Nominal Length (mm)"] = dims.get("length_mm")
    rec["Nominal Width (mm)"] = dims.get("width_mm")
    rec["Nominal Height (mm)"] = dims.get("height_mm")
    rec["Nominal Thickness (mm)"] = dims.get("thickness_mm")
    rec["Nominal Depth (mm)"] = dims.get("depth_mm")
    rec["Nominal Diameter (mm)"] = dims.get("diameter_mm")

    return rec


def build_records(items: list[dict[str, Any]], with_carbon: bool = True) -> list[dict[str, Any]]:
    """Run the enrichment chain over raw items and return passport records."""
    carbon_factors = carbon.load_factors() if with_carbon else {}
    records: list[dict[str, Any]] = []

    flat_items: list[dict[str, Any]] = []
    for it in items:
        # Check if item has sub-items
        sub_items = it.get("sub_items")
        if sub_items and len(sub_items) > 0:
            for sub_it in sub_items:
                merged = dict(it)
                merged.update(sub_it)
                flat_items.append(merged)
        else:
            flat_items.append(it)

    for idx, raw_item in enumerate(flat_items):
        item = dict(raw_item)
        parse.parse_item(item)
        normalize.normalize_item(item)
        classify.classify_item(item)
        if with_carbon:
            carbon.enrich_carbon(item, carbon_factors)

        rec = build_record(item, idx)
        records.append(rec)

    return records
