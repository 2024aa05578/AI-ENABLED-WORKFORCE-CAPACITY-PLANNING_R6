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

st.sidebar.subheader("🌍 Regional Growth")

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

with st.sidebar.expander("BAU and DC Growth by Region", expanded=True):
    col_region, col_bau, col_dc = st.columns([1.4, 1, 1])

    with col_region:
        st.markdown("**Region**")

    with col_bau:
        st.markdown("**BAU %**")

    with col_dc:
        st.markdown("**DC %**")

    for region in REGIONS:
        col_region, col_bau, col_dc = st.columns([1.4, 1, 1])

        with col_region:
            st.write(region)

