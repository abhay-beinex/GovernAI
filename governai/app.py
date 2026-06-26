import streamlit as st

st.set_page_config(
    page_title="GovernAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🛡️ GovernAI: AI Governance Platform")

st.markdown("""
Welcome to **GovernAI**. This is your centralized portal for managing AI systems, 
assessing risk against the EU AI Act, mapping compliance controls, and monitoring 
operational safety in real-time.

Please use the navigation menu on the left to explore the platform:
- **Dashboard**: High-level portfolio view.
- **Inventory**: Central registry of all AI systems.
- **Risk Setup**: Questionnaire for EU AI Act risk tiers.
- **Compliance**: Checklists and framework mappings.
- **Monitoring**: Real-time metrics and alerts.
""")

# Sidebar Role Selector
st.sidebar.title("Simulation Identity")
role = st.sidebar.selectbox(
    "Current User:",
    ["Admin", "Compliance Officer", "Engineer"]
)

st.session_state["current_user"] = role

st.sidebar.markdown(f"**Logged in as:** {role}")
st.sidebar.info("This lightweight role selector drives the audit log trail to demonstrate realistic governance workflows.")
