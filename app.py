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
    "min-height: 118px;"
    "}"
    ".metric-label {"
    "font-size: 13px;"
    "font-weight: 600;"
    "color: white;"
    "margin-bottom: 6px;"
    "}"
    ".metric-value {"
    "font-size: 28px;"
    "font-weight: 800;"
    "color: white;"
    "}"
    ".blue-card {background: linear-gradient(135deg, #1B4F9C, #2D9CDB);}"
    ".green-card {background: linear-gradient(135deg, #00875A, #36B37E);}"
    ".purple-card {background: linear-gradient(135deg, #5E35B1, #9C27B0);}"
    ".orange-card {background: linear-gradient(135deg, #F57C00, #FFB300);}"
