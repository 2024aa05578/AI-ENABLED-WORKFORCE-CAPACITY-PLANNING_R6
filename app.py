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
        st.markdown("### BAU Growth")

        for product in PRODUCTS:
            bau_value = st.slider(
                f"{region} - {product} BAU Growth %",
                min_value=0,
                max_value=100,
                value=default_bau[product],
                key=f"{clean_key(region)}_{clean_key(product)}_bau"
            )

            growth_parameters[region][product] = {
                "BAU": bau_value,
                "DC": 0
            }

        st.markdown("---")
        st.markdown("### DC Growth")

        for product in PRODUCTS:
            dc_value = st.slider(
                f"{region} - {product} DC Growth %",
                min_value=0,
                max_value=100,
                value=default_dc[product],
                key=f"{clean_key(region)}_{clean_key(product)}_dc"
            )

            growth_parameters[region][product]["DC"] = dc_value


# =====================================================
# SIDEBAR - ATTRITION PARAMETERS
# =====================================================

st.sidebar.title("BU Wise Attrition")

attrition_parameters = {}

with st.sidebar.expander("Attrition %", expanded=False):
    for product in PRODUCTS:
