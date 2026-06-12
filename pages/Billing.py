# pages/Billing.py
import streamlit as st

def show_billing_page(c, conn, current_date, current_year):
    st.markdown("<h2 style='color:#1E3A8A;'>📝 Patient Registration & Diagnostic Billing</h2>", unsafe_allow_html=True)
    
    st.subheader("Patient Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("Patient Full Name *").upper()
        p_phone = st.text_input("Mobile / Phone Number *")
    with col2:
        p_age = st.number_input("Age (Years)", min_value=1, value=25)
        p_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        referred_by = st.text_input("Referred By (Doctor Name)").upper()
        if not referred_by: referred_by = "SELF"
        
    st.write("---")
    st.subheader("Test Selection & Live Rate Entry")
    
    # Static Catalog + Custom Test Insertion ( হুবহু আপনার স্ক্রিনশটের মডেল )
    test_catalog = {"CBC": 400.0, "RBS": 150.0, "Lipid Profile": 1000.0, "USG": 800.0, "X-Ray": 500.0}
    selected_base = st.multiselect("Select Tests from Catalog:", list(test_catalog.keys()))
    
    subtotal = sum([test_catalog[t] for t in selected_base])
    
    # ➕ স্ক্রিনশটের মতো তালিকা বহির্ভূত কাস্টম টেস্ট যোগ করার ঘর
    st.markdown("#### ➕ Add Custom Extra Test (ঐচ্ছিক)")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        custom_name = st.text_input("Custom Test Name:")
    with c_col2:
        custom_rate = st.number_input("Custom Test Rate (TK):", min_value=0.0, value=0.0)
        
    if custom_name and custom_rate > 0:
        subtotal += custom_rate
        selected_base.append(f"{custom_name}(Custom)")
        
    st.info(f"📋 **Total Combined Test Fee:** {subtotal:,.2f} TK")
    
    st.write("---")
    st.subheader("Payment & Discount Settlement")
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

    if st.button("Save Bill and Go to Print (ডাটা সেভ করুন)"):
        if p_name and p_phone and selected_base:
            test_str = ", ".join(selected_base)
            c.execute('''
                INSERT INTO billing (patient_name, age, gender, phone, referred_by, test_names, total_bill, discount, paid_amount, due_amount, date, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (p_name, p_age, p_gender, p_phone, referred_by, test_str, total_payable, discount, paid_amount, due_amount, current_date, current_year))
            conn.commit()
            st.success(f"🎉 Diagnostic Bill saved successfully for {p_name}!")
        else:
            st.error("⚠️ Validation Error: Please input Patient Name, Phone and choose a Test.")

