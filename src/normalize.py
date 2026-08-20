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

from . import config

def normalize_unit(raw_unit: str) -> tuple[str | None, float]:
    """Return (canonical_unit, multiplier) for a raw scan unit string."""
    if not raw_unit:
        return None, 1.0
    clean = raw_unit.strip().lower()
    if clean in config.SPECIAL_UNITS:
        return config.SPECIAL_UNITS[clean]
    if clean in config.UNIT_ALIASES:
        return config.UNIT_ALIASES[clean], 1.0
    return None, 1.0


def normalize_item(item: dict) -> dict:
    """Populate original_unit + the correct quantity column + derived qty."""
    raise NotImplementedError  # TODO: implement in the normalize step
