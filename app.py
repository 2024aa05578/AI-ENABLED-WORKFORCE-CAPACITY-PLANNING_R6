import streamlit as st
import pandas as pd

from workforce_model import calculate_workforce

st.set_page_config(
    page_title="AI Enabled Workforce & Capacity Planning",
    page_icon="🚀",
    layout="wide"
)

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
    return str(text).lower().replace(" ", "_").replace("-", "_").replace("/", "_")


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

    with st.sidebar.expander(f"{region} Business Growth", expanded=(region == "North")):
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
                min_value=-100,
                max_value=100,
                value=default_dc[product],
                key=f"{clean_key(region)}_{clean_key(product)}_dc"
            )

            growth_parameters[region][product]["DC"] = dc_value


st.sidebar.title("BU Wise Attrition")

attrition_parameters = {}

with st.sidebar.expander("Attrition %", expanded=False):
    for product in PRODUCTS:
        attrition_parameters[product] = st.slider(
            f"{product} Attrition %",
            min_value=0,
            max_value=30,
            value=8,
            key=f"{clean_key(product)}_attrition"
        )


st.sidebar.title("Workforce Productivity")

productive_hours = st.sidebar.slider(
    "Productive Hours Per Day",
    min_value=4,
    max_value=10,
    value=7
)

working_days = st.sidebar.slider(
    "Working Days Per Month",
    min_value=15,
    max_value=26,
    value=20
)

target_utilization = st.sidebar.slider(
    "Target Engineer Utilization %",
    min_value=60,
    max_value=100,
    value=90
)


st.title("AI Enabled Workforce & Capacity Planning")

st.write(
    """
    This application estimates service engineer requirements based on:

    - Current service engineer count
    - Breakdown, preventive maintenance and startup work orders
    - Average hours per work order type
    - Region-wise and product-wise BAU growth
    - Region-wise and product-wise DC growth
    - Positive DC growth adds business load
    - Zero DC growth ignores DC impact
    - Negative DC growth deletes or reduces DC impact
    - BU-wise attrition
    - Engineer productivity assumptions
    """
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
        st.error("Some numeric columns contain blank or invalid values.")
        st.stop()

    st.subheader("Input Data")
    st.dataframe(df, use_container_width=True)

    result = calculate_workforce(
        df=df,
        growth_parameters=growth_parameters,
        attrition_parameters=attrition_parameters,
        productive_hours=productive_hours,
        working_days=working_days,
        target_utilization=target_utilization
    )

    st.subheader("Workforce Planning Results")
    st.dataframe(result, use_container_width=True)

    total_current = df["Current_SE"].sum()
    total_available = round(result["Available Engineers"].sum(), 1)
    total_required = round(result["Required Engineers"].sum(), 1)
    total_hiring = int(result["Additional Required"].sum())

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    c1.metric("Current SE", total_current)
    c2.metric("Available After Attrition", total_available)
    c3.metric("Required SE", total_required)
    c4.metric("Hiring Gap", total_hiring)
    c5.metric("Hrs/Day", productive_hours)
    c6.metric("Days/Month", working_days)
    c7.metric("Utilization %", target_utilization)

    st.subheader("Hiring by Product Line")
    hiring_by_product = result.groupby("Product")["Additional Required"].sum()
    st.bar_chart(hiring_by_product)

    st.subheader("Hiring by Region")
    hiring_by_region = result.groupby("Region")["Additional Required"].sum()
    st.bar_chart(hiring_by_region)

    st.subheader("Hiring Matrix - Product vs Region")
    hiring_matrix = result.pivot_table(
        values="Additional Required",
        index="Product",
        columns="Region",
        fill_value=0,
        aggfunc="sum"
    )
    st.dataframe(hiring_matrix, use_container_width=True)

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

    csv_output = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Workforce Planning Output",
        data=csv_output,
        file_name="workforce_planning_output.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload workforce_input.csv to start workforce planning.")
