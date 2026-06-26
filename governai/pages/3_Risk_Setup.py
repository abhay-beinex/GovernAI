import streamlit as st
from database.db import SessionLocal
from services.ai_system_svc import get_systems
from services.risk_svc import RISK_QUESTIONS, assess_risk

st.set_page_config(page_title="Risk Setup", page_icon="⚖️", layout="wide")

st.title("⚖️ Risk Classification Setup")

db = SessionLocal()
current_user = st.session_state.get("current_user", "Admin")

systems = get_systems(db)
if not systems:
    st.warning("No systems found. Please add a system in the Inventory first.")
else:
    # Select a system to assess
    system_names = {sys.id: sys.name for sys in systems}
    selected_sys_id = st.selectbox("Select AI System", options=list(system_names.keys()), format_func=lambda x: system_names[x])
    
    selected_sys = next(s for s in systems if s.id == selected_sys_id)
    
    st.subheader(f"Assess Risk for: {selected_sys.name}")
    st.write(f"**Current Risk Tier:** {selected_sys.risk_tier}")
    
    with st.form("risk_assessment_form"):
        st.write("Please answer the following questions based on EU AI Act criteria:")
        
        answers = {}
        for q in RISK_QUESTIONS:
            answers[q["key"]] = st.radio(q["text"], q["options"], key=q["key"])
            
        submitted = st.form_submit_button("Submit Assessment")
        
        if submitted:
            assessment = assess_risk(db, selected_sys_id, answers, current_user)
            st.success(f"Assessment completed. Assigned Tier: **{assessment.calculated_tier}**")
            st.rerun()

db.close()
