# app.py (Main Landing Page)
import streamlit as st
import sqlite3

# Database Configuration (Multi-table for Hospital ERP)
conn = sqlite3.connect('dr_jashim_hospital_erp.db', check_same_thread=False)
c = conn.cursor()

# Create Tables for Billing and Admission once
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

# Set Page Configuration
st.set_page_config(page_title="Dr. Jashim Mukul Hospital", layout="wide")

# Welcome Dashboard Content
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏥 Dr. Jashim Mukul Hospital</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #4B5563;'>Diagnostic Centre & Hospital Management ERP</h3>", unsafe_allow_html=True)
st.write("---")

st.info("👈 Please select a module from the sidebar navigation to start managing Patient Registrations, Admissions, or Invoice Search.")

# Quick Overview Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.success("📝 **Diagnostic Billing**\n\nCreate invoices, manage test rates, and allow discounts.")
with col2:
    st.info("🏥 **Patient Admission**\n\nManage indoor patient admissions, allocate cabins, and process releases.")
with col3:
    st.warning("🔍 **Invoice & Due Search**\n\nLook up old receipts by phone number and clear outstanding dues.")
