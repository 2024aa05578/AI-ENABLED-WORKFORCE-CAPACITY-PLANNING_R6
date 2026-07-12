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

REGIONS = ["North", "South", "East", "West"]

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


# =====================================================
# SIDEBAR - REGION AND PRODUCT WISE BUSINESS GROWTH
# =====================================================

st.sidebar.title("Region Wise Business Growth")

growth_parameters = {}

default_bau = {
    "UPS": 25,
    "Cooling": 20,
    "Power Products": 15,
    "Power System": 18,
    "Industrial Automation": 12
}

default_dc = {
    "UPS": 40,
    "Cooling": 50,
    "Power Products": 10,
    "Power System": 20,
    "Industrial Automation": 5
}

for region in REGIONS:
    growth_parameters[region] = {}

    with st.sidebar.expander(
        f"{region} Business Growth",
        expanded=(region == "North")
    ):
        header_col1, header_col2, header_col3 = st.columns([1.6, 1, 1])

        with header_col1:
            st.markdown("**Product**")

        with header_col2:
            st.markdown("**BAU %**")

        with header_col3:
            st.markdown("**DC %**")

        for product in PRODUCTS:
            product_col, bau_col, dc_col = st.columns([1.6, 1, 1])

            with product_col:
                st.write(product)

            with bau_col:
                bau_value = st.number_input(
                    label=f"{region}_{product}_BAU",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(default_bau[product]),
                    step=1.0,
                    key=f"{clean_key(region)}_{clean_key(product)}_bau",
                    label_visibility="collapsed"
                )

            with dc_col:
                dc_value = st.number_input(
                    label=f"{region}_{product}_DC",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(default_dc[product]),
                    step=1.0,
                    key=f"{clean_key(region)}_{clean_key(product)}_dc",
                    label_visibility="collapsed"
                )

            growth_parameters[region][product] = {
                "BAU": bau_value,
                "DC": dc_value
            }


# =====================================================
# SIDEBAR - ATTRITION PARAMETERS
# =====================================================

st.sidebar.title("BU Wise Attrition")

attrition_parameters = {}

with st.sidebar.expander("Attrition %", expanded=False):
    header_col1, header_col2 = st.columns([1.8, 1])

    with header_col1:
        st.markdown("**Product**")

    with header_col2:
        st.markdown("**Attrition %**")

    for product in PRODUCTS:
        product_col, attrition_col = st.columns([1.8, 1])

        with product_col:
            st.write(product)

        with attrition_col:
            attrition_value = st.number_input(
                label=f"{product}_Attrition",
                min_value=0.0,
                max_value=30.0,
                value=8.0,
                step=0.5,
                key=f"{clean_key(product)}_attrition",
                label_visibility="collapsed"
            )

