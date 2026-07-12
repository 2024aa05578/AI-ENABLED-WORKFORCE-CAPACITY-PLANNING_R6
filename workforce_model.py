import math
import pandas as pd


def calculate_workforce(
    df,
    growth_parameters,
    attrition_parameters,
    productive_hours,
    working_days,
    target_utilization
):
    results = []

    annual_capacity = productive_hours * working_days * 12
    effective_capacity = annual_capacity * target_utilization / 100

    for _, row in df.iterrows():
        region = row["Region"]
        product = row["Product"]

        region_product_params = growth_parameters.get(region, {}).get(
            product,
            {
                "BAU": 20,
                "DC": 0
            }
        )

        bau_growth = region_product_params["BAU"]
        dc_growth = region_product_params["DC"]
        attrition = attrition_parameters.get(product, 8)

        total_growth = bau_growth + dc_growth

        current_hours = (
            row["Breakdown_WO"] * row["Breakdown_Hrs"]
            + row["PM_WO"] * row["PM_Hrs"]
            + row["Startup_WO"] * row["Startup_Hrs"]
        )

        future_hours = current_hours * (1 + total_growth / 100)
        required_engineers = future_hours / effective_capacity
        available_engineers = row["Current_SE"] * (1 - attrition / 100)

        additional_required = max(
            math.ceil(required_engineers - available_engineers),
            0
        )

        results.append(
            {
                "Region": region,
                "Product": product,
                "BAU Growth %": bau_growth,
                "DC Growth %": dc_growth,
                "Total Growth %": total_growth,
                "Attrition %": attrition,
                "Productive Hrs/Day": productive_hours,
                "Working Days/Month": working_days,
                "Utilization %": target_utilization,
                "Annual Capacity": round(annual_capacity),
                "Effective Capacity": round(effective_capacity),
                "Current Hours": round(current_hours),
                "Future Hours": round(future_hours),
                "Required Engineers": round(required_engineers, 1),
                "Available Engineers": round(available_engineers, 1),
                "Additional Required": additional_required
            }
        )

    return pd.DataFrame(results)
