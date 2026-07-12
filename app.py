import copy
from io import StringIO

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


# =====================================================
# DEFAULT ASSUMPTIONS
# =====================================================

DEFAULT_GROWTH_PARAMETERS = {
    "North": {
        "UPS": {"BAU": 20.0, "DC": 10.0},
        "Cooling": {"BAU": 20.0, "DC": 10.0},
        "Power Products": {"BAU": 15.0, "DC": 5.0},
        "Power System": {"BAU": 15.0, "DC": 5.0},
        "Industrial Automation": {"BAU": 15.0, "DC": 5.0}
    },
    "West": {
        "UPS": {"BAU": 30.0, "DC": 20.0},
        "Cooling": {"BAU": 30.0, "DC": 20.0},
        "Power Products": {"BAU": 20.0, "DC": 10.0},
        "Power System": {"BAU": 20.0, "DC": 10.0},
        "Industrial Automation": {"BAU": 20.0, "DC": 10.0}
    },
    "South": {
        "UPS": {"BAU": 22.0, "DC": 10.0},
        "Cooling": {"BAU": 22.0, "DC": 10.0},
        "Power Products": {"BAU": 20.0, "DC": 5.0},
        "Power System": {"BAU": 20.0, "DC": 5.0},
        "Industrial Automation": {"BAU": 20.0, "DC": 5.0}
    },
    "East": {
        "UPS": {"BAU": 15.0, "DC": 5.0},
        "Cooling": {"BAU": 15.0, "DC": 5.0},
        "Power Products": {"BAU": 15.0, "DC": 5.0},
        "Power System": {"BAU": 15.0, "DC": 5.0},
        "Industrial Automation": {"BAU": 15.0, "DC": 5.0}
    }
}

DEFAULT_ATTRITION = {
    "UPS": 8.0,
    "Cooling": 8.0,
    "Power Products": 8.0,
    "Power System": 8.0,
    "Industrial Automation": 8.0
}

DEFAULT_PRODUCTIVITY = {
    "productive_hours": 7.0,
    "working_days": 20,
    "target_utilization": 90.0
}


# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================

if "growth_parameters" not in st.session_state:
    st.session_state.growth_parameters = copy.deepcopy(DEFAULT_GROWTH_PARAMETERS)

if "attrition_parameters" not in st.session_state:
    st.session_state.attrition_parameters = copy.deepcopy(DEFAULT_ATTRITION)

if "productive_hours" not in st.session_state:
    st.session_state.productive_hours = DEFAULT_PRODUCTIVITY["productive_hours"]

if "working_days" not in st.session_state:
    st.session_state.working_days = DEFAULT_PRODUCTIVITY["working_days"]

if "target_utilization" not in st.session_state:
    st.session_state.target_utilization = DEFAULT_PRODUCTIVITY["target_utilization"]

if "input_df" not in st.session_state:
    st.session_state.input_df = None


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def clean_key(text):
    return str(text).lower().replace(" ", "_").replace("-", "_").replace("/", "_")


def add_total_row_and_column(matrix):
    matrix = matrix.copy()
    matrix["Total"] = matrix.sum(axis=1)

    total_row = pd.DataFrame(matrix.sum(axis=0)).T
    total_row.index = ["Total"]

    matrix = pd.concat([matrix, total_row])
    return matrix


def safe_read_csv(uploaded_file):
    raw_bytes = uploaded_file.getvalue()

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin1")

    cleaned_lines = []

    for line in text.splitlines():
        line = line.strip()

        while line.endswith(","):
            line = line[:-1]

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    df = pd.read_csv(StringIO(cleaned_text), engine="python")
    df.columns = df.columns.str.strip()

    unnamed_columns = [
        col for col in df.columns
        if str(col).startswith("Unnamed")
    ]

    if unnamed_columns:
        df = df.drop(columns=unnamed_columns)

    return df


def validate_input_data(df):
    required_columns = [
        "Region",
        "Product",
        "Current_SE",
        "Breakdown_WO",
        "Breakdown_Hrs",
        "PM_WO",
        "PM_Hrs",
        "Startup_WO",
        "Startup_Hrs"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}")
        st.stop()

    df = df.copy()

    df["Region"] = df["Region"].astype(str).str.strip()
    df["Product"] = df["Product"].astype(str).str.strip()
    df["Product"] = df["Product"].replace(PRODUCT_ALIASES)

    invalid_regions = sorted(set(df["Region"].unique()) - set(REGIONS))
    invalid_products = sorted(set(df["Product"].unique()) - set(PRODUCTS))

    if invalid_regions:
        st.error(f"Invalid regions found in uploaded file: {invalid_regions}")
        st.stop()

    if invalid_products:
        st.error(f"Invalid products found in uploaded file: {invalid_products}")
        st.stop()

    numeric_columns = [
        "Current_SE",
        "Breakdown_WO",
        "Breakdown_Hrs",
        "PM_WO",
        "PM_Hrs",
        "Startup_WO",
        "Startup_Hrs"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[numeric_columns].isnull().any().any():
        st.error("Some numeric columns contain blank or invalid numeric values.")
        st.stop()

    return df


# =====================================================
# SIDEBAR FORM
# =====================================================

st.sidebar.header("Planning Assumptions")

st.sidebar.info(
    "Update product-wise BAU and DC growth under each region, then click Apply Assumptions."
)

with st.sidebar.form("planning_assumptions_form"):
    st.subheader("Region and Product Wise Growth")

    updated_growth_parameters = {}

    for region in REGIONS:
        updated_growth_parameters[region] = {}

        st.markdown(f"### {region} Growth")

        col_product, col_bau, col_dc = st.columns([1.8, 1, 1])

        with col_product:
            st.markdown("**Product**")

        with col_bau:
            st.markdown("**BAU %**")

        with col_dc:
            st.markdown("**DC %**")

        for product in PRODUCTS:
            product_col, bau_col, dc_col = st.columns([1.8, 1, 1])

            with product_col:
                st.write(product)

            with bau_col:
                bau_value = st.number_input(
                    "BAU",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(st.session_state.growth_parameters[region][product]["BAU"]),
                    step=1.0,
                    key=f"{clean_key(region)}_{clean_key(product)}_bau_form",
                    label_visibility="collapsed"
                )

            with dc_col:
                dc_value = st.number_input(
                    "DC",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(st.session_state.growth_parameters[region][product]["DC"]),
                    step=1.0,
                    key=f"{clean_key(region)}_{clean_key(product)}_dc_form",
                    label_visibility="collapsed"
                )

            updated_growth_parameters[region][product] = {
                "BAU": bau_value,
                "DC": dc_value
            }

        st.markdown("---")

    st.subheader("BU Wise Attrition")

    updated_attrition = {}

    for product in PRODUCTS:
        updated_attrition[product] = st.number_input(
            f"{product} Attrition %",
            min_value=0.0,
            max_value=30.0,
            value=float(st.session_state.attrition_parameters[product]),
            step=0.5,
            key=f"{clean_key(product)}_attrition_form"
        )

    st.markdown("---")

    st.subheader("Workforce Productivity")

    updated_productive_hours = st.number_input(
        "Productive Hours Per Day",
        min_value=1.0,
        max_value=24.0,
        value=float(st.session_state.productive_hours),
        step=0.5
    )

    updated_working_days = st.number_input(
        "Working Days Per Month",
