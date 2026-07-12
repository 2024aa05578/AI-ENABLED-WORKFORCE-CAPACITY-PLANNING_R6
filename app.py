import streamlit as st
import pandas as pd

from workforce_model import calculate_workforce


st.set_page_config(
    page_title="AI Enabled Workforce & Capacity Planning",
    page_icon="🚀",
    layout="wide"
)


# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown(
    "<style>"
    ".main-title {"
    "font-size: 42px;"
    "font-weight: 800;"
    "color: #163B73;"
    "margin-bottom: 6px;"
    "}"
    ".main-subtitle {"
    "font-size: 17px;"
    "color: #4F5B67;"
    "margin-bottom: 20px;"
    "}"
    ".section-header {"
    "background: linear-gradient(90deg, #163B73, #2D9CDB);"
    "color: white;"
    "padding: 10px 16px;"
    "border-radius: 10px;"
    "font-size: 20px;"
    "font-weight: 700;"
    "margin-top: 22px;"
    "margin-bottom: 12px;"
    "}"
    ".metric-card {"
    "padding: 18px 16px;"
    "border-radius: 16px;"
    "box-shadow: 0 4px 14px rgba(0,0,0,0.10);"
    "text-align: center;"
    "margin-bottom: 12px;"
    "}"
    ".metric-label {"
    "font-size: 14px;"
    "font-weight: 600;"
    "color: white;"
    "margin-bottom: 6px;"
    "}"
    ".metric-value {"
    "font-size: 30px;"
    "font-weight: 800;"
    "color: white;"
    "}"
    ".blue-card {background: linear-gradient(135deg, #1B4F9C, #2D9CDB);}"
    ".green-card {background: linear-gradient(135deg, #00875A, #36B37E);}"
    ".purple-card {background: linear-gradient(135deg, #5E35B1, #9C27B0);}"
    ".orange-card {background: linear-gradient(135deg, #F57C00, #FFB300);}"
    ".red-card {background: linear-gradient(135deg, #C62828, #EF5350);}"
    ".teal-card {background: linear-gradient(135deg, #006064, #00ACC1);}"
    ".info-box {"
    "background: #EEF6FF;"
    "border-left: 6px solid #2D9CDB;"
    "padding: 14px 18px;"
    "border-radius: 10px;"
    "font-size: 15px;"
    "color: #233142;"
    "margin-bottom: 18px;"
    "}"
    ".sidebar-heading {"
    "background: linear-gradient(90deg, #163B73, #2D9CDB);"
    "color: white;"
    "padding: 8px 10px;"
    "border-radius: 8px;"
    "font-weight: 700;"
    "margin-top: 8px;"
    "margin-bottom: 8px;"
    "}"
    "div[data-testid='stSidebar'] {"
    "background: linear-gradient(180deg, #F2F7FF, #FFFFFF);"
    "}"
    "div[data-testid='stNumberInput'] input {"
    "border-radius: 10px;"
    "border: 1px solid #B5C7E3;"
    "background-color: #FFFFFF;"
    "}"
    "</style>",
    unsafe_allow_html=True
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
