import os
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="AmosFlow AI | GTM Automation Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Custom Premium Styling (Dark Mode Theme)
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sleek headers and gradients */
    .header-container {
        background: linear-gradient(135deg, #1E1B4B 0%, #311042 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #3730A3;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .tagline {
        color: #C084FC;
        font-weight: 600;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.5rem;
    }
    .title {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 2.5rem;
        margin: 0;
    }
    .subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Glassmorphic Metrics */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(192, 132, 252, 0.4);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Control Panel design */
    .control-box {
        background: #0F172A;
        border: 1px solid #1E293B;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Define API URL
API_URL = "http://127.0.0.1:8000"

# Import database module for fallback
try:
    import database
    db_available = True
except ImportError:
    db_available = False

# Helper to fetch data with API first, DB fallback
def fetch_crm_data():
    try:
        response = requests.get(f"{API_URL}/crm", timeout=2)
        if response.status_code == 200:
            return response.json(), "API"
    except Exception:
        pass
        
    if db_available:
        try:
            return database.get_crm(), "Local DB (API Offline)"
        except Exception as e:
            st.error(f"Failed to read database: {e}")
            
    return [], "No Connection"

def fetch_company_data():
    try:
        response = requests.get(f"{API_URL}/companies", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
        
    if db_available:
        return database.get_companies()
    return []

def fetch_email_data():
    try:
        response = requests.get(f"{API_URL}/emails", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
        
    if db_available:
        return database.get_emails()
    return []

def fetch_contact_data():
    try:
        response = requests.get(f"{API_URL}/contacts", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
        
    if db_available:
        return database.get_contacts()
    return []

# App Header
st.markdown("""
<div class="header-container">
    <div class="tagline">AmosFlow AI</div>
    <h1 class="title">Autonomous GTM Pipeline</h1>
    <div class="subtitle">Personalized prospecting outreach, company intelligence, and reply follow-up automations.</div>
</div>
""", unsafe_allow_html=True)

# Fetch CRM Records
crm_records, source_mode = fetch_crm_data()
companies = fetch_company_data()
emails = fetch_email_data()
contacts = fetch_contact_data()

# Status Bar
st.sidebar.markdown(f"**Backend Connection:** `{source_mode}`")

# Metrics Calculations
total_leads = len(crm_records)
emailed_leads = sum(1 for r in crm_records if r.get("current_stage") in ["Emailed", "Follow-up Sent"])
replied_leads = sum(1 for r in crm_records if r.get("reply_status") == "Replied")
avg_lead_score = 0.0
if total_leads > 0:
    scores = [r.get("lead_score") for r in crm_records if r.get("lead_score") is not None]
    if scores:
        avg_lead_score = sum(scores) / len(scores)

# Metric Columns
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_leads}</div>
        <div class="metric-label">Total Leads</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{emailed_leads}</div>
        <div class="metric-label">Outreach Emailed</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card" style="border-color: rgba(34, 197, 94, 0.4);">
        <div class="metric-value" style="color: #22C55E;">{replied_leads}</div>
        <div class="metric-label">Warm Replies</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_lead_score:.2f}</div>
        <div class="metric-label">Avg GTM Fit Score</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 CRM Pipeline", 
    "🏢 Enriched Companies", 
    "👤 Target Contacts", 
    "✉️ Outreach Queue & Logs", 
    "⚙️ Control Panel & Actions"
])

# TAB 1: CRM Pipeline
with tab1:
    st.header("Pipeline Tracking Board")
    if crm_records:
        df_crm = pd.DataFrame(crm_records)
        # Select clean columns
        df_display = df_crm[[
            "id", "company_name", "company_website", "contact_name", "contact_role", 
            "current_stage", "lead_score", "reply_status", "reply_count", "next_action"
        ]].rename(columns={
            "id": "CRM ID",
            "company_name": "Company",
            "company_website": "Website",
            "contact_name": "Contact",
            "contact_role": "Role",
            "current_stage": "Stage",
            "lead_score": "Score",
            "reply_status": "Reply",
            "reply_count": "Replies",
            "next_action": "Next Action"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("The CRM is currently empty. Run the GTM pipeline from the Control Panel to import targets.")

# TAB 2: Enriched Companies
with tab2:
    st.header("Enriched Business Intelligence")
    if companies:
        df_companies = pd.DataFrame(companies)
        
        # Display details in an expander layout or clean table
        for comp in companies:
            with st.expander(f"🏢 {comp['name']} ({comp['website']}) - Enrichment Confidence: {comp.get('enrichment_confidence', 0.0):.2f}"):
                c_col1, c_col2 = st.columns([2, 1])
                with c_col1:
                    st.markdown(f"**Business Summary:**\n{comp.get('summary')}")
                    st.markdown(f"**Core Product Offerings:**\n{comp.get('product')}")
                    st.markdown(f"**Ideal Customer Profile (ICP):**\n{comp.get('icp')}")
                with c_col2:
                    st.markdown(f"**Hiring & Growth Activity:**\n`{comp.get('hiring_status')}`")
                    st.markdown(f"**Funding Signals:**\n`{comp.get('funding')}`")
                    st.markdown(f"**AI/ML Maturity:**\n{comp.get('ai_summary')}")
                    st.caption(f"Enriched at: {comp.get('enriched_at')}")
    else:
        st.info("No company profiles enriched yet.")

# TAB 3: Target Contacts
with tab3:
    st.header("Identified Decision Makers")
    if contacts:
        df_contacts = pd.DataFrame(contacts)
        df_contacts_display = df_contacts[[
            "id", "name", "role", "email", "linkedin", "discovery_confidence"
        ]].rename(columns={
            "id": "Contact ID",
            "name": "Name",
            "role": "Role",
            "email": "Email Address",
            "linkedin": "LinkedIn URL",
            "discovery_confidence": "Discovery Confidence"
        })
        st.dataframe(df_contacts_display, use_container_width=True, hide_index=True)
    else:
        st.info("No decision makers identified yet.")

# TAB 4: Outreach Logs
with tab4:
    st.header("Generated Outreach Drafts")
    if emails:
        # Display list of emails
        for em in emails:
            with st.expander(f"✉️ {em['email_type']} email for {em['company_name']} -> {em['contact_email']} ({em['status']})"):
                st.markdown(f"**Subject:** {em['subject']}")
                st.markdown("**Body:**")
                st.code(em['body'], language='text')
                st.caption(f"Created at: {em['created_at']}")
    else:
        st.info("No email outreach drafted yet.")

# TAB 5: Control Panel
with tab5:
    st.header("Workflow Operations Center")
    
    st.markdown("<div class='control-box'>", unsafe_allow_html=True)
    st.subheader("1. Launch Bulk Outreach Campaign")
    st.write("Reads the `companies.csv` seed file, runs LangGraph to enrich each firm, locates contacts, crafts hyper-personalized cold outreach emails, and queues the drafts.")
    if st.button("🚀 Trigger GTM Outreach Pipeline", type="primary"):
        if source_mode == "API":
            try:
                res = requests.post(f"{API_URL}/run")
                if res.status_code == 200:
                    st.success("Outreach pipeline initiated in backend background tasks! Refresh page to see progress.")
                else:
                    st.error(f"Backend returned error: {res.text}")
            except Exception as e:
                st.error(f"API Request failed: {e}")
        else:
            st.warning("FastAPI backend is offline. Launch the uvicorn backend to run background pipelines.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='control-box'>", unsafe_allow_html=True)
    st.subheader("2. Simulate Prospect Reply")
    st.write("Select an active lead from the CRM pipeline to simulate them replying. This stops follow-ups and flags the lead for manual sales conversion.")
    
    # Filter crm records for Emailed/Followup Sent
    active_crm = [r for r in crm_records if r["current_stage"] in ["Emailed", "Follow-up Sent"] and r["reply_status"] == "Waiting"]
    
    if active_crm:
        crm_options = {f"{r['company_name']} ({r['contact_name']})": r["id"] for r in active_crm}
        selected_label = st.selectbox("Select Lead to Reply:", list(crm_options.keys()))
        selected_id = crm_options[selected_label]
        
        if st.button("💬 Trigger Simulated Reply"):
            if source_mode == "API":
                try:
                    res = requests.post(f"{API_URL}/simulate-reply", json={"crm_id": selected_id})
                    if res.status_code == 200:
                        st.success(f"Reply simulated successfully for CRM ID {selected_id}!")
                        st.rerun()
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"API Request failed: {e}")
            elif db_available:
                database.simulate_reply(selected_id)
                st.success(f"Reply saved directly to SQLite for CRM ID {selected_id}!")
                st.rerun()
    else:
        st.write("No emailed leads currently waiting for replies.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='control-box'>", unsafe_allow_html=True)
    st.subheader("3. Force Follow-up Scheduler Execution")
    st.write("Forces the system scheduler to check for companies whose next follow-up dates have elapsed, generating polite follow-up drafts for non-responsive contacts.")
    if st.button("⏰ Execute Follow-up Scheduler Now"):
        if source_mode == "API":
            try:
                res = requests.post(f"{API_URL}/run-scheduler")
                if res.status_code == 200:
                    st.success("Follow-up scheduler check executed! Refresh page to see new follow-up drafts.")
                    st.rerun()
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"API request failed: {e}")
        else:
            st.warning("FastAPI backend is offline. Cannot trigger scheduled tasks without backend running.")
    st.markdown("</div>", unsafe_allow_html=True)

# Add automatic refresh instruction
st.sidebar.button("🔄 Refresh Data")
st.sidebar.caption("AmosFlow AI GTM Pipeline v1.0.0")
st.sidebar.caption("Built with Python, FastAPI, LangGraph & Streamlit")
