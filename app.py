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

st.sidebar.header("Planning Assumptions")

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

st.sidebar.subheader("Regional Growth")

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
                min_value=0.0,
                max_value=100.0,
                value=default_dc_region[region],
                step=1.0,
                key=f"{clean_key(region)}_dc_growth"
            )

        regional_growth[region] = {
            "BAU": bau_value,
            "DC": dc_value
        }


st.sidebar.subheader("BU Wise Attrition")

attrition_parameters = {}

with st.sidebar.expander("Attrition Inputs", expanded=False):
    for product in PRODUCTS:
        attrition_parameters[product] = st.number_input(
            f"{product} Attrition %",
            min_value=0.0,
            max_value=30.0,
            value=8.0,
            step=0.5,
            key=f"{clean_key(product)}_attrition"
        )


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

st.info(
    "Enter regional BAU and DC growth values in the sidebar, upload workforce_input.csv, "
    "and review BAU requirement, DC addition, combined requirement and hiring gap."
)

uploaded_file = st.file_uploader("Upload workforce_input.csv", type=["csv"])

if uploaded_file is None:
    st.warning("Please upload workforce_input.csv to start workforce planning.")
    st.stop()


# =====================================================
# READ AND VALIDATE CSV
# =====================================================

df = pd.read_csv(uploaded_file)
df.columns = df.columns.str.strip()

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

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

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


# =====================================================
# CALCULATE WORKFORCE
# =====================================================

result = calculate_workforce(
    df=df,
    regional_growth=regional_growth,
    attrition_parameters=attrition_parameters,
    productive_hours=productive_hours,
    working_days=working_days,
    target_utilization=target_utilization
)

if result.empty:
    st.error("No output generated. Please check the uploaded CSV.")
    st.stop()

required_result_columns = [
    "Available Engineers",
    "BAU Required Engineers",
    "DC Incremental Engineers",
    "Combined Required Engineers",
    "Combined Additional Required"
]

missing_result_columns = [col for col in required_result_columns if col not in result.columns]

if missing_result_columns:
    st.error(
        "workforce_model.py is not updated. Missing result columns: "
        + str(missing_result_columns)
    )
    st.stop()

st.success("CSV uploaded successfully. Dashboard output is calculated below.")


# =====================================================
# DASHBOARD SUMMARY
# =====================================================

st.subheader("Dashboard Summary")

total_current = df["Current_SE"].sum()
total_available = round(result["Available Engineers"].sum(), 1)
total_bau_required = round(result["BAU Required Engineers"].sum(), 1)
total_dc_required = round(result["DC Incremental Engineers"].sum(), 1)
total_combined_required = round(result["Combined Required Engineers"].sum(), 1)
total_combined_hiring = int(result["Combined Additional Required"].sum())

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

kpi1.metric("Current SE", total_current)
kpi2.metric("Available After Attrition", total_available)
kpi3.metric("BAU Required SE", total_bau_required)
kpi4.metric("DC Addl. SE", total_dc_required)
kpi5.metric("Combined Required SE", total_combined_required)
kpi6.metric("Hiring Gap", total_combined_hiring)


# =====================================================
# VISUAL DASHBOARD
# =====================================================

st.markdown("---")
st.subheader("Visual Dashboard")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### Combined Required Engineers by Product")
    product_required = result.groupby("Product")["Combined Required Engineers"].sum()
    st.bar_chart(product_required)

with chart_col2:
    st.markdown("#### Combined Required Engineers by Region")
    region_required = result.groupby("Region")["Combined Required Engineers"].sum()
    st.bar_chart(region_required)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("#### Combined Hiring Requirement by Product")
    product_hiring = result.groupby("Product")["Combined Additional Required"].sum()
    st.bar_chart(product_hiring)

with chart_col4:
    st.markdown("#### Combined Hiring Requirement by Region")
    region_hiring = result.groupby("Region")["Combined Additional Required"].sum()
    st.bar_chart(region_hiring)


# =====================================================
# DETAIL TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Input Data",
        "Full Results",
        "BAU Requirement",
        "DC and Combined",
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
    st.subheader("BAU Requirement Table")

    bau_table = result.pivot_table(
        values="BAU Required Engineers",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )

    bau_total = add_total_row_and_column(bau_table).round(1)

    st.dataframe(
        bau_total,
        use_container_width=True
    )


with tab4:
    st.subheader("DC Addition Requirement Table")

    dc_table = result.pivot_table(
        values="DC Incremental Engineers",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )

    dc_total = add_total_row_and_column(dc_table).round(1)

    st.dataframe(
        dc_total,
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

    combined_total = add_total_row_and_column(combined_table).round(1)

    st.dataframe(
        combined_total,
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

    hiring_total = add_total_row_and_column(hiring_table).round(1)

    st.dataframe(
        hiring_total,
        use_container_width=True
    )


with tab5:
    st.subheader("Download Output")

    csv_output = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Workforce Planning Output",
        data=csv_output,
        file_name="workforce_planning_output.csv",
        mime="text/csv"
    )
