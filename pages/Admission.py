# pages/Admission.py
import streamlit as st
import pandas as pd

def show_admission_page(c, conn, current_date):
    st.markdown("<h2 style='color:#1E3A8A;'>🏥 Indoor Patient Admission & Release Management</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🛌 Admit New Patient (রোগী ভর্তি)", "🚪 Discharge/Release Patient (রোগী রিলিজ)"])
    
    with tab1:
        st.subheader("Patient Admission Form")
        col1, col2 = st.columns(2)
        with col1:
            adm_name = st.text_input("Patient Full Name *", key="adm_n").upper()
            adm_phone = st.text_input("Mobile Number *", key="adm_p")
            adm_age = st.number_input("Age", min_value=1, value=30, key="adm_a")
        with col2:
            adm_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="adm_g")
            bed_no = st.text_input("Cabin / Bed / Ward No *", key="adm_b").upper()
            doc_charge = st.text_input("Doctor In-Charge *", key="adm_d").upper()
            
        if st.button("Confirm Admission & Allocate Bed"):
            if adm_name and adm_phone and bed_no:
                c.execute('''
                    INSERT INTO admissions (p_name, age, gender, phone, bed_no, doctor_in_charge, admission_date, status, total_hospital_bill, paid_at_discharge)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'ADMITTED', 0.0, 0.0)
                ''', (adm_name, adm_age, adm_gender, adm_phone, bed_no, doc_charge, current_date))
                conn.commit()
                st.success(f"🎉 Patient {adm_name} successfully admitted to Cabin/Bed {bed_no}!")
            else:
                st.error("⚠️ Please fill all required (*) fields.")
                
    with tab2:
        st.subheader("Active Admitted Patients List")
        df_active = pd.read_sql_query("SELECT id, p_name, bed_no, phone, admission_date FROM admissions WHERE status='ADMITTED'", conn)
        
        if not df_active.empty:
            st.dataframe(df_active, use_container_width=True)
            
            st.write("---")
            st.subheader("Process Discharge & Billing")
            p_id = st.number_input("Enter Patient ID to Release:", min_value=1, step=1)
            
            # Fetch chosen patient details
            p_details = pd.read_sql_query(f"SELECT * FROM admissions WHERE id={p_id} AND status='ADMITTED'", conn)
            if not p_details.empty:
                st.info(f"📋 Releasing Patient: {p_details['p_name'].values[0]} | Cabin: {p_details['bed_no'].values[0]}")
                
                col3, col4 = st.columns(2)
                with col3:
                    total_h_bill = st.number_input("Total Hospital & Cabin Bill (TK):", min_value=0.0)
                with col4:
                    paid_at_release = st.number_input("Amount Received (TK):", min_value=0.0)
                    
                if st.button("Approve Release & Print Discharge Bill"):
                    c.execute(f'''
                        UPDATE admissions 
                        SET status='RELEASED', discharge_date='{current_date}', 
                            total_hospital_bill={total_h_bill}, paid_at_discharge={paid_at_release} 
                        WHERE id={p_id}
                    ''')
                    conn.commit()
                    st.success(f"✅ Patient successfully released! Hospital accounts updated.")
                    st.rerun()
            else:
                st.warning("No active admitted patient found with this ID.")
        else:
            st.info("🛌 No patients are currently admitted in cabins or wards.")
                  
