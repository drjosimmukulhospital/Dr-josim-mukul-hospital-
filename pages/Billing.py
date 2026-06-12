# pages/1_Billing.py
import streamlit as st
from datetime import datetime

def show_billing_page(c, conn, test_catalog, current_date, current_month, current_year):
    st.markdown("<h1 style='text-align:center; color:#1E3A8A;'>📝 Patient Registration & Lab Billing</h1>", unsafe_allow_html=True)
    
    st.subheader("Patient Information")
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
    st.subheader("Test Selection and Live Rate Entry")
    
    selected_tests = st.multiselect("Select Requested Tests:", list(test_catalog.keys()))
    subtotal = sum([test_catalog[test] for test in selected_tests])
    st.info(f"📋 **Total Test Fee (Subtotal):** {subtotal:,.2f} TK")
    
    st.write("---")
    st.subheader("Payment & Settlement")
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

    if 'show_receipt' not in st.session_state:
        st.session_state.show_receipt = False

    if st.button("Save Transaction & Generate Invoice"):
        if p_name and p_phone and selected_tests:
            test_str = ", ".join(selected_tests)
            c.execute('''
                INSERT INTO billing (patient_name, age, gender, phone, referred_by, test_names, total_bill, discount, paid_amount, due_amount, date, month, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (p_name, p_age, p_gender, p_phone, referred_by, test_str, total_payable, discount, paid_amount, due_amount, current_date, current_month, current_year))
            conn.commit()
            
            st.session_state.invoice_id = c.lastrowid
            st.session_state.receipt_data = {
                "name": p_name, "phone": p_phone, "age": p_age, "gender": p_gender,
                "ref": referred_by, "tests": selected_tests, "subtotal": subtotal,
                "discount": discount, "paid": paid_amount, "due": due_amount, "date": current_date
            }
            st.session_state.show_receipt = True
            st.success(f"🎉 Bill saved successfully! Permanent Database Record Created.")
            st.rerun()
        else:
            st.error("⚠️ Validation Error: Please fill Name, Phone, and select at least one Test.")

    if st.session_state.show_receipt:
        st.write("---")
        st.subheader("🖨️ Patient Money Receipt")
        r = st.session_state.receipt_data
        inv_id = st.session_state.invoice_id
        
        receipt_html = f"""
        <div class="printable-area">
            <div class="receipt-container">
                <div class="receipt-header">
                    <h2>DR. JASHIM MUKUL HOSPITAL</h2>
                    <p>Diagnostic & Hospital Management System</p>
                    <p>Date: {r['date']}</p>
                </div>
                <div class="receipt-divider"></div>
                <div class="receipt-body">
                    <p><b>Invoice No:</b> #INV-{inv_id}</p>
                    <p><b>Patient Name:</b> {r['name']}</p>
                    <p><b>Phone:</b> {r['phone']}</p>
                    <div class="receipt-divider"></div>
                    <p><b>Selected Tests:</b></p>
        """
        for t in r['tests']:
            receipt_html += f"<p style='margin-left:15px;'>- {t}</p>"
        receipt_html += f"""
                    <div class="receipt-divider"></div>
                    <table style="width:100%; font-size:13px;">
                        <tr><td>Subtotal:</td><td style="text-align:right;">{r['subtotal']:.2f} TK</td></tr>
                        <tr><td>Discount:</td><td style="text-align:right;">{r['discount']:.2f} TK</td></tr>
                        <tr style="font-weight:bold;"><td>Net Payable:</td><td style="text-align:right;">{r['subtotal']-r['discount']:.2f} TK</td></tr>
                        <tr style="font-weight:bold; color:green;"><td>Paid Amount:</td><td style="text-align:right;">{r['paid']:.2f} TK</td></tr>
                        <tr style="font-weight:bold; color:red;"><td>Due Amount:</td><td style="text-align:right;">{r['due']:.2f} TK</td></tr>
                    </table>
                </div>
                <div class="receipt-divider"></div>
                <div class="receipt-footer"><p>Thank you.</p></div>
            </div>
        </div>
        """
        st.markdown(receipt_html, unsafe_allow_html=True)
        if st.button("🖨️ Click to Print Receipt"):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
