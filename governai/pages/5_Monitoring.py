import streamlit as st
import pandas as pd
from database.db import SessionLocal
from services.ai_system_svc import get_systems
from services.monitoring_svc import DEFAULT_THRESHOLDS, ingest_metric, get_metrics
from services.audit_svc import get_audit_logs

st.set_page_config(page_title="Monitoring", page_icon="📈", layout="wide")

st.title("📈 System Monitoring & Alerts")

db = SessionLocal()
current_user = st.session_state.get("current_user", "Admin")

systems = get_systems(db)

if not systems:
    st.warning("No systems found.")
else:
    system_names = {sys.id: sys.name for sys in systems}
    selected_sys_id = st.selectbox("Select AI System", options=list(system_names.keys()), format_func=lambda x: system_names[x])
    
    selected_sys = next(s for s in systems if s.id == selected_sys_id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Simulate Metric Ingestion")
        st.info("Use this simulation tool to demonstrate how threshold breaches trigger the Golden Thread (automated status degradation and audit logging).")
        
        with st.form("metric_ingestion_form"):
            metric_to_sim = st.selectbox("Select Metric", list(DEFAULT_THRESHOLDS.keys()))
            sim_value = st.number_input("Metric Value", min_value=0.0, value=0.0, step=0.01)
            
            st.write(f"*(Threshold for {metric_to_sim} is {DEFAULT_THRESHOLDS[metric_to_sim]})*")
            
            if st.form_submit_button("Ingest Metric"):
                ingest_metric(db, selected_sys_id, metric_to_sim, sim_value, current_user)
                st.success(f"Ingested {metric_to_sim}: {sim_value}")
                st.rerun()

        st.subheader("Metric History")
        metrics = get_metrics(db, selected_sys_id)
        if metrics:
            metric_data = []
            for m in metrics:
                metric_data.append({
                    "Timestamp": m.timestamp,
                    "Metric": m.metric_name,
                    "Value": m.metric_value,
                    "Threshold": m.threshold_value,
                    "Breached": "Yes" if m.is_breached else "No"
                })
            df = pd.DataFrame(metric_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No metrics recorded yet.")

    with col2:
        st.subheader("Live Status")
        if selected_sys.compliance_status == "Compliant":
            st.success("Status: Compliant")
        elif selected_sys.compliance_status == "Non-Compliant":
            st.error("Status: Non-Compliant")
        elif selected_sys.compliance_status == "At Risk":
            st.warning("Status: At Risk")
        else:
            st.info("Status: Pending")

        st.subheader("Audit Trail")
        logs = get_audit_logs(db, selected_sys_id)
        if logs:
            for log in logs[:10]: # show last 10
                with st.expander(f"**{log.action}** - {log.timestamp.split('T')[0]}"):
                    st.write(f"**User:** {log.user}")
                    st.json(log.details)
        else:
            st.write("No audit logs.")

db.close()
