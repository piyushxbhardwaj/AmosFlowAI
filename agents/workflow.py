import os
import logging
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, START, END

# Import Agents and Services
from agents.enrich import run_enrichment_agent
from agents.contacts import run_contacts_agent
from agents.personalize import run_personalize_agent
from agents.email_agent import run_email_agent
from agents.crm_agent import run_crm_agent
from agents.followup import run_followup_agent
import database

# Configure Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AmosFlowWorkflow")

# --- Initial Outreach Graph State & Nodes ---

class GTMState(TypedDict):
    company_name: str
    website: str
    company_id: Optional[int]
    crm_id: Optional[int]
    enriched_data: Optional[Dict[str, Any]]
    contact_data: Optional[Dict[str, Any]]
    email_data: Optional[Dict[str, Any]]
    crm_status: Optional[str]
    reply_status: Optional[str]

def enrich_node(state: GTMState) -> Dict[str, Any]:
    company_name = state["company_name"]
    website = state["website"]
    company_id = state["company_id"]
    
    logger.info(f"START NODE: enrich_company for {company_name} ({website})")
    
    # Run enrichment agent
    enriched = run_enrichment_agent(company_name, website)
    
    # Update SQLite database
    database.update_company_enrichment(company_id, enriched)
    
    logger.info(f"COMPLETED NODE: enrich_company for {company_name}")
    return {"enriched_data": enriched}

def contact_node(state: GTMState) -> Dict[str, Any]:
    company_name = state["company_name"]
    website = state["website"]
    company_id = state["company_id"]
    
    logger.info(f"START NODE: find_contact for {company_name}")
    
    # Run contact agent
    contact = run_contacts_agent(company_name, website)
    
    # Save contact to SQLite
    contact_id = database.add_contact(
        company_id=company_id,
        name=contact["name"],
        role=contact["role"],
        email=contact["email"],
        linkedin=contact["linkedin"],
        confidence=contact["confidence"]
    )
    
    # Add contact ID to the state contact data
    contact["id"] = contact_id
    
    logger.info(f"COMPLETED NODE: find_contact for {company_name} -> Contact ID: {contact_id}")
    return {"contact_data": contact}

def personalize_node(state: GTMState) -> Dict[str, Any]:
    company_name = state["company_name"]
    contact_data = state["contact_data"]
    enriched_data = state["enriched_data"]
    
    logger.info(f"START NODE: personalize_email for {company_name} targeting {contact_data['name']}")
    
    # Run personalization agent
    email_draft = run_personalize_agent(
        company_name=company_name,
        contact_name=contact_data["name"],
        contact_role=contact_data["role"],
        enriched_data=enriched_data
    )
    
    logger.info(f"COMPLETED NODE: personalize_email for {company_name}")
    return {"email_data": email_draft}

def queue_node(state: GTMState) -> Dict[str, Any]:
    company_id = state["company_id"]
    contact_data = state["contact_data"]
    email_data = state["email_data"]
    enriched_data = state["enriched_data"]
    
    # Find CRM ID for this company
    conn = database.get_db_connection()
    row = conn.execute("SELECT id FROM crm WHERE company_id = ?", (company_id,)).fetchone()
    crm_id = row["id"] if row else None
    conn.close()
    
    if not crm_id:
        logger.error(f"CRM record not found for company ID {company_id}")
        return {"crm_status": "Failed"}
        
    logger.info(f"START NODE: queue_email for CRM ID {crm_id}")
    
    # Save and queue the email
    email_res = run_email_agent(
        crm_id=crm_id,
        contact_email=contact_data["email"],
        subject=email_data["subject"],
        body=email_data["body"],
        email_type="Initial"
    )
    
    # Compute lead score and sync to sheets
    lead_score = run_crm_agent(
        company_id=company_id,
        enriched_data=enriched_data,
        contact_id=contact_data["id"]
    )
    
    logger.info(f"COMPLETED NODE: queue_email for CRM ID {crm_id}. Lead score calculated: {lead_score}")
    return {"crm_status": "Emailed"}

# --- Compile Initial Outreach Graph ---
outreach_workflow = StateGraph(GTMState)
outreach_workflow.add_node("enrich_company", enrich_node)
outreach_workflow.add_node("find_contact", contact_node)
outreach_workflow.add_node("personalize_email", personalize_node)
outreach_workflow.add_node("queue_email", queue_node)

outreach_workflow.add_edge(START, "enrich_company")
outreach_workflow.add_edge("enrich_company", "find_contact")
outreach_workflow.add_edge("find_contact", "personalize_email")
outreach_workflow.add_edge("personalize_email", "queue_email")
outreach_workflow.add_edge("queue_email", END)

outreach_app = outreach_workflow.compile()


# --- Follow-up Graph State & Nodes ---

class FollowupState(TypedDict):
    crm_id: int
    company_name: str
    company_id: int
    contact_name: str
    contact_email: str
    reply_status: str
    email_data: Optional[Dict[str, Any]]
    crm_status: Optional[str]

def check_reply_node(state: FollowupState) -> Dict[str, Any]:
    crm_id = state["crm_id"]
    company_name = state["company_name"]
    
    logger.info(f"START NODE: check_reply for CRM ID {crm_id} ({company_name})")
    
    # Query current DB status
    conn = database.get_db_connection()
    row = conn.execute("SELECT reply_status FROM crm WHERE id = ?", (crm_id,)).fetchone()
    conn.close()
    
    reply_status = row["reply_status"] if row else "Waiting"
    
    logger.info(f"COMPLETED NODE: check_reply status is '{reply_status}'")
    return {"reply_status": reply_status}

