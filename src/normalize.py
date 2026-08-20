"""normalize.py — canonicalise units and route quantities.

Applies the Instructions-sheet unit conventions (Cu.m->cum, Sq.m->sqm, Mtr.->m,
Kg.->kg, Each->nos) plus the documented special cases ("10 Cubic decimetre" =
0.01 cum; DSR "100 Sq.m" basis). The canonical quantity is then written into
exactly one of the Volume/Area/Length/Weight/Count columns via
config.UNIT_TO_QTY_COLUMN.

Public API
----------
normalize_unit(raw_unit) -> (canonical_unit, factor)
normalize_item(item) -> dict   # sets original_unit, the routed qty column,
                               # and derived_quantity / _unit / _basis
"""
from __future__ import annotations

from typing import Any
from . import config


def normalize_unit(raw_unit: str) -> tuple[str | None, float]:
    """Return (canonical_unit, multiplier) for a raw scan unit string.

    multiplier applies special-unit scaling (e.g. 0.01 for cubic decimetre);
    it is 1.0 for ordinary units. canonical_unit is None if unrecognised.
    """
    if not raw_unit:
        return None, 1.0
    clean = raw_unit.strip().lower()
    if clean in config.SPECIAL_UNITS:
        return config.SPECIAL_UNITS[clean]
    if clean in config.UNIT_ALIASES:
        return config.UNIT_ALIASES[clean], 1.0
    return None, 1.0


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    """Populate original_unit + the correct quantity column + derived qty."""
    raw_unit = item.get("unit") or ""
    raw_qty = item.get("quantity")

    canonical_unit, factor = normalize_unit(raw_unit)

    item["original_unit"] = raw_unit
    item["canonical_unit"] = canonical_unit
    item["unit_factor"] = factor

    if raw_qty is not None and canonical_unit is not None:
        item["normalized_quantity"] = round(float(raw_qty) * factor, 4)
    else:
        item["normalized_quantity"] = None

    # Determine quantity column letter (P, Q, R, S, T)
    item["qty_column"] = config.UNIT_TO_QTY_COLUMN.get(canonical_unit) if canonical_unit else None

    # Handle derived quantity fields for special units like 10 Cubic decimetre or 100 Sq.m
    clean_unit = raw_unit.strip().lower()
    if clean_unit in config.SPECIAL_UNITS:
        c_unit, f = config.SPECIAL_UNITS[clean_unit]
        item["derived_quantity"] = item["normalized_quantity"]
        item["derived_quantity_unit"] = c_unit
        item["derived_quantity_basis"] = f"Scaled from {raw_unit} (factor {f})"
    else:
        item["derived_quantity"] = None
        item["derived_quantity_unit"] = None
        item["derived_quantity_basis"] = None

    return item
