import streamlit as st
import pandas as pd

from workforce_model import calculate_workforce


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Enabled Workforce & Capacity Planning",
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


# =====================================================
# SIDEBAR INPUTS
# =====================================================

st.sidebar.header("Planning Assumptions")


# -----------------------------
# Growth assumptions
# -----------------------------

st.sidebar.subheader("Region Wise Business Growth")

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

growth_parameters = {}

for region in REGIONS:
    growth_parameters[region] = {}

    with st.sidebar.expander(
        f"{region} Business Growth",
        expanded=(region == "North")
    ):
        col_product, col_bau, col_dc = st.columns([1.8, 1, 1])

        with col_product:
            st.markdown("**Product**")

        with col_bau:
            st.markdown("**BAU %**")

        with col_dc:
            st.markdown("**DC %**")

        for product in PRODUCTS:
            col_product, col_bau, col_dc = st.columns([1.8, 1, 1])

            with col_product:
                st.write(product)

            with col_bau:
                bau_value = st.number_input(
                    label=f"{region}_{product}_bau",
                    min_value=0.0,
                    max_value=100.0,
                    value=default_bau[product],
                    step=1.0,
                    key=f"{clean_key(region)}_{clean_key(product)}_bau",
                    label_visibility="collapsed"
                )

            with col_dc:
                dc_value = st.number_input(
                    label=f"{region}_{product}_dc",
                    min_value=0.0,
                    max_value=100.0,
                    value=default_dc[product],
                    step=1.0,
                    key=f"{clean_key(region)}_{clean_key(product)}_dc",
                    label_visibility="collapsed"
                )

            growth_parameters[region][product] = {
                "BAU": bau_value,
                "DC": dc_value
            }


# -----------------------------
# Attrition assumptions
# -----------------------------

st.sidebar.subheader("BU Wise Attrition")

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
                label=f"{product}_attrition",
                min_value=0.0,
                max_value=30.0,
                value=8.0,
                step=0.5,
                key=f"{clean_key(product)}_attrition",
                label_visibility="collapsed"
            )

        attrition_parameters[product] = attrition_value


# -----------------------------
# Productivity assumptions
# -----------------------------

st.sidebar.subheader("Workforce Productivity")

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

st.success("App loaded successfully")

st.markdown(
    """
    This application calculates workforce requirement based on:
    - Current service engineer count
    - Breakdown, PM and startup work orders
    - Average hours per work order
    - BAU growth
    - DC growth
    - Attrition
    - Engineer productivity assumptions
    """
)

uploaded_file = st.file_uploader(
    "Upload workforce_input.csv",
    type=["csv"]
)


# =====================================================
# IF NO FILE UPLOADED
# =====================================================

if uploaded_file is None:
    st.info("Please upload workforce_input.csv to start workforce planning.")
    st.stop()


# =====================================================
# READ AND VALIDATE FILE
# =====================================================

df = pd.read_csv(uploaded_file)

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
    st.error("Some numeric columns contain blank or invalid numeric values.")
    st.stop()


# =====================================================
# CALCULATE WORKFORCE
# =====================================================

result = calculate_workforce(
    df=df,
    growth_parameters=growth_parameters,
    attrition_parameters=attrition_parameters,
    productive_hours=productive_hours,
    working_days=working_days,
    target_utilization=target_utilization
)

if result.empty:
    st.error("No output generated. Please check your CSV data.")
    st.stop()

st.success("CSV uploaded successfully. Dashboard output is calculated below.")


# =====================================================
# DASHBOARD SUMMARY
# =====================================================

st.subheader("Dashboard Summary")

total_current = df["Current_SE"].sum()
total_available = round(result["Available Engineers"].sum(), 1)
total_required = round(result["Required Engineers"].sum(), 1)
total_hiring = int(result["Additional Required"].sum())
total_net_gap = round(result["Net Gap / Surplus"].sum(), 1)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Current SE", total_current)
kpi2.metric("Available After Attrition", total_available)
kpi3.metric("Required SE", total_required)
kpi4.metric("Hiring Gap", total_hiring)
kpi5.metric("Net Gap / Surplus", total_net_gap)


# =====================================================
# CHARTS
# =====================================================

st.markdown("---")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Required Engineers by Product")
    required_by_product = result.groupby("Product")["Required Engineers"].sum()
    st.bar_chart(required_by_product)

with chart_col2:
    st.subheader("Required Engineers by Region")
    required_by_region = result.groupby("Region")["Required Engineers"].sum()
    st.bar_chart(required_by_region)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Additional Hiring by Product")
    hiring_by_product = result.groupby("Product")["Additional Required"].sum()
    st.bar_chart(hiring_by_product)

with chart_col4:
    st.subheader("Additional Hiring by Region")
    hiring_by_region = result.groupby("Region")["Additional Required"].sum()
    st.bar_chart(hiring_by_region)


# =====================================================
# DETAIL TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Input Data",
        "Workforce Results",
        "Matrices",
        "Download"
    ]
)

with tab1:
    st.subheader("Uploaded Input Data")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Workforce Planning Results")
    st.dataframe(result, use_container_width=True)

with tab3:
    st.subheader("Required Engineers Matrix")
    required_matrix = result.pivot_table(
        values="Required Engineers",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )
    st.dataframe(required_matrix, use_container_width=True)

    st.subheader("Additional Hiring Matrix")
    hiring_matrix = result.pivot_table(
        values="Additional Required",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )
    st.dataframe(hiring_matrix, use_container_width=True)

    st.subheader("Net Gap / Surplus Matrix")
    net_gap_matrix = result.pivot_table(
        values="Net Gap / Surplus",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )
    st.dataframe(net_gap_matrix, use_container_width=True)

    st.info(
        "Net Gap / Surplus: Positive value means shortage. Negative value means surplus."
    )

    st.subheader("BAU Growth Matrix")
    bau_matrix = result.pivot_table(
        values="BAU Growth %",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="mean"
    )
    st.dataframe(bau_matrix, use_container_width=True)

    st.subheader("DC Growth Matrix")
    dc_matrix = result.pivot_table(
        values="DC Growth %",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="mean"
    )
    st.dataframe(dc_matrix, use_container_width=True)

    st.subheader("Total Growth Matrix")
    growth_matrix = result.pivot_table(
        values="Total Growth %",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="mean"
    )
    st.dataframe(growth_matrix, use_container_width=True)

with tab4:
    csv_output = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Workforce Planning Output",
        data=csv_output,
        file_name="workforce_planning_output.csv",
        mime="text/csv"
    )
