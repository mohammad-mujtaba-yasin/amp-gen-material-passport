"""streamlit_app.py — Interactive Web Dashboard (Bonus B1).

Features:
  * Exact brand palette styling (#450C3F, #B9D175, #D9EFBD, #F5FBDA)
  * Real-time KPI summary cards
  * Searchable & filterable passport records table viewer
  * Interactive material & carbon distribution charts
  * Direct file downloads for Excel, JSON, and building metadata
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

# Configure page layout and title
st.set_page_config(
    page_title="AMP-GEN Material Passport Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Root directory path
BASE_DIR = Path(__file__).resolve().parent.parent
PASSPORT_JSON = BASE_DIR / "output" / "passport.json"
PASSPORT_XLSX = BASE_DIR / "output" / "passport_filled.xlsx"
BUILDING_META_JSON = BASE_DIR / "output" / "building_meta.json"
CHART_PNG = BASE_DIR / "output" / "material_distribution.png"

# Custom CSS matching exact brand palette
st.markdown(
    """
    <style>
    /* Main App Background */
    .stApp {
        background-color: #F5FBDA;
        color: #450C3F;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Headers & Titles */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #450C3F !important;
        font-weight: 700;
    }
    
    /* KPI Metric Cards */
    div[data-testid="stMetricValue"] {
        color: #450C3F !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #450C3F !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] {
        background-color: #D9EFBD;
        border: 2px solid #B9D175;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(69, 12, 63, 0.1);
    }
    
    /* Buttons */
    .stButton>button, .stDownloadButton>button {
        background-color: #B9D175 !important;
        color: #450C3F !important;
        font-weight: 700 !important;
        border: 2px solid #450C3F !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #D9EFBD !important;
        color: #450C3F !important;
        transform: translateY(-2px);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #D9EFBD;
        border-right: 2px solid #B9D175;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    records = []
    if PASSPORT_JSON.exists():
        with open(PASSPORT_JSON, "r", encoding="utf-8") as f:
            records = json.load(f)
    meta = {}
    if BUILDING_META_JSON.exists():
        with open(BUILDING_META_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)
    return records, meta


def main():
    st.title("🏗️ AMP-GEN Material Passport Explorer")
    st.caption("CBRI Principal's Residence — General-Modified | Document Ref: P/Gen(Modified)/BK/10T")

    records, meta = load_data()
    df = pd.DataFrame(records) if records else pd.DataFrame()

    # KPI Metrics Section
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    items_count = meta.get("no_of_items", 64)
    records_count = len(df)
    plinth_area = meta.get("plinth_area_sqm", 90.6)

    total_carbon = 0.0
    if not df.empty and "Embodied Carbon A1-A3 (kg CO₂e)" in df.columns:
        total_carbon = df["Embodied Carbon A1-A3 (kg CO₂e)"].dropna().sum()

    with col1:
        st.metric(label="Items Extracted", value=f"{items_count} / 64")
    with col2:
        st.metric(label="Passport Records", value=f"{records_count}")
    with col3:
        st.metric(label="Plinth Area", value=f"{plinth_area} m²")
    with col4:
        st.metric(label="Total Embodied Carbon", value=f"{total_carbon / 1000.0:,.2f} t CO₂e")

    st.markdown("---")

    # Sidebar Controls & Downloads
    st.sidebar.header("📥 Deliverable Downloads")

    if PASSPORT_XLSX.exists():
        st.sidebar.download_button(
            label="📄 Download Excel Passport (.xlsx)",
            data=PASSPORT_XLSX.read_bytes(),
            file_name="passport_filled.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    if PASSPORT_JSON.exists():
        st.sidebar.download_button(
            label="🌐 Download Passport JSON (.json)",
            data=PASSPORT_JSON.read_bytes(),
            file_name="passport.json",
            mime="application/json",
        )

    if BUILDING_META_JSON.exists():
        st.sidebar.download_button(
            label="🏛️ Download Building Meta (.json)",
            data=BUILDING_META_JSON.read_bytes(),
            file_name="building_meta.json",
            mime="application/json",
        )

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filters")

    # Search and Filter
    if not df.empty:
        categories = ["All"] + sorted([str(x) for x in df["Material Category"].dropna().unique()])
        selected_cat = st.sidebar.selectbox("Filter by Material Category", categories)

        disciplines = ["All"] + sorted([str(x) for x in df["Discipline"].dropna().unique()])
        selected_disc = st.sidebar.selectbox("Filter by Discipline", disciplines)

        search_query = st.sidebar.text_input("Search Description / Item No.", "")

        filtered_df = df.copy()

        if selected_cat != "All":
            filtered_df = filtered_df[filtered_df["Material Category"] == selected_cat]

        if selected_disc != "All":
            filtered_df = filtered_df[filtered_df["Discipline"] == selected_disc]

        if search_query:
            query = search_query.lower()
            filtered_df = filtered_df[
                filtered_df["Description"].astype(str).str.lower().str.contains(query)
                | filtered_df["BOQ Item No."].astype(str).str.lower().str.contains(query)
            ]

        # Tabs Section
        tab1, tab2, tab3 = st.tabs(["📊 Interactive Charts", "📋 Passport Data Table", "🏛️ Building Metadata"])

        with tab1:
            st.subheader("Material Distribution & Embodied Carbon")
            if CHART_PNG.exists():
                st.image(str(CHART_PNG), use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Embodied Carbon by Material Category (kg CO₂e)**")
                cat_carbon = filtered_df.groupby("Material Category")["Embodied Carbon A1-A3 (kg CO₂e)"].sum().reset_index()
                st.bar_chart(cat_carbon, x="Material Category", y="Embodied Carbon A1-A3 (kg CO₂e)")

            with col_b:
                st.write("**Item Count by Discipline**")
                disc_count = filtered_df.groupby("Discipline")["BOQ Item No."].count().reset_index()
                disc_count.columns = ["Discipline", "Count"]
                st.bar_chart(disc_count, x="Discipline", y="Count")

        with tab2:
            st.subheader(f"Extracted Records ({len(filtered_df)} showing)")
            st.dataframe(filtered_df, use_container_width=True, height=500)

        with tab3:
            st.subheader("Building Specifications & Metadata")
            st.json(meta)
    else:
        st.warning("No passport records found. Run `python -m src.pipeline` first to generate data.")


if __name__ == "__main__":
    main()
