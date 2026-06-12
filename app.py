# app.py (Main Controller)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Import pages from the new folder
from pages.1_Billing import show_billing_page
from pages.2_Search import show_search_page

# Database Configuration
conn = sqlite3.connect('hospital_management_v3.db', check_same_thread=False)
c = conn.cursor()

st.set_page_config(page_title="Dr. Jashim Mukul Hospital", layout="wide")

# Shared Test Catalog
test_catalog = {
    "CBC (Complete Blood Count)": 400.0,
    "RBS (Random Blood Sugar)": 150.0,
    "Lipid Profile": 1000.0,
    "Ultrasonography (USG)": 800.0,
    "X-Ray Chest PA View": 500.0,
    "Serum Creatinine": 350.0,
    "HBsAg": 400.0
}

current_date = datetime.now().strftime('%Y-%m-%d')
current_month = datetime.now().strftime('%B')
current_year = datetime.now().strftime('%Y')

# --- SIDEBAR OVERVIEW ---
st.sidebar.markdown("<h2 style='color:#059669;'>Dr. Jashim Mukul Hospital</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"📅 **Date:** {datetime.now().strftime('%d-%b-%Y')}")
st.sidebar.write("---")

menu = ["📝 Billing Page", "🔍 Search & Due Clearance"]
choice = st.sidebar.radio("Navigation Menu", menu)

# Live Statistics
df_today = pd.read_sql_query(f"SELECT * FROM billing WHERE date='{current_date}'", conn)
today_revenue = df_today['paid_amount'].sum() if not df_today.empty else 0.0
today_due = df_today['due_amount'].sum() if not df_today.empty else 0.0

st.sidebar.write("---")
st.sidebar.metric("Total Collection Today", f"{today_revenue:,.2f} TK")
st.sidebar.metric("Total Due Today", f"{today_due:,.2f} TK")

# --- CONNECTING PAGES BASED ON CHOICE ---
if choice == "📝 Billing Page":
    show_billing_page(c, conn, test_catalog, current_date, current_month, current_year)
elif choice == "🔍 Search & Due Clearance":
    show_search_page(c, conn)
