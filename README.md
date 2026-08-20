# AMP-GEN Material Passport Generator

An automated system for rendering, extracting, normalizing, and estimating embodied carbon from scanned Bill of Quantities (BoQ) civil engineering documents.

---

## 📋 Submission Summary

- **Name**: Mohammad Mujtaba Yasin
- **Phone**: +91 7249554613
- **Hours Spent**: ~5 hours
- **Items Extracted**: 64 of 64 (100% complete coverage including all sub-items)
- **Bonuses Attempted**:
  - **B1**: Interactive Streamlit Web Application (`app/streamlit_app.py`)
  - **B2**: Embodied Carbon Estimation ($A1$-$A3$ $kg CO_2e$, GWP/kg, Density, and traceable citations in `Comment`)
  - **B3**: Building Metadata Extraction (`output/building_meta.json`)

---

## 🚀 Quickstart (< 5 Minutes)

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/mohammad-mujtaba-yasin/amp-gen-material-passport.git
cd amp-gen-material-passport
pip install -r requirements.txt
```

### 2. Run Complete Pipeline (Offline Fast Path)
Run the automated end-to-end pipeline. This reads the committed dataset `data/boq_items.json` and generates all deliverables in `< 5 seconds`:
```bash
python -m src.pipeline
```

### 3. Launch Interactive Streamlit Web UI (Bonus B1)
Launch the interactive web application to explore items, view metrics, and download deliverables:
```bash
streamlit run app/streamlit_app.py
```

### 4. (Optional) Re-run Vision Extraction
To re-render PDF pages and call Claude Vision API directly:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
python -m src.pipeline --extract
```

---

## 📂 Project Directory Structure

```
├── app/
│   └── streamlit_app.py        # Streamlit interactive dashboard UI (Bonus B1)
├── data/
│   ├── BoQ_CBRI_Principals_Residence.pdf # Original 13-page scan PDF
│   ├── AMP_Passport_Template.xlsx        # Provided master Excel template
│   ├── boq_items.json                    # 64 extracted BoQ line items + sub-items
│   └── reference/
│       └── carbon_factors.csv            # ICE v3 / Indian LCA carbon factors (Bonus B2)
├── output/                     # Generated graded deliverables
│   ├── passport_filled.xlsx    # Filled Excel passport (74 rows, GREEN + AMBER cols)
│   ├── passport.json           # JSON export of filled passport
│   ├── building_meta.json      # Extracted Page-1 building metadata (Bonus B3)
│   ├── material_distribution.png # Brand-styled material distribution chart
│   └── visualization.png       # Alternative visualization render
├── src/                        # Modular processing engine
│   ├── config.py               # Column map, paths, unit aliases, constants
│   ├── render.py               # PyMuPDF 300 DPI page renderer
│   ├── extract.py              # Vision API extractor & JSON loader
│   ├── parse.py                # Description text miner (materials, grades, dims)
│   ├── normalize.py            # Unit canonicalizer & quantity router
│   ├── classify.py             # DSR 1989 taxonomy & category classifier
│   ├── carbon.py               # Embodied carbon & density calculator (Bonus B2)
│   ├── passport.py             # Passport record assembler
│   ├── fill_excel.py           # OpenPyXL template generator
│   ├── export_json.py          # JSON exporter
│   ├── visualize.py            # Matplotlib / Pillow chart generator
│   └── pipeline.py             # End-to-end orchestrator & CLI
├── tests/                      # Automated test suite (12 passing tests)
│   ├── test_extract.py
│   ├── test_normalize.py
│   ├── test_parse.py
│   └── test_classify_carbon.py
├── APPROACH.md                 # 1-page architecture & scaling roadmap
├── README.md                   # Quickstart instructions & submission summary
└── requirements.txt            # Project dependencies
```

---

## 🛠️ Verification & Testing

Run the automated test suite:
```bash
python -m unittest discover tests
```
All 12 unit tests verify data extraction integrity, sub-item mapping (`16`, `17`, `31`, `32`, `34`, `51`), unit canonicalization, taxonomy classification, and embodied carbon calculations.
