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

from collections import defaultdict
from pathlib import Path
from typing import Any

from . import config


def _make_chart_matplotlib(
    data: dict[str, float],
    by: str,
    title_metric: str,
    has_carbon: bool,
    out_path: Path,
) -> Path:
    import matplotlib.pyplot as plt

    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, v in sorted_items if v > 0]
    values = [v for k, v in sorted_items if v > 0]

    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    colors = ["#2b5c8f", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666", "#1b9e77"]
    colors = colors[: len(labels)] if len(labels) <= len(colors) else colors * (len(labels) // len(colors) + 1)

    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], edgecolor="none", height=0.65)

    ax.set_title(f"Material Distribution by {by}\n(Weighted by {title_metric})", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel(title_metric, fontsize=11, labelpad=10)
    ax.set_ylabel(by, fontsize=11, labelpad=10)

    ax.xaxis.set_major_formatter("{x:,.0f}")

    for bar in bars:
        width = bar.get_width()
        val_str = f"{width:,.1f}" if has_carbon else f"{int(width)}"
        ax.text(width + (max(values) * 0.01), bar.get_y() + bar.get_height() / 2, val_str, ha="left", va="center", fontsize=9, fontweight="bold")

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


def _make_chart_pil(
    data: dict[str, float],
    by: str,
    title_metric: str,
    has_carbon: bool,
    out_path: Path,
) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 700
    img = Image.new("RGB", (width, height), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    # Title
    title_text = f"Material Distribution by {by} ({title_metric})"
    draw.text((60, 40), title_text, fill=(33, 37, 41))

    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, v in sorted_items if v > 0]
    values = [v for k, v in sorted_items if v > 0]

    if not values:
        img.save(out_path)
        return out_path

    max_val = max(values)
    colors = [
        (43, 92, 143),
        (217, 95, 2),
        (117, 112, 179),
        (231, 41, 138),
        (102, 166, 30),
        (230, 171, 2),
        (166, 118, 29),
        (102, 102, 102),
        (27, 158, 119),
    ]

    start_y = 120
    bar_height = 40
    gap = 20
    max_bar_w = 700
    label_x = 60
    bar_x = 280

    for i, (lbl, val) in enumerate(zip(labels, values)):
        y = start_y + i * (bar_height + gap)
        w = int((val / max_val) * max_bar_w) if max_val > 0 else 0
        color = colors[i % len(colors)]

        # Label
        draw.text((label_x, y + 10), str(lbl), fill=(50, 50, 50))
        # Bar
        draw.rectangle([bar_x, y, bar_x + w, y + bar_height], fill=color)
        # Value text
        val_str = f"{val:,.1f}" if has_carbon else f"{int(val)}"
        draw.text((bar_x + w + 15, y + 10), val_str, fill=(30, 30, 30))

    img.save(out_path)
    return out_path


def make_chart(
    records: list[dict[str, Any]],
    by: str = "Material Category",  # or "Discipline" / "Floor / Section"
    out_path: Path = config.CHART_PNG,
) -> Path:
    """Render the material-distribution chart to *out_path*; return it."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    category_carbon: dict[str, float] = defaultdict(float)
    category_counts: dict[str, int] = defaultdict(int)

    for rec in records:
        key = rec.get(by) or "Unclassified"
        category_counts[key] += 1
        carbon_val = rec.get("Embodied Carbon A1-A3 (kg CO₂e)")
        if carbon_val is not None and isinstance(carbon_val, (int, float)):
            category_carbon[key] += float(carbon_val)

    has_carbon = sum(category_carbon.values()) > 0
    if has_carbon:
        data = dict(category_carbon)
        title_metric = "Embodied Carbon (kg CO₂e)"
    else:
        data = {k: float(v) for k, v in category_counts.items()}
        title_metric = "Item Count"

    try:
        return _make_chart_matplotlib(data, by, title_metric, has_carbon, out_path)
    except ImportError:
        return _make_chart_pil(data, by, title_metric, has_carbon, out_path)
