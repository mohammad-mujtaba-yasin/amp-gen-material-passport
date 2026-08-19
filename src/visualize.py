"""visualize.py — material-distribution chart (deliverable #5).

Produces one PNG summarising how material is distributed across the building.
Default dimension is Material Category; Discipline and Floor / Section are also
supported (the brief lets us choose one). Aggregation weight defaults to
embodied carbon when available, else item count, with the choice shown in the
title/labels so the chart is self-explanatory.

Public API
----------
make_chart(records, by, out_path) -> Path
"""
from __future__ import annotations

from pathlib import Path

from . import config


def make_chart(
    records: list[dict],
    by: str = "Material Category",   # or "Discipline" / "Floor / Section"
    out_path: Path = config.CHART_PNG,
) -> Path:
    """Render the material-distribution chart to *out_path*; return it."""
    raise NotImplementedError  # TODO: implement in the visualise step
