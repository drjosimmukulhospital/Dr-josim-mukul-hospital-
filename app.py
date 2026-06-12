# app.py (Full Hospital ERP with A4 Auto-Print)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Database Setup for Lifetime Data Storage
conn = sqlite3.connect('dr_jashim_hospital_final.db', check_same_thread=False)
c = conn.cursor()

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

# Page Setups
st.set_page_config(page_title="Dr. Jashim Mukul Hospital ERP", layout="wide")

# CSS for A4 Styling and Hiding Dashboard Elements During Print
st.markdown("""
    <style>
    /* Styling for A4 Print */
    .a4-receipt {
        width: 210mm;
        min-height: 297mm;
        padding: 20mm;
        margin: 10px auto;
        border: 1px solid #D3D3D3;
        background: white;
        color: black;
        font-family: Arial, sans-serif;
    }
    .invoice-title { text-align: center; color: #1E3A8A; font-size: 26px; font-weight: bold; margin-bottom: 5px; }
    .invoice-subtitle { text-align: center; font-size: 14px; color: #4B5563; margin-bottom: 20px; }
    .info-table, .item-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .item-table th, .item-table td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }
    .item-table th { background-color: #F3F4F6; color: black; }
    .total-section { float: right; width: 40%; margin-top: 20px; font-size: 14px; line-height: 1.8; }
    
    /* Print Command */
    @media print {
        body * { visibility: hidden; }
        .printable-section, .printable-section * { visibility: visible; }
        .printable-section { position: absolute; left: 0; top: 0; width: 100%; }
        .no-print { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

current_date = datetime.now().strftime('%Y-%m-%d')
current_year = datetime.now().strftime('%Y')

# --- SIDEBAR UI (হুবহু রোগ মুক্তি ড্যাশবোর্ডের রেপ্লিকা) ---
st.sidebar.markdown("<h2 style='color:#1E3A8A; text-align:center;'>Dr. Jashim Mukul Hospital</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"📅 **Date:** {datetime.now().strftime('%d %B, %Y')}")
st.sidebar.write("---")

st.sidebar.markdown("### 🛠️ ERP MODULES")
choice = st.sidebar.radio("Go To:", ["📝 Diagnostic Billing & A4 Print", "🏥 Patient Admission", "🔍 Search & Due Clearance"])

# Live Accounts Overview on Sidebar
df_today_bill = pd.read_sql_query(f"SELECT paid_amount, due_amount FROM billing WHERE date='{current_date}'", conn)
df_today_adm = pd.read_sql_query(f"SELECT paid_at_discharge FROM admissions WHERE admission_date='{current_date}'", conn)
bill_paid = df_today_bill['paid_amount'].sum() if not df_today_bill.empty else 0.0
bill_due = df_today_bill['due_amount'].sum() if not df_today_bill.empty else 0.0
total_collection = bill_paid + (df_today_adm['paid_at_discharge'].sum() if not df_today_adm.empty else 0.0)

st.sidebar.write("---")
st.sidebar.markdown("### 📊 Today's Cash Flow")
st.sidebar.metric("Total Received Cash", f"{total_collection:,.2f} TK")
st.sidebar.metric("Total Pending Due", f"{bill_due:,.2f} TK")

# --- Initialize Print Session State ---
if 'receipt_triggered' not in st.session_state:
    st.session_state.receipt_triggered = False

# --- MODULE 1: DIAGNOSTIC BILLING & A4 PRINT ---
if choice == "📝 Diagnostic Billing & A4 Print":
    st.markdown("<h2 style='color:#1E3A8A;'>📝 Patient Registration & Diagnostic Billing</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("Patient Full Name *").upper()
        p_phone = st.text_input("Mobile / Phone Number *")
        p_age = st.number_input("Age (Years)", min_value=1, value=25)
    with col2:
        p_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        referred_by = st.text_input("Referred By (Doctor Name)").upper()
        if not referred_by: referred_by = "SELF"
        
    st.write("---")
    st.subheader("Test Selection & Rates")
    test_catalog = {"CBC": 400.0, "RBS": 150.0, "Lipid Profile": 1000.0, "USG": 800.0, "X-Ray": 500.0}
    selected_base = st.multiselect("Select Tests from Catalog:", list(test_catalog.keys()))
    subtotal = sum([test_catalog[t] for t in selected_base])
    
    st.markdown("#### ➕ Add Custom Extra Test (Optional)")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        custom_name = st.text_input("Custom Test Name:")
    with c_col2:
        custom_rate = st.number_input("Custom Test Rate (TK):", min_value=0.0, value=0.0)
    if custom_name and custom_rate > 0:
        subtotal += custom_rate
        selected_base.append(f"{custom_name}")
        test_catalog[custom_name] = custom_rate
        
    st.write("---")
    st.subheader("Billing Settlement")
    col3, col4 = st.columns(2)
    with col3:
        discount = st.number_input("Discount Allowed (TK):", min_value=0.0, value=0.0)
        paid_amount = st.number_input("Advance Paid (TK):", min_value=0.0, value=0.0)
    with col4:
        total_payable = subtotal - discount
        due_amount = total_payable - paid_amount
        if due_amount < 0: due_amount = 0.0
        st.markdown(f"### **Net Payable:** {total_payable:,.2f} TK")
        st.markdown(f"### **Due Outstanding:** <span style='color:red;'>{due_amount:,.2f} TK</span>", unsafe_allow_html=True)

    if st.button("Save Bill and Generate Receipt"):
        if p_name and p_phone and selected_base:
            test_str = ", ".join(selected_base)
            c.execute('''
                INSERT INTO billing (patient_name, age, gender, phone, referred_by, test_names, total_bill, discount, paid_amount, due_amount, date, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (p_name, p_age, p_gender, p_phone, referred_by, test_str, total_payable, discount, paid_amount, due_amount, current_date, current_year))
            conn.commit()
            
            st.session_state.inv_id = c.lastrowid
            st.session_state.p_data = {"name": p_name, "phone": p_phone, "age": p_age, "gender": p_gender, "ref": referred_by, "tests": selected_base, "subtotal": subtotal, "discount": discount, "paid": paid_amount, "due": due_amount, "date": current_date}
            st.session_state.receipt_triggered = True
            st.success("🎉 Bill saved to lifetime database successfully!")
            st.rerun()
        else:
            st.error("⚠️ Validation Error: Please fill Name, Phone, and select at least one Test.")

    # --- A4 PRINT ENGINE ---
    if st.session_state.receipt_triggered:
        st.write("---")
        st.subheader("🖨️ A4 Document Preview")
        d = st.session_state.p_data
        
        a4_html = f"""
        <div class="printable-section">
            <div class="a4-receipt">
                <div class="invoice-title">DR. JASHIM MUKUL HOSPITAL & DIAGNOSTIC CENTRE</div>
                <div class="invoice-subtitle">Hospital ERP Management System | Patient Copy</div>
                <hr>
                <table class="info-table" style="font-size:14px; line-height:2;">
                    <tr><td><b>Invoice No:</b> #JM-{st.session_state.inv_id}</td><td><b>Date:</b> {d['date']}</td></tr>
                    <tr><td><b>Patient Name:</b> {d['name']}</td><td><b>Age/Gender:</b> {d['age']} Yrs / {d['gender']}</td></tr>
                    <tr><td><b>Mobile No:</b> {d['phone']}</td><td><b>Referred By:</b> {d['ref']}</td></tr>
                </table>
                <br>
                <table class="item-table">
                    <thead><tr><th>SL</th><th>Investigation / Test Name</th><th style='text-align:right;'>Price (TK)</th></tr></thead>
                    <tbody>
        """
        for i, t in enumerate(d['tests'], 1):
            price = test_catalog.get(t, 0.0)
            a4_html += f"<tr><td>{i}</td><td>{t}</td><td style='text-align:right;'>{price:,.2f}</td></tr>"
            
        a4_html += f"""
                    </tbody>
                </table>
                <div class="total-section">
                    <table style="width:100%;">
                        <tr><td>Subtotal:</td><td style="text-align:right;">{d['subtotal']:,.2f} TK</td></tr>
                        <tr><td>Discount:</td><td style="text-align:right;">{d['discount']:,.2f} TK</td></tr>
                        <tr style="font-weight:bold; border-top:1px solid #000;"><td>Net Payable:</td><td style="text-align:right;">{d['subtotal']-d['discount']:,.2f} TK</td></tr>
                        <tr style="font-weight:bold; color:green;"><td>Paid Amount:</td><td style="text-align:right;">{d['paid']:,.2f} TK</td></tr>
                        <tr style="font-weight:bold; color:red;"><td>Due Outstanding:</td><td style="text-align:right;">{d['due']:,.2f} TK</td></tr>
                    </table>
                </div>
                <div style="clear:both; margin-top:150px; text-align:center; font-size:12px; color:#6B7280;">
                    <hr style='border-top: 1px dotted #ccc;'>
                    Thank you for choosing Dr. Jashim Mukul Hospital. System Powered by ERP Client.
                </div>
            </div>
        </div>
        """
        st.markdown(a4_html, unsafe_allow_html=True)
        if st.button("🖨️ Print A4 Receipt Now", class_name="no-print"):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

# --- MODULE 2: PATIENT ADMISSION ---
elif choice == "🏥 Patient Admission":
