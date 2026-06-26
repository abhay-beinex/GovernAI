import streamlit as st
from database.db import SessionLocal
from services.ai_system_svc import get_systems, create_system
import os
import base64
from reports.report_gen import generate_pdf_report

st.set_page_config(page_title="Inventory", page_icon="📝", layout="wide")

st.title("📝 AI System Inventory")

db = SessionLocal()
current_user = st.session_state.get("current_user", "Admin")

tab1, tab2 = st.tabs(["View Systems", "Add New System"])

with tab1:
    st.subheader("Registered AI Systems")
    systems = get_systems(db)
    if systems:
        for sys in systems:
            with st.expander(f"**{sys.name}** (Owner: {sys.owner})"):
                st.write(f"**Business Purpose:** {sys.business_purpose}")
                st.write(f"**Model Vendor:** {sys.model_vendor}")
                st.write(f"**Model Type:** {sys.model_type}")
                st.write(f"**Model Source:** {sys.model_source}")
                st.write(f"**Risk Tier:** {sys.risk_tier}")
                st.write(f"**Compliance Status:** {sys.compliance_status}")
                
                # Export Report Button
                if st.button("Export Audit Report (PDF)", key=f"export_{sys.id}"):
                    try:
                        report_path = f"report_{sys.id}.pdf"
                        generate_pdf_report(sys.id, report_path)
                        
                        with open(report_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name=f"GovernAI_Audit_{sys.name}.pdf",
                            mime="application/pdf"
                        )
                        os.remove(report_path) # Cleanup
                    except Exception as e:
                        st.error(f"Failed to generate report: {e}")
    else:
        st.info("No AI systems registered yet.")

with tab2:
    st.subheader("Register New AI System")
    with st.form("new_system_form"):
        name = st.text_input("System Name")
        owner = st.text_input("Owner (Department/Person)")
        business_purpose = st.text_area("Business Purpose")
        model_vendor = st.text_input("Model Vendor (e.g., OpenAI, Anthropic, In-house)")
        
        col1, col2 = st.columns(2)
        with col1:
            model_type = st.selectbox("Model Type", ["LLM", "Classical ML", "Computer Vision", "Agentic AI"])
        with col2:
            model_source = st.selectbox("Model Source", ["Proprietary", "Open Source"])
            
        agentic_trace_required = st.radio("Is Agentic Trace Required?", ["Yes", "No"], index=1)
        
        submit_button = st.form_submit_button("Register System")
        
        if submit_button:
            if name and owner:
                system_data = {
                    "name": name,
                    "owner": owner,
                    "business_purpose": business_purpose,
                    "model_vendor": model_vendor,
                    "model_type": model_type,
                    "model_source": model_source,
                    "agentic_trace_required": agentic_trace_required
                }
                create_system(db, system_data, current_user)
                st.success(f"System '{name}' registered successfully!")
                st.rerun()
            else:
                st.error("Name and Owner are required fields.")

db.close()
