import streamlit as st
from database.db import SessionLocal
from services.ai_system_svc import get_systems

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Portfolio Dashboard")

# Initialize database session
db = SessionLocal()
systems = get_systems(db)

# Dashboard metrics
total_systems = len(systems)
compliant = sum(1 for s in systems if s.compliance_status == "Compliant")
non_compliant = sum(1 for s in systems if s.compliance_status == "Non-Compliant")
at_risk = sum(1 for s in systems if s.compliance_status == "At Risk")
pending = sum(1 for s in systems if s.compliance_status == "Pending")

# Display metrics in columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total AI Systems", total_systems)
col2.metric("Compliant", compliant)
col3.metric("At Risk", at_risk)
col4.metric("Non-Compliant", non_compliant)

st.markdown("---")
st.subheader("System Overview")

if systems:
    # Prepare data for table
    table_data = []
    for sys in systems:
        table_data.append({
            "Name": sys.name,
            "Owner": sys.owner,
            "Risk Tier": sys.risk_tier,
            "Compliance Status": sys.compliance_status,
            "Model Type": sys.model_type
        })
    st.table(table_data)
else:
    st.info("No AI systems found. Please add a system in the Inventory.")

db.close()
