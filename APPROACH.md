# APPROACH

_Max one page. Filled in as the build progresses._

## The problem in one line
Scanned dot-matrix BoQ (no text layer, **handwritten quantities**) → filled
Material Passport + JSON + carbon + chart.

## Tools I picked and why
- **PyMuPDF** to rasterise — no poppler/ImageMagick binary needed on Windows.
- **Claude Vision** for extraction — the quantities are handwritten and the
  print is degraded dot-matrix, which defeats tesseract. A multimodal model
  reads both in one pass. _(On-theme for an AI/ML AMP-GEN task.)_
- **openpyxl** to fill the template by column letter, preserving formatting.
- **pandas + matplotlib/seaborn** for aggregation and the chart.
- Extraction output **committed to `data/boq_items.json`** so grading runs
  offline in <5 min without an API key.

## What worked
- _TBD_

## What didn't / limitations
- _TBD (e.g. smudged right-edge DSR codes on some pages, ambiguous units)_

## With two more weeks
- _TBD (e.g. confidence-scored human-in-the-loop review UI, a proper DSR-code →
  material master, ICE-backed carbon for every line, multi-doc batch mode)._
