import streamlit as st
import pandas as pd

from workforce_model import calculate_workforce


st.set_page_config(
    page_title="AI Enabled Workforce & Capacity Planning",
    page_icon="🚀",
    layout="wide"
)

REGIONS = ["North", "West", "South", "East"]

PRODUCTS = [
    "UPS",
    "Cooling",
    "Power Products",
    "Power System",
    "Industrial Automation"
]

PRODUCT_ALIASES = {
    "Power Product": "Power Products",
    "Power Products": "Power Products",
    "Power System": "Power System",
    "Industrial Automation": "Industrial Automation",
    "Industiral Automation": "Industrial Automation",
    "UPS": "UPS",
    "Cooling": "Cooling"
}


def clean_key(text):
    return str(text).lower().replace(" ", "_").replace("-", "_").replace("/", "_")


def add_total_row_and_column(matrix):
    matrix = matrix.copy()
    matrix["Total"] = matrix.sum(axis=1)

    total_row = pd.DataFrame(matrix.sum(axis=0)).T
    total_row.index = ["Total"]

    matrix = pd.concat([matrix, total_row])
    return matrix


# =====================================================
# SIDEBAR INPUTS
# =====================================================

st.sidebar.header("📌 Planning Assumptions")
st.sidebar.info("Enter regional growth, product attrition and productivity assumptions below.")

regional_growth = {}

default_bau_region = {
    "North": 20.0,
    "West": 30.0,
    "South": 22.0,
    "East": 15.0
}

default_dc_region = {
    "North": 10.0,
    "West": 20.0,
    "South": 10.0,
    "East": 5.0
}

st.sidebar.subheader("🌍 Regional Growth")

for region in REGIONS:
    with st.sidebar.expander(f"{region} Growth", expanded=(region == "North")):
        bau_col, dc_col = st.columns(2)

        with bau_col:
            bau_value = st.number_input(
                "BAU %",
                min_value=0.0,
                max_value=100.0,
                value=default_bau_region[region],
                step=1.0,
                key=f"{clean_key(region)}_bau_growth"
            )

        with dc_col:
            dc_value = st.number_input(
                "DC %",