def generate_followup_node(state: FollowupState) -> Dict[str, Any]:
    crm_id = state["crm_id"]
    company_name = state["company_name"]
    contact_name = state["contact_name"]
    
    logger.info(f"START NODE: generate_followup for {company_name}")
    
    # Get previous email info to context the follow-up
    conn = database.get_db_connection()
    prev_email = conn.execute(
        "SELECT subject, body FROM emails WHERE crm_id = ? AND email_type = 'Initial' ORDER BY id DESC LIMIT 1",
        (crm_id,)
    ).fetchone()
    conn.close()
    
    prev_subj = prev_email["subject"] if prev_email else "Our GTM automation pipeline"
    prev_body = prev_email["body"] if prev_email else ""
    
    # Run follow-up agent
    followup_draft = run_followup_agent(
        company_name=company_name,
        contact_name=contact_name,
        previous_subject=prev_subj,
        previous_body=prev_body
    )
    
    logger.info(f"COMPLETED NODE: generate_followup for {company_name}")
    return {"email_data": followup_draft}

def queue_followup_node(state: FollowupState) -> Dict[str, Any]:
    crm_id = state["crm_id"]
    company_id = state["company_id"]
    contact_email = state["contact_email"]
    email_data = state["email_data"]
    
    logger.info(f"START NODE: queue_followup for CRM ID {crm_id}")
    
    # Queue email draft
    run_email_agent(
        crm_id=crm_id,
        contact_email=contact_email,
        subject=email_data["subject"],
        body=email_data["body"],
        email_type="Followup"
    )
    
    # Fetch enriched data for lead score recalculation and sync
    conn = database.get_db_connection()
    comp_row = conn.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
    conn.close()
    
    enriched_data = dict(comp_row) if comp_row else {}
    
    # Trigger CRM update and sync to Google Sheets
    run_crm_agent(
        company_id=company_id,
        enriched_data=enriched_data
    )
    
    logger.info(f"COMPLETED NODE: queue_followup for CRM ID {crm_id}")
    return {"crm_status": "Follow-up Sent"}

def should_followup_router(state: FollowupState) -> str:
    """
    Decides whether to generate follow-up or end.
    """
    if state["reply_status"] == "Replied":
        return "replied"
    return "no_reply"

# --- Compile Follow-up Graph ---
followup_workflow = StateGraph(FollowupState)
followup_workflow.add_node("check_reply", check_reply_node)
followup_workflow.add_node("generate_followup", generate_followup_node)
followup_workflow.add_node("queue_followup", queue_followup_node)

followup_workflow.add_edge(START, "check_reply")
followup_workflow.add_conditional_edges(
    "check_reply",
    should_followup_router,
    {
        "replied": END,
        "no_reply": "generate_followup"
    }
)
followup_workflow.add_edge("generate_followup", "queue_followup")
followup_workflow.add_edge("queue_followup", END)

followup_app = followup_workflow.compile()


# --- Core Orchestration API ---

def execute_initial_outreach(company_name: str, website: str) -> dict:
    """
    Imports the company and executes the initial outreach LangGraph pipeline.
    """
    logger.info(f"Starting Outreach Pipeline for company: {company_name}")
    
    # 1. Register in SQLite database (idempotency check happens inside add_company)
    company_id = database.add_company(company_name, website)
    
    # 2. Setup initial state
    initial_state = {
        "company_name": company_name,
        "website": website,
        "company_id": company_id,
        "crm_id": None,
        "enriched_data": None,
        "contact_data": None,
        "email_data": None,
        "crm_status": "Imported",
        "reply_status": "Waiting"
    }
    
    # 3. Execute LangGraph
    final_state = outreach_app.invoke(initial_state)
    logger.info(f"Outreach Pipeline complete for: {company_name}. CRM Status: {final_state.get('crm_status')}")
    return final_state

def execute_followup_check() -> List[dict]:
    """
    Scans the CRM for companies requiring a follow-up.
    Generates follow-up emails for non-responsive targets.
    """
    logger.info("Starting scheduler follow-up scans...")
    crm_records = database.get_crm()
    
    triggered_followups = []
    
    for record in crm_records:
        # Check if company is at 'Emailed' stage, hasn't replied, and next followup date is past
        if record["current_stage"] == "Emailed" and record["reply_status"] == "Waiting":
            next_date_str = record["next_followup_date"]
            
            should_trigger = False
            if next_date_str:
                try:
                    next_date = datetime.fromisoformat(next_date_str)
                    if datetime.utcnow() >= next_date:
                        should_trigger = True
                except ValueError:
                    should_trigger = True
            else:
                should_trigger = True
                
            if should_trigger:
                logger.info(f"Triggering follow-up workflow for CRM ID {record['id']} ({record['company_name']})")
                
                state = {
                    "crm_id": record["id"],
                    "company_name": record["company_name"],
                    "company_id": record["company_id"],
                    "contact_name": record["contact_name"] or "Contact",
                    "contact_email": record["contact_email"] or "demo-contact@example.com",
                    "reply_status": "Waiting",
                    "email_data": None,
                    "crm_status": "Emailed"
                }
                
                final_state = followup_app.invoke(state)
                triggered_followups.append(final_state)
                
    logger.info(f"Follow-up scan completed. Triggered {len(triggered_followups)} followups.")
    return triggered_followups
