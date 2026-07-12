import streamlit as st
import pandas as pd

from workforce_model import calculate_workforce


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Enabled Workforce & Capacity Planning",
    page_icon="🚀",
    layout="wide"
)


# =====================================================
# MASTER DATA
# =====================================================

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
    return (
        str(text)
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


def add_total_row_and_column(matrix):
    matrix = matrix.copy()
    matrix["Total"] = matrix.sum(axis=1)

    total_row = pd.DataFrame(matrix.sum(axis=0)).T
    total_row.index = ["Total"]

    matrix = pd.concat([matrix, total_row])

    return matrix


# =====================================================
# SIDEBAR - REGIONAL GROWTH INPUTS
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

        with col_bau:
            bau_value = st.number_input(
                label=f"{region} BAU Growth %",
                min_value=0.0,
                max_value=100.0,
                value=default_bau_region[region],
                step=1.0,
                key=f"{clean_key(region)}_bau_growth",
                label_visibility="collapsed"
            )

        with col_dc:
            dc_value = st.number_input(
                label=f"{region} DC Growth %",
                min_value=0.0,
                max_value=100.0,
                value=default_dc_region[region],
                step=1.0,
                key=f"{clean_key(region)}_dc_growth",
                label_visibility="collapsed"
            )

        regional_growth[region] = {
            "BAU": bau_value,
            "DC": dc_value
        }


# =====================================================
# SIDEBAR - ATTRITION INPUTS
# =====================================================

st.sidebar.subheader("👥 BU Wise Attrition")

attrition_parameters = {}

with st.sidebar.expander("Attrition Inputs", expanded=False):
    col_product, col_attrition = st.columns([1.8, 1])

    with col_product:
        st.markdown("**Product**")

    with col_attrition:
        st.markdown("**Attrition %**")

    for product in PRODUCTS:
        col_product, col_attrition = st.columns([1.8, 1])

        with col_product:
            st.write(product)

        with col_attrition:
            attrition_value = st.number_input(
                label=f"{product} Attrition %",
                min_value=0.0,
                max_value=30.0,
                value=8.0,
                step=0.5,
                key=f"{clean_key(product)}_attrition",
                label_visibility="collapsed"
            )

        attrition_parameters[product] = attrition_value


# =====================================================
# SIDEBAR - PRODUCTIVITY INPUTS
# =====================================================

st.sidebar.subheader("⚙️ Workforce Productivity")

productive_hours = st.sidebar.number_input(
    "Productive Hours Per Day",
    min_value=1.0,
    max_value=24.0,
    value=7.0,
    step=0.5
)

working_days = st.sidebar.number_input(
    "Working Days Per Month",
    min_value=1,
    max_value=31,
    value=20,
    step=1
)

target_utilization = st.sidebar.number_input(
    "Target Engineer Utilization %",
    min_value=1.0,
    max_value=100.0,
    value=90.0,
    step=1.0
)


# =====================================================
# MAIN PAGE
# =====================================================

st.title("🚀 AI Enabled Workforce & Capacity Planning")

st.info(
    "Enter regional BAU and DC growth values in the sidebar, upload workforce_input.csv, "
    "and review BAU requirement, DC addition, combined requirement and hiring gap."
)

uploaded_file = st.file_uploader(
