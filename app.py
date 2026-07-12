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


def validate_and_clean_input(df):
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

    invalid_regions = sorted(
        set(df["Region"].unique()) - set(REGIONS)
    )

    invalid_products = sorted(
        set(df["Product"].unique()) - set(PRODUCTS)
    )

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
        st.error("Some numeric columns contain blank or invalid values.")
        st.stop()

    return df


def build_growth_inputs():
    default_bau = {
        "UPS": 25.0,
        "Cooling": 20.0,
        "Power Products": 15.0,
        "Power System": 18.0,
        "Industrial Automation": 12.0
    }

    default_dc = {
        "UPS": 40.0,
        "Cooling": 50.0,
        "Power Products": 10.0,
        "Power System": 20.0,
        "Industrial Automation": 5.0
    }

    st.sidebar.title("Region Wise Business Growth")

    growth_parameters = {}

    for region in REGIONS:
        growth_parameters[region] = {}

        with st.sidebar.expander(
            f"{region} Business Growth",
            expanded=(region == "North")
        ):
            header_col1, header_col2, header_col3 = st.columns([1.7, 1, 1])

            header_col1.markdown("**Product**")
            header_col2.markdown("**BAU %**")
            header_col3.markdown("**DC %**")

            for product in PRODUCTS:
                product_col, bau_col, dc_col = st.columns([1.7, 1, 1])

                product_col.write(product)

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

    return growth_parameters


def build_attrition_inputs():
    st.sidebar.title("BU Wise Attrition")

    attrition_parameters = {}

    with st.sidebar.expander("Attrition Inputs", expanded=False):
        header_col1, header_col2 = st.columns([1.8, 1])

        header_col1.markdown("**Product**")
        header_col2.markdown("**Attrition %**")

        for product in PRODUCTS:
            product_col, attrition_col = st.columns([1.8, 1])

            product_col.write(product)

            with attrition_col:
                attrition_value = st.number_input(
                    label=f"{product}_Attrition",
                    min_value=0.0,
                    max_value=30.0,
                    value=8.0,
                    step=0.5,
