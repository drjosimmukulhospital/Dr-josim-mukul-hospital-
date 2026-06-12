pages/2_Search.py
import streamlit as st
import pandas as pd

def show_search_page(c, conn):
    st.markdown("<h1 style='text-align:center; color:#1E3A8A;'>🔍 Due Clearance & Invoice Lookup</h1>", unsafe_allow_html=True)
    
    search_phone = st.text_input("Enter Patient Mobile Number to Search:")
    if search_phone:
        df_search = pd.read_sql_query(f"SELECT * FROM billing WHERE phone='{search_phone}'", conn)
        
        if not df_search.empty:
            st.write("### 📋 Found Records:")
            for index, row in df_search.iterrows():
                st.write(f"**Invoice ID:** {row['id']} | **Patient Name:** {row['patient_name']} | **Date:** {row['date']}")
                st.write(f"Tests: {row['test_names']}")
                st.write(f"Total: {row['total_bill']} TK | Paid: {row['paid_amount']} TK | **Due: {row['due_amount']} TK**")
                
                if row['due_amount'] > 0:
                    new_pay = st.number_input(f"Enter Amount to Collect (TK):", min_value=0.0, max_value=float(row['due_amount']), key=f"due_{row['id']}")
                    if st.button(f"Clear Due for Invoice {row['id']}", key=f"btn_{row['id']}"):
                        updated_paid = row['paid_amount'] + new_pay
                        updated_due = row['due_amount'] - new_pay
                        c.execute(f"UPDATE billing SET paid_amount={updated_paid}, due_amount={updated_due} WHERE id={row['id']}")
                        conn.commit()
                        st.success(f"✅ Successfully updated Payment! Remaining Due: {updated_due} TK")
                        st.rerun()
                else:
                    st.success("✅ This Invoice is Already Fully Paid.")
                st.write("---")
        else:
            st.error("❌ No records found for this mobile number.")
