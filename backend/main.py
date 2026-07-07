import os
import csv
import logging
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

import database
from agents.workflow import execute_initial_outreach, execute_followup_check

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AmosFlowAPI")

# Initialize database
database.init_db()

# Create Scheduler
scheduler = BackgroundScheduler()

def run_scheduled_followups():
    """
    Background job to periodically check for companies that need follow-ups.
    """
    try:
        logger.info("[Scheduler] Checking for pending follow-up drafts...")
        triggered = execute_followup_check()
        if triggered:
            logger.info(f"[Scheduler] Generated {len(triggered)} follow-up drafts.")
    except Exception as e:
        logger.error(f"[Scheduler] Error running background check: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start APScheduler
    scheduler.add_job(run_scheduled_followups, 'interval', minutes=1, id='followup_job')
    scheduler.start()
    logger.info("Background scheduler started (polling every 1 minute).")
    yield
    # Shutdown: Stop APScheduler
    scheduler.shutdown()
    logger.info("Background scheduler stopped.")

app = FastAPI(
    title="AmosFlow AI - GTM Automation Backend",
    description="Autonomous GTM pipeline orchestrating company research, contact discovery, personalization and outreach.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ReplySimulationRequest(BaseModel):
    crm_id: int

# REST Endpoints

def process_csv_pipeline():
    """
    Reads the CSV and runs outreach pipeline sequentially.
    """
    csv_path = os.path.join("data", "companies.csv")
    if not os.path.exists(csv_path):
        logger.error(f"Companies CSV not found at {csv_path}")
        return
        
    logger.info("Starting CSV bulk outreach process...")
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company = row.get("Company") or row.get("company")
                website = row.get("Website") or row.get("website")
                
                if company and website:
                    try:
                        execute_initial_outreach(company.strip(), website.strip())
                    except Exception as ex:
                        logger.error(f"Error processing outreach for {company}: {ex}")
        logger.info("Bulk CSV outreach execution finished.")
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")

@app.post("/run", summary="Trigger the GTM bulk pipeline run")
def run_pipeline(background_tasks: BackgroundTasks):
    """
    Asynchronously reads data/companies.csv and executes target enrichment,
    decision maker search, personalized copy drafting, and CRM sync.
    """
    background_tasks.add_task(process_csv_pipeline)
    return {"status": "success", "message": "GTM pipeline run initiated in the background."}

@app.get("/companies", summary="Get all enriched company intelligence")
def get_companies():
    """
    Returns the list of enriched company records.
    """
    try:
        return database.get_companies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails", summary="Get all drafted and queued outreach emails")
def get_emails():
    """
    Returns all outreach initial and follow-up drafts from the queue.
    """
    try:
        return database.get_emails()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crm", summary="Get CRM spreadsheet records")
def get_crm():
    """
    Returns the expanded CRM dashboard contents.
    """
    try:
        return database.get_crm()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulate-reply", summary="Simulate a prospect replying")
def trigger_reply(request: ReplySimulationRequest):
    """
    Marks a company record as Replied to test scheduling and stopping criteria.
    """
    try:
        # Check if CRM ID exists
        conn = database.get_db_connection()
        row = conn.execute("SELECT id FROM crm WHERE id = ?", (request.crm_id,)).fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"CRM record {request.crm_id} not found.")
            
        database.simulate_reply(request.crm_id)
        return {"status": "success", "message": f"CRM ID {request.crm_id} reply simulated."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-scheduler", summary="Force run follow-up checks immediately")
def force_scheduler():
    """
    Forces checking the CRM for non-responding leads and drafts follow-ups.
    """
    try:
        logger.info("Forced follow-up check triggered via API.")
        triggered = execute_followup_check()
        return {
            "status": "success", 
            "message": f"Follow-up check execution finished.",
            "triggered_count": len(triggered)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Read port from env or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
