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
            bau_value = st.number_input(
                f"{region} - {product} BAU Growth %",
                min_value=0.0,
                max_value=100.0,
                value=float(default_bau[product]),
                step=1.0,
                key=f"{clean_key(region)}_{clean_key(product)}_bau"
            )

            growth_parameters[region][product] = {
                "BAU": bau_value,
                "DC": 0.0
            }

        st.markdown("---")
        st.markdown("### DC Growth")

        for product in PRODUCTS:
            dc_value = st.number_input(
                f"{region} - {product} DC Growth %",
                min_value=0.0,
                max_value=100.0,
                value=float(default_dc[product]),
                step=1.0,
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
        attrition_value = st.number_input(
            f"{product} Attrition %",
            min_value=0.0,
            max_value=30.0,
            value=8.0,
            step=1.0,
            key=f"{clean_key(product)}_attrition"
        )

        attrition_parameters[product] = attrition_value


# =====================================================
# SIDEBAR - PRODUCTIVITY PARAMETERS
# =====================================================

st.sidebar.title("Workforce Productivity")

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

st.title("AI Enabled Workforce & Capacity Planning")

st.write(
    """
    This application estimates service engineer requirements based on:

    - Current service engineer count
