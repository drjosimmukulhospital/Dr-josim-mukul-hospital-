# app.py (Main Controller)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Import modular pages from pages folder
from pages.Billing import show_billing_page
from pages.Search import show_search_page
from pages.Admission import show_admission_page

# Database Configuration (Multi-table for Hospital ERP)
conn = sqlite3.connect('dr_jashim_hospital_erp.db', check_same_thread=False)
c = conn.cursor()

# Create Tables for Billing and Admission
c.execute('''
    CREATE TABLE IF NOT EXISTS billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT, p_name TEXT, age INTEGER, gender TEXT, 
        phone TEXT, referred_by TEXT, test_names TEXT, total_bill REAL, 
        discount REAL, paid_amount REAL, due_amount REAL, date TEXT, year TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, p_name TEXT, age INTEGER, gender TEXT, 
        phone TEXT, bed_no TEXT, doctor_in_charge TEXT, admission_date TEXT, 
        status TEXT, discharge_date TEXT, total_hospital_bill REAL, paid_at_discharge REAL
    )
''')
conn.commit()

st.set_page_config(page_title="Dr. Jashim Mukul Hospital", layout="wide")

current_date = datetime.now().strftime('%Y-%m-%d')
current_year = datetime.now().strftime('%Y')

# --- SIDEBAR UI ( হুবহু রোগ মুক্তি ড্যাশবোর্ডের মতো ) ---
st.sidebar.markdown(<h2 style='color:#1E3A8A; text-align:center;'>Dr. Jashim Mukul Hospital</h2>, unsafe_allow_html=True)
st.sidebar.markdown(f"📅 **Date:** {datetime.now().strftime('%d %B, %Y')}")
st.sidebar.write("---")

st.sidebar.markdown("### 🛠️ MAIN NAVIGATION")
menu = [
    "📝 Diagnostic Billing", 
    "🏥 Patient Admission (রোগী ভর্তি)", 
    "🔍 Due Clearance & Invoice Search"
]
choice = st.sidebar.radio("Go To:", menu)

# Live Analytics Calculation for Sidebar
df_today_bill = pd.read_sql_query(f"SELECT paid_amount, due_amount FROM billing WHERE date='{current_date}'", conn)
df_today_adm = pd.read_sql_query(f"SELECT paid_at_discharge FROM admissions WHERE admission_date='{current_date}'", conn)

bill_paid = df_today_bill['paid_amount'].sum() if not df_today_bill.empty else 0.0
bill_due = df_today_bill['due_amount'].sum() if not df_today_bill.empty else 0.0
adm_paid = df_today_adm['paid_at_discharge'].sum() if not df_today_adm.empty else 0.0
total_collection = bill_paid + adm_paid

st.sidebar.write("---")
st.sidebar.markdown("### 📊 Today's Live Counter")
st.sidebar.metric("Total Cash Collection", f"{total_collection:,.2f} TK")
st.sidebar.metric("Total Pending Due", f"{bill_due:,.2f} TK")

# Routing to pages
if choice == "📝 Diagnostic Billing":
    show_billing_page(c, conn, current_date, current_year)
elif choice == "🏥 Patient Admission (রোগী ভর্তি)":
    show_admission_page(c, conn, current_date)
elif choice == "🔍 Due Clearance & Invoice Search":
    show_search_page(c, conn)
