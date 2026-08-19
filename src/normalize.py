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
    """Return (canonical_unit, multiplier) for a raw scan unit string.

    multiplier applies special-unit scaling (e.g. 0.01 for cubic decimetre);
    it is 1.0 for ordinary units. canonical_unit is None if unrecognised.
    """
    raise NotImplementedError  # TODO: implement in the normalize step


def normalize_item(item: dict) -> dict:
    """Populate original_unit + the correct quantity column + derived qty."""
    raise NotImplementedError  # TODO: implement in the normalize step
