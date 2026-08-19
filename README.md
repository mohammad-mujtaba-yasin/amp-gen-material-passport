# AMP-GEN — Material Passport from a Scanned BoQ

Pipeline that turns a **scanned dot-matrix Bill of Quantities**
(`BoQ_CBRI_Principals_Residence.pdf`, 13 pages, 64 items) into a filled
**Material Passport** (`AMP_Passport_Template.xlsx`), a JSON export, a building
metadata file, an embodied-carbon estimate, and a distribution chart.

> **The hard part:** the PDF has **no text layer** — every page is a scanned
> image — and the **quantities are handwritten**. Classical OCR (tesseract)
> cannot read handwriting reliably, so extraction uses a **vision model**
> (Claude). Its output is committed to `data/boq_items.json` so the rest of the
> pipeline runs **fully offline in under five minutes**, no API key required.

## Quickstart (offline, ≤5 min)

```bash
python -m pip install -r requirements.txt
python -m src.pipeline
```

Outputs land in `output/`:

| File | Deliverable |
|---|---|
| `output/passport_filled.xlsx` | #1 — filled template (GREEN + AMBER columns) |
| `output/passport.json` | #2 — one JSON record per BoQ row |
| `output/building_meta.json` | bonus B3 — Page-1 building metadata |
| `output/material_distribution.png` | #5 — material-distribution chart |

Re-run the vision extraction from the scan (needs `ANTHROPIC_API_KEY`):

```bash
python -m src.pipeline --extract
```

Optional viewer:

```bash
streamlit run app/streamlit_app.py
```

## Project layout

```
iit/
├── requirements.txt         # all dependencies
├── README.md                # this file (deliverable #6)
├── APPROACH.md              # tools/decisions write-up (deliverable #4)
├── data/
│   ├── BoQ_CBRI_Principals_Residence.pdf   # source scan (committed copy)
│   ├── AMP_Passport_Template.xlsx          # target schema (committed copy)
│   ├── boq_items.json                       # authoritative vision extraction
│   └── reference/carbon_factors.csv         # ICE/GreenPro GWP factors + sources
├── src/
│   ├── config.py     # paths, column map, colours, unit rules (single source of truth)
│   ├── render.py     # PDF scan -> page images (PyMuPDF)
│   ├── extract.py    # page image -> BoQ items (Claude Vision)
│   ├── parse.py      # description -> material / grade / mix ratio / dimensions
│   ├── normalize.py  # units -> canonical + route to Volume/Area/Length/Weight/Count
│   ├── classify.py   # material category + DSR classification
│   ├── carbon.py     # bonus B2: density / GWP / embodied carbon A1-A3
│   ├── passport.py   # assemble enriched items into passport records
│   ├── fill_excel.py # write records into the template
│   ├── export_json.py# write passport.json
│   ├── visualize.py  # material-distribution chart
│   └── pipeline.py   # orchestrator + CLI
├── app/streamlit_app.py     # optional UI
├── tests/                   # unit tests (pytest)
└── output/                  # generated deliverables
```

## How extraction works

1. **Render** — PyMuPDF rasterises each scan page at 300 DPI.
2. **Vision extract** — each page image is sent to Claude, which returns
   structured line items (`item_no`, `description`, `quantity`, `unit`,
   `dsr_code`). Handwritten quantities and dot-matrix text are read together.
3. **Enrich** — `parse → normalize → classify → carbon` derive every GREEN
   (and AMBER) column from the raw item.
4. **Emit** — filled xlsx + JSON + building metadata + chart.

## Notes

- Column colours in the template drive the code: **GREEN = required**,
  **AMBER = bonus (carbon)**, **GREY = skipped** (circularity/detachability).
- The three provided EXAMPLE rows are preserved; our 64 items are written below
  them.

<!-- FILL BEFORE SUBMISSION -->
- **Hours spent:** _TBD_
- **Tools/LLMs used:** Claude (vision extraction), PyMuPDF, openpyxl, pandas,
  matplotlib/seaborn, Streamlit.
