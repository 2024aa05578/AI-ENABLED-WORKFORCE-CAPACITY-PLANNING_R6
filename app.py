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
# SIDEBAR - REGIONAL GROWTH INPUTS
# =====================================================

st.sidebar.title("Regional Growth Assumptions")

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

with st.sidebar.expander("Regional BAU and DC Growth", expanded=True):
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

st.sidebar.title("BU Wise Attrition")

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
    "This application estimates workforce requirement using regional BAU growth, "
    "regional DC growth, product attrition, and engineer productivity assumptions."
)

uploaded_file = st.file_uploader(
    "Upload workforce_input.csv",
    type=["csv"]
)


if uploaded_file is not None:
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
        st.error("Some numeric columns contain blank or invalid values.")
        st.stop()

    st.subheader("Input Data")
    st.dataframe(df, use_container_width=True)

    result = calculate_workforce(
        df=df,
        regional_growth=regional_growth,
        attrition_parameters=attrition_parameters,
        productive_hours=productive_hours,
        working_days=working_days,
        target_utilization=target_utilization
    )

    st.subheader("Dashboard Summary")

    total_current = df["Current_SE"].sum()

    total_available = round(
        result["Available Engineers"].sum(),
        1
    )

    total_bau_required = round(
        result["BAU Required Engineers"].sum(),
        1
    )

    total_dc_required = round(
        result["DC Incremental Engineers"].sum(),
        1
    )

    total_combined_required = round(
        result["Combined Required Engineers"].sum(),
        1
    )

    total_combined_hiring = int(
        result["Combined Additional Required"].sum()
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Current SE", total_current)
    c2.metric("Available After Attrition", total_available)
    c3.metric("BAU Required SE", total_bau_required)
    c4.metric("DC Addl. SE", total_dc_required)
    c5.metric("Combined Required SE", total_combined_required)
    c6.metric("Hiring Gap", total_combined_hiring)

    st.subheader("Workforce Planning Results")
    st.dataframe(result, use_container_width=True)

    st.subheader("BAU Requirement Table")

    bau_table = result.pivot_table(
        values="BAU Required Engineers",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )

    st.dataframe(
        add_total_row_and_column(bau_table).round(1),
        use_container_width=True
    )

    st.subheader("DC Addition Requirement Table")

    dc_table = result.pivot_table(
        values="DC Incremental Engineers",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )

    st.dataframe(
        add_total_row_and_column(dc_table).round(1),
        use_container_width=True
    )

    st.subheader("Combined BAU + DC Requirement Table")

    combined_table = result.pivot_table(
        values="Combined Required Engineers",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )

    st.dataframe(
        add_total_row_and_column(combined_table).round(1),
        use_container_width=True
    )

    st.subheader("Combined Hiring Requirement Table")

    hiring_table = result.pivot_table(
        values="Combined Additional Required",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )

    st.dataframe(
        add_total_row_and_column(hiring_table),
        use_container_width=True
    )

    st.subheader("Charts")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("Combined Required Engineers by Product")
        st.bar_chart(
            result.groupby("Product")["Combined Required Engineers"].sum()
        )

    with chart_col2:
        st.write("Combined Required Engineers by Region")
        st.bar_chart(
            result.groupby("Region")["Combined Required Engineers"].sum()
        )

    csv_output = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Workforce Planning Output",
        data=csv_output,
        file_name="workforce_planning_output.csv",
        mime="text/csv"
    )

else:
    st.info("Upload workforce_input.csv")
