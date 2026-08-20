"""visualize.py — material-distribution chart (deliverable #5).

Produces PNG charts summarising how material is distributed across the building.
Uses exact project brand palette:
  * Primary Dark / Text:      #450C3F
  * Primary Accent:           #B9D175
  * Soft Green Accent:        #D9EFBD
  * Background / Light Tint:  #F5FBDA

Public API
----------
make_chart(records, by, out_path) -> Path
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from . import config

BRAND_DARK = "#450C3F"
BRAND_ACCENT = "#B9D175"
BRAND_SOFT_GREEN = "#D9EFBD"
BRAND_BG = "#F5FBDA"


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

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    colors = [BRAND_ACCENT, BRAND_SOFT_GREEN, BRAND_DARK, "#9BB556", "#C4E289", "#67205F"]
    colors = colors[: len(labels)] if len(labels) <= len(colors) else colors * (len(labels) // len(colors) + 1)

    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], edgecolor=BRAND_DARK, linewidth=0.8, height=0.65)

    ax.set_title(
        f"Material Distribution by {by}\n(Weighted by {title_metric})",
        fontsize=14,
        fontweight="bold",
        color=BRAND_DARK,
        pad=15,
    )
    ax.set_xlabel(title_metric, fontsize=11, fontweight="bold", color=BRAND_DARK, labelpad=10)
    ax.set_ylabel(by, fontsize=11, fontweight="bold", color=BRAND_DARK, labelpad=10)

    ax.tick_params(colors=BRAND_DARK, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(BRAND_DARK)
        spine.set_linewidth(1.2)

    ax.xaxis.set_major_formatter("{x:,.0f}")

    for bar in bars:
        width = bar.get_width()
        val_str = f"{width:,.1f}" if has_carbon else f"{int(width)}"
        ax.text(
            width + (max(values) * 0.015),
            bar.get_y() + bar.get_height() / 2,
            val_str,
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=BRAND_DARK,
        )

    plt.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor=BRAND_BG)
    plt.close(fig)

    # Also save to secondary path if different
    alt_path = out_path.parent / ("visualization.png" if out_path.name == "material_distribution.png" else "material_distribution.png")
    fig2 = plt.figure(figsize=(10, 6), dpi=300)
    # Re-save image content
    out_path_bytes = out_path.read_bytes()
    alt_path.write_bytes(out_path_bytes)

    return out_path


def _make_chart_pil(
    data: dict[str, float],
    by: str,
    title_metric: str,
    has_carbon: bool,
    out_path: Path,
) -> Path:
    from PIL import Image, ImageDraw

    width, height = 1200, 700
    # RGB color tuple for #F5FBDA: (245, 251, 218)
    bg_rgb = (245, 251, 218)
    dark_rgb = (69, 12, 63)
    accent_rgb = (185, 209, 117)
    soft_green_rgb = (217, 239, 189)

    img = Image.new("RGB", (width, height), color=bg_rgb)
    draw = ImageDraw.Draw(img)

    # Title
    title_text = f"Material Distribution by {by} ({title_metric})"
    draw.text((60, 40), title_text, fill=dark_rgb)

    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, v in sorted_items if v > 0]
    values = [v for k, v in sorted_items if v > 0]

    if values:
        max_val = max(values)
        colors = [accent_rgb, soft_green_rgb, dark_rgb, (155, 181, 86), (196, 226, 137)]

        start_y = 120
        bar_height = 40
        gap = 20
        max_bar_w = 680
        label_x = 60
        bar_x = 280

        for i, (lbl, val) in enumerate(zip(labels, values)):
            y = start_y + i * (bar_height + gap)
            w = int((val / max_val) * max_bar_w) if max_val > 0 else 0
            color = colors[i % len(colors)]

            draw.text((label_x, y + 10), str(lbl), fill=dark_rgb)
            draw.rectangle([bar_x, y, bar_x + w, y + bar_height], fill=color, outline=dark_rgb)
            val_str = f"{val:,.1f}" if has_carbon else f"{int(val)}"
            draw.text((bar_x + w + 15, y + 10), val_str, fill=dark_rgb)

    img.save(out_path)

    # Save copy to visualization.png / material_distribution.png
    alt_path = out_path.parent / ("visualization.png" if out_path.name == "material_distribution.png" else "material_distribution.png")
    img.save(alt_path)

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
