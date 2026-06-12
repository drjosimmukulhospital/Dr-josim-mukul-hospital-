import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. Database Configuration (SQLite for lifetime data storage)
conn = sqlite3.connect('hospital_management_v2.db', check_same_thread=False)
c = conn.cursor()

# Create Tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        referred_by TEXT,
        test_names TEXT,
        total_bill REAL,
        discount REAL,
        paid_amount REAL,
        due_amount REAL,
        date TEXT,
        month TEXT,
        year TEXT
    )
''')
conn.commit()

# Page Configurations
st.set_page_config(page_title="Dr. Jashim Mukul Hospital", layout="wide")

# Custom CSS for Clean Professional UI
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 25px; }
    .sidebar-title { font-size: 20px; font-weight: bold; color: #059669; }
    .metric-box { background-color: #F3F4F6; padding: 15px; rounded-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# Current Date & Time Context
current_date = datetime.now().strftime('%Y-%m-%d')
current_month = datetime.now().strftime('%B')
current_year = datetime.now().strftime('%Y')

# --- SIDEBAR MENU ---
st.sidebar.markdown("<h2 class='sidebar-title'>Dr. Jashim Mukul Hospital</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"📅 **Date:** {datetime.now().strftime('%d-%b-%Y')}")
st.sidebar.write("---")

menu = [
    "📝 Patient Registration & Billing", 
    "🔍 Due Clearance & Invoice Search", 
    "📊 Financial Dashboard & Lifetime Archive"
]
choice = st.sidebar.radio("Navigation Menu", menu)

# Live Daily Statistics in Sidebar
df_today = pd.read_sql_query(f"SELECT * FROM billing WHERE date='{current_date}'", conn)
today_revenue = df_today['paid_amount'].sum() if not df_today.empty else 0.0
today_due = df_today['due_amount'].sum() if not df_today.empty else 0.0

st.sidebar.write("---")
st.sidebar.markdown("### 📊 Today's Live Overview")
st.sidebar.metric("Total Collection Today", f"${today_revenue:,.2f}" if today_revenue > 0 else "0.00 TK")
st.sidebar.metric("Total Due Today", f"${today_due:,.2f}" if today_due > 0 else "0.00 TK")

# --- MAIN CONTENT AREA ---

# MODULE 1: Patient Entry & Billing
if choice == "📝 Patient Registration & Billing":
    st.markdown("<h1 class='main-title'>📝 Patient Registration & Lab Billing</h1>", unsafe_allow_html=True)
    
    st.subheader("1. Patient Personal Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_name = st.text_input("Patient Full Name *").upper()
        p_phone = st.text_input("Mobile / Phone Number *")
    with col2:
        p_age = st.number_input("Age (Years)", min_value=1, max_value=120, value=30)
    with col3:
        p_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        referred_by = st.text_input("Referred By (Doctor Name)").upper()
        if not referred_by: referred_by = "SELF"
        
    st.write("---")
    st.subheader("2. Investigation / Test Selection")
    
    # Pre-defined test catalog with pricing structure
    test_catalog = {
        "CBC (Complete Blood Count)": 400.0,
        "RBS (Random Blood Sugar)": 150.0,
        "Lipid Profile": 1000.0,
        "Ultrasonography (USG)": 800.0,
        "X-Ray Chest Chest PA View": 500.0,
        "Serum Creatinine": 350.0,
        "HBsAg": 400.0
    }
    
    selected_tests = st.multiselect("Select Requested Tests:", list(test_catalog.keys()))
    
    # Calculate Dynamic Subtotal
    subtotal = sum([test_catalog[test] for test in selected_tests])
    st.info(f"📋 **Total Test Fee (Subtotal):** {subtotal:,.2f} TK")
    
    st.write("---")
    st.subheader("3. Payment & Settlement")
    col4, col5 = st.columns(2)
    with col4:
        discount = st.number_input("Discount Allowed (TK)", min_value=0.0, value=0.0)
        paid_amount = st.number_input("Amount Paid (TK)", min_value=0.0, value=0.0)
    with col5:
        total_payable = subtotal - discount
        due_amount = total_payable - paid_amount
        if due_amount < 0: due_amount = 0.0
        
        st.markdown(f"### **Net Payable:** {total_payable:,.2f} TK")
        if due_amount > 0:
            st.markdown(f"⚠️ <span style='color:red; font-weight:bold;'>Total Due Amount: {due_amount:,.2f} TK</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"✅ <span style='color:green; font-weight:bold;'>Fully Paid</span>", unsafe_allow_html=True)

    if st.button("Save Transaction & Generate Invoice"):
        if p_name and p_phone and selected_tests:
            test_str = ", ".join(selected_tests)
            c.execute('''
                INSERT INTO billing (patient_name, age, gender, phone, referred_by, test_names, total_bill, discount, paid_amount, due_amount, date, month, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (p_name, p_age, p_gender, p_phone, referred_by, test_str, total_payable, discount, paid_amount, due_amount, current_date, current_month, current_year))
            conn.commit()
            st.success(f"🎉 Bill saved successfully for {p_name}! Permanent Database Record Created.")
        else:
            st.error("⚠️ Validation Error: Please fill Name, Phone, and select at least one Test.")

# MODULE 3: Lifetime Archive & Analytics
elif choice == "📊 Financial Dashboard & Lifetime Archive":
    st.markdown("<h1 class='main-title'>📊 Lifetime Financial Archive & Analytics</h1>", unsafe_allow_html=True)
    
    # Fetch all available years recorded in database
    years_df = pd.read_sql_query("SELECT DISTINCT year FROM billing ORDER BY year DESC", conn)
    
    if not years_df.empty:
        available_years = years_df['year'].tolist()
        selected_yr = st.selectbox("Select Financial Year to Audit:", available_years)
        
        # Load filtered data
        df_year = pd.read_sql_query(f"SELECT * FROM billing WHERE year='{selected_yr}'", conn)
        
        # Display Summary Cards
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Patients Documented", f"{len(df_year)} Patients")
        c2.metric("Total Net Earnings", f"{df_year['paid_amount'].sum():,.2f} TK")
        c3.metric("Total Outstanding Receivables (Due)", f"{df_year['due_amount'].sum():,.2f} TK")
        
        st.write("---")
        st.subheader(f"Detailed Transaction Logs for Year: {selected_yr}")
        st.dataframe(df_year[['id', 'patient_name', 'phone', 'test_names', 'total_bill', 'paid_amount', 'due_amount', 'date']])
    else:
        st.warning("No long-term historical records found in the system database yet.")
