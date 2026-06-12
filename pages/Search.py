# pages/Search.py
import streamlit as st
import pandas as pd
import sqlite3

conn = sqlite3.connect('dr_jashim_hospital_erp.db', check_same_thread=False)
c = conn.cursor()

st.markdown("<h2 style='color:#1E3A8A;'>🔍 Central Invoice Lookup & Reports</h2>", unsafe_allow_html=True)

search_phone = st.text_input("Enter Patient Mobile Number to Search Across ERP:")
if search_phone:
    df_search = pd.read_sql_query(f"SELECT * FROM billing WHERE phone='{search_phone}'", conn)
    
    if not df_search.empty:
        st.write("### 📋 Matching Transactions Found:")
        for index, row in df_search.iterrows():
            st.write(f"**Invoice ID:** #INV-{row['id']} | **Patient Name:** {row['patient_name']} | **Date:** {row['date']}")
            st.write(f"Tests Taken: {row['test_names']}")
            st.write(f"Total Bill: {row['total_bill']} TK | Received: {row['paid_amount']} TK | **Remaining Due: {row['due_amount']} TK**")
            
            if row['due_amount'] > 0:
                new_pay = st.number_input(f"Collect Due for Invoice #{row['id']} (TK):", min_value=0.0, max_value=float(row['due_amount']), key=f"due_{row['id']}")
                if st.button(f"Update Payment for #{row['id']}", key=f"btn_{row['id']}"):
                    updated_paid = row['paid_amount'] + new_pay
                    updated_due = row['due_amount'] - new_pay
                    c.execute(f"UPDATE billing SET paid_amount={updated_paid}, due_amount={updated_due} WHERE id={row['id']}")
                    conn.commit()
                    st.success(f"✅ Payment updated! New Due Balance: {updated_due} TK")
                    st.rerun()
            st.write("---")
    else:
        st.error("❌ No diagnostic record discovered under this phone number.")

