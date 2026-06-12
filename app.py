import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ১. ডাটাবেজ সেটআপ (যা বছরের পর বছর হিসাব ধরে রাখবে)
conn = sqlite3.connect('hospital_management.db', check_same_thread=False)
c = conn.cursor()

# টেবিল তৈরি (যদি আগে থেকে না থাকে)
c.execute('''
    CREATE TABLE IF NOT EXISTS billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        age INTEGER,
        phone TEXT,
        referred_by TEXT,
        test_names TEXT,
        total_bill REAL,
        discount REAL,
        paid REAL,
        due REAL,
        date TEXT,
        year TEXT
    )
''')
conn.commit()

# পেজ কনফিগারেশন ও ডিজাইন
st.set_page_config(page_title="ডাঃ জসিম মুকুল হসপিটাল", layout="wide")

# সিএসএস দিয়ে ডিজাইন সুন্দর করা
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 20px; }
    .sidebar-title { font-size: 18px; font-weight: bold; color: #10B981; }
    </style>
""", unsafe_allow_html=True)

# --- সাইডবার বা বাম পাশের মেনু ---
st.sidebar.markdown("<h2 class='sidebar-title'>ডাঃ জসিম মুকুল হসপিটাল</h2>", unsafe_allow_html=True)
st.sidebar.info(f"📅 তারিখ: {datetime.now().strftime('%d %B, %Y')}")

menu = [
    "📝 Patient Entry & Billing", 
    "💰 Money Receipt & Reports", 
    "🔍 Due Collection", 
    "📊 Yearly Archive (আজীবন হিসাব)"
]
choice = st.sidebar.radio("প্রধান কার্যভার (Main)", menu)

# আজকের লাইভ হিসাবের সংক্ষিপ্ত রূপ সাইডবারে দেখানো
current_year = datetime.now().strftime('%Y')
current_date = datetime.now().strftime('%Y-%m-%d')

df_today = pd.read_sql_query(f"SELECT * FROM billing WHERE date='{current_date}'", conn)
today_total = df_today['paid'].sum() if not df_today.empty else 0
today_due = df_today['due'].sum() if not df_today.empty else 0

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 আজকের লাইভ হিসাব")
st.sidebar.metric("মোট কালেকশন (টাকা)", f"{today_total} ৳")
st.sidebar.metric("মোট বাকি (Due)", f"{today_due} ৳")

# --- মূল সেকশন (ডান পাশ) ---

# ১ নম্বর মডিউল: পেশেন্ট এন্ট্রি ও বিলিং
if choice == "📝 Patient Entry & Billing":
    st.markdown("<h1 class='main-title'>📝 টেস্ট এবং বিলিং সেকশন</h1>", unsafe_allow_html=True)
    
    st.subheader("পেশেন্ট ইনফরমেশন")
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
        p_phone = st.text_input("মোবাইল নম্বর (Phone) *")
    with col2:
        p_age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)
        referred_by = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", ["ডাঃ সাইদুল ইসলাম", "ডাঃ জসিম মুকুল", "অন্যান্য"])
        
    st.write("---")
    st.subheader("টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি")
    tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", ["CBC (400 ৳)", "RBS (150 ৳)", "Lipid Profile (1000 ৳)", "Ultrasonography (800 ৳)", "X-Ray (500 ৳)"])
    
    # টেস্টের মূল্য নির্ধারণ
    test_rates = {"CBC (400 ৳)": 400, "RBS (150 ৳)": 150, "Lipid Profile (1000 ৳)": 1000, "Ultrasonography (800 ৳)": 800, "X-Ray (500 ৳)": 500}
    subtotal = sum([test_rates[t] for t in tests])
    
    st.info(f"📋 সাইট রেট বিল (টোটাল টেস্ট ফি): {subtotal} টাকা")
    
    st.write("---")
    st.subheader("পেমেন্ট ও ডিসকাউন্ট")
    col3, col4 = col3, col4 = st.columns(2)
    with col3:
        discount = st.number_input("ডিসকাউন্ট প্রদেয় (টাকা)", min_value=0.0, value=0.0)
        advance_paid = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0.0, value=0.0)
    with col4:
        total_payable = subtotal - discount
        due_amount = total_payable - advance_paid
        if due_amount < 0: due_amount = 0.0
        
        st.write(f"**মোট প্রদেয় টাকা:** {total_payable} ৳")
        st.write(f"**মোট বাকি টাকা (Due):** {due_amount} ৳")

    if st.button("Save Bill and Go to Print (ডাটা সেভ করুন)"):
        if p_name and p_phone and tests:
            test_str = ", ".join(tests)
            c.execute('''
                INSERT INTO billing (patient_name, age, phone, referred_by, test_names, total_bill, discount, paid, due, date, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (p_name, p_age, p_phone, referred_by, test_str, total_payable, discount, advance_paid, due_amount, current_date, current_year))
            conn.commit()
            st.success("🎉 বিলটি ডাটাবেজে আজীবনের জন্য সফলভাবে সেভ হয়েছে!")
        else:
            st.error("⚠️ দয়া করে নাম, মোবাইল নম্বর এবং অন্তত একটি টেস্ট সিলেক্ট করুন।")

# ৪ নম্বর মডিউল: বছরের পর বছর হিসাব রাখার আর্কাইভ
elif choice == "📊 Yearly Archive (আজীবন হিসাব)":
    st.markdown("<h1 class='main-title'>📊 আজীবন হিসাব ও আর্কাইভ সেকশন</h1>", unsafe_allow_html=True)
    st.write("এখানে কোনো নির্বাচন ছাড়াই বছরের পর বছর আপনার সমস্ত ডেটা সংরক্ষিত থাকবে।")
    
    # ডাটাবেজ থেকে উপলব্ধ সমস্ত বছরের তালিকা নেওয়া
    years_df = pd.read_sql_query("SELECT DISTINCT year FROM billing", conn)
    if not years_df.empty:
        available_years = years_df['year'].tolist()
        selected_year = st.selectbox("কোন বছরের হিসাব দেখতে চান সিলেক্ট করুন:", available_years)
        
        # নির্দিষ্ট বছরের ডেটা দেখানো
        df_year = pd.read_sql_query(f"SELECT * FROM billing WHERE year='{selected_year}'", conn)
        
        st.write(f"### 📅 {selected_year} সালের মোট রিপোর্ট:")
        st.dataframe(df_year)
        
        # মোট হিসাবের সামারি
        st.markdown(f"""
        * **ঐ বছরের মোট রোগী সংখ্যা:** {len(df_year)} জন
        * **ঐ বছরের মোট অর্জিত ক্যাশ:** {df_year['paid'].sum()} ৳
        * **ঐ বছরের মোট বকেয়া (Due):** {df_year['due'].sum()} ৳
        """)
    else:
        st.warning("এখনো ডাটাবেজে কোনো দীর্ঘমেয়াদী হিসাব জমা হয়নি।")
