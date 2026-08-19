"""
Central configuration & shared contract for the AMP-GEN pipeline.

Every module imports paths, the Excel column map, colour codes, and the
unit-normalisation rules from here so there is a single source of truth
that matches AMP_Passport_Template.xlsx exactly.

Nothing in this module does I/O at import time except computing paths.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------
# Paths (repo-root relative, so the pipeline is location-independent)
# --------------------------------------------------------------------------
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
DATA_DIR = ROOT_DIR / "data"
REFERENCE_DIR = DATA_DIR / "reference"
OUTPUT_DIR = ROOT_DIR / "output"
PAGE_IMAGE_DIR = DATA_DIR / "page_images"  # rendered scan pages (gitignored cache)

# Inputs (committed copies live under data/ so the repo is self-contained)
SOURCE_PDF = DATA_DIR / "BoQ_CBRI_Principals_Residence.pdf"
TEMPLATE_XLSX = DATA_DIR / "AMP_Passport_Template.xlsx"

# Intermediate + final artefacts
BOQ_ITEMS_JSON = DATA_DIR / "boq_items.json"          # authoritative vision extraction
CARBON_FACTORS_CSV = REFERENCE_DIR / "carbon_factors.csv"

FILLED_XLSX = OUTPUT_DIR / "passport_filled.xlsx"      # deliverable #1
PASSPORT_JSON = OUTPUT_DIR / "passport.json"           # deliverable #2
BUILDING_META_JSON = OUTPUT_DIR / "building_meta.json"  # bonus B3
CHART_PNG = OUTPUT_DIR / "material_distribution.png"    # deliverable #5

# --------------------------------------------------------------------------
# Excel template geometry
# --------------------------------------------------------------------------
SHEET_NAME = "Material Passport"
SECTION_ROW = 2        # merged section banners (IDENTIFICATION, MATERIAL, ...)
HEADER_ROW = 3         # column headers (the names in COLUMN_MAP below)
EXAMPLE_ROWS = (4, 5, 6)   # provided EXAMPLE rows — preserved, not overwritten
DATA_START_ROW = 7     # our 64 extracted items are written from here downward
EXPECTED_ITEM_COUNT = 64   # stated on Page 1 ("No of Items : 64")

# Fill colours used by the template to categorise columns (openpyxl ARGB)
COLOR_SECTION = "00305496"   # dark teal section banners
COLOR_GREEN = "00C6EFCE"     # REQUIRED
COLOR_AMBER = "00FFEB9C"     # BONUS (B2 carbon)
COLOR_GREY = "00D9D9D9"      # SKIP
COLOR_EXAMPLE = "00DDEBF7"   # provided example-row fill

# --------------------------------------------------------------------------
# Column map — header text -> spreadsheet column letter (verbatim from row 3)
# --------------------------------------------------------------------------
COLUMN_MAP: dict[str, str] = {
    # IDENTIFICATION
    "GMAP Id": "A",
    "BOQ Item No.": "B",
    "Article Number": "C",
    "External DB Id": "D",
    # ELEMENT & LOCATION
    "Description": "E",
    "Floor / Section": "F",
    "Discipline": "G",
    # MATERIAL
    "Material / Product": "H",
    "All Materials Detected": "I",
    "Material Category": "J",
    "Material Confidence": "K",
    "Grade": "L",
    "Mix Ratio": "M",
    # QUANTITIES
    "Original Quantity": "N",
    "Original Unit": "O",
    "Volume (m3)": "P",
    "Area (m2)": "Q",
    "Length (m)": "R",
    "Weight (kg)": "S",
    "Count (Nos)": "T",
    # DERIVED QUANTITY
    "Derived Quantity": "U",
    "Derived Quantity Unit": "V",
    "Derived Quantity Basis": "W",
    # MASS & CARBON  (AMBER / bonus B2)
    "Density (kg/m3)": "X",
    "Embodied Carbon A1-A3 (kg CO2e)": "Y",
    "GWP / kg (kg CO2e/kg)": "Z",
    # CLASSIFICATION
    "Schedule (DSR/SOR)": "AA",
    "Schedule Item Code": "AB",
    "Standard / Code Reference": "AC",
    "Classification (Matched)": "AD",
    # CIRCULARITY & EOL  (GREY / skip)
    "% Reused": "AE",
    "% Available for Reuse": "AF",
    "Assumed Construction Waste": "AG",
    "Waste Codes": "AH",
    "Detachability - Connection": "AI",
    "Detachability - Connection Detail": "AJ",
    "Detachability - Accessibility": "AK",
    "Detachability - Intersection": "AL",
    "Detachability - Product Edge": "AM",
    # LIFECYCLE & ASSET  (GREY / skip)
    "Lifespan (Years)": "AN",
    # DIMENSIONS (from Description)
    "Length (mm)": "AO",
    "Width (mm)": "AP",
    "Height (mm)": "AQ",
    "Thickness (mm)": "AR",
    "Depth (mm)": "AS",
    "Diameter (mm)": "AT",
    # COMMERCIAL
    "Unit Rate": "AU",
    "Total Cost": "AV",
    "Currency": "AW",
    "Comment": "AX",
}

# Column groups by colour (spreadsheet letters)
GREEN_REQUIRED = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W",
    "AA", "AB", "AC", "AD",
    "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV", "AW", "AX",
]
AMBER_BONUS = ["X", "Y", "Z"]
GREY_SKIP = ["AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN"]

# --------------------------------------------------------------------------
# Unit normalisation (per the Instructions sheet)
# --------------------------------------------------------------------------
# Canonical units used across the pipeline
CUM, SQM, M, KG, NOS = "cum", "sqm", "m", "kg", "nos"

# Raw scan spelling (lower-cased, stripped) -> canonical unit
UNIT_ALIASES: dict[str, str] = {
    "cu.m": CUM, "cum": CUM, "m3": CUM, "m³": CUM, "cubic metre": CUM,
    "cubic meter": CUM, "cu m": CUM, "cu. m": CUM,
    "sq.m": SQM, "sqm": SQM, "m2": SQM, "m²": SQM, "square metre": SQM,
    "square meter": SQM, "sq m": SQM, "sq. m": SQM,
    "mtr.": M, "mtr": M, "m": M, "metre": M, "meter": M, "rmt": M, "r.m.": M,
    "kg.": KG, "kg": KG, "kilogram": KG, "quintal": KG,
    "each": NOS, "nos": NOS, "no.": NOS, "no": NOS, "nos.": NOS, "number": NOS,
}

# Canonical unit -> the passport quantity column that receives the value
UNIT_TO_QTY_COLUMN: dict[str, str] = {
    CUM: "P",   # Volume (m3)
    SQM: "Q",   # Area (m2)
    M: "R",     # Length (m)
    KG: "S",    # Weight (kg)
    NOS: "T",   # Count (Nos)
}

# Compound / special units -> (canonical_unit, multiply raw quantity by factor)
# e.g. "10 Cubic decimetre" (item 24, wood work) == 0.01 cum;
#      DSR surface-dressing "100 Sq.m" means the qty is expressed per 100 sqm.
SPECIAL_UNITS: dict[str, tuple[str, float]] = {
    "10 cubic decimetre": (CUM, 0.01),
    "cubic decimetre": (CUM, 0.001),
    "100 sq.m": (SQM, 100.0),
    "100 sqm": (SQM, 100.0),
    "quintal": (KG, 100.0),
}

# --------------------------------------------------------------------------
# Defaults sourced from the scan header / Page 1
# --------------------------------------------------------------------------
DEFAULT_SCHEDULE = "DSR 1989"           # scan column 7 header: "DSR 1989 Code No."
DEFAULT_STANDARD_REF = "CPWD DSR 1989"
DEFAULT_CURRENCY = "INR"
PROJECT_NAME = "Principal's Residence (General-Modified)"
PROJECT_ORG = "Central Building Research Institute, Roorkee"
