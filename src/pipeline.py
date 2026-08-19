"""pipeline.py — end-to-end orchestrator + CLI.

Default (offline) run:
    python -m src.pipeline
        loads data/boq_items.json -> enrich -> passport_filled.xlsx,
        passport.json, building_meta.json, material_distribution.png

Re-run the vision extraction (needs ANTHROPIC_API_KEY):
    python -m src.pipeline --extract

    python -m src.pipeline --chart-by Discipline --no-carbon
"""
from __future__ import annotations

import argparse

from . import (
    carbon,
    export_json,
    extract,
    fill_excel,
    passport,
    visualize,
)


def run(
    do_extract: bool = False,
    with_carbon: bool = True,
    chart_by: str = "Material Category",
) -> dict:
    """Run the whole pipeline and return a summary of what was written.

    Steps: (0) obtain raw items — re-extract with vision or load the committed
    JSON; (1) build enriched passport records; (2) write the filled xlsx;
    (3) write passport.json; (4) write building_meta.json (bonus B3);
    (5) render the material-distribution chart.
    """
    items = extract.extract_items() if do_extract else extract.load_items()
    records = passport.build_records(items, with_carbon=with_carbon)

    filled = fill_excel.write_passport(records)
    js = export_json.write_json(records)
    meta = extract.extract_building_meta() if do_extract else None
    chart = visualize.make_chart(records, by=chart_by)

    return {
        "items": len(items),
        "filled_xlsx": str(filled),
        "passport_json": str(js),
        "building_meta": str(meta) if meta else None,
        "chart": str(chart),
    }


def _cli() -> None:
    p = argparse.ArgumentParser(description="AMP-GEN material passport pipeline")
    p.add_argument("--extract", action="store_true",
                   help="re-run Claude Vision extraction (needs ANTHROPIC_API_KEY)")
    p.add_argument("--no-carbon", dest="carbon", action="store_false",
                   help="skip the AMBER embodied-carbon bonus (B2)")
    p.add_argument("--chart-by", default="Material Category",
                   choices=["Material Category", "Discipline", "Floor / Section"])
    args = p.parse_args()
    summary = run(do_extract=args.extract, with_carbon=args.carbon,
                  chart_by=args.chart_by)
    for k, v in summary.items():
        print(f"{k:>16}: {v}")


if __name__ == "__main__":
    _cli()
