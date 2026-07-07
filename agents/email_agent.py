import os
import time
import random
from services.gmail_service import create_gmail_draft
import database

def run_email_agent(crm_id: int, contact_email: str, subject: str, body: str, email_type: str = "Initial") -> dict:
    """
    Queues the generated outreach email in SQLite database and creates a Gmail draft if credentials exist.
    Implements a simple rate limiter simulation to avoid API rate limits.
    """
    print(f"[Email Queue] Queueing {email_type} email for {contact_email}...")
    
    # 1. Simulate rate limiting (optional random delay of 0.2 to 1.0 seconds for PoC safety)
    delay = random.uniform(0.2, 1.0)
    time.sleep(delay)
    
    # 2. Add initial record to database as 'Queued'
    email_id = database.add_email(crm_id, subject, body, "Queued", email_type)
    
    # 3. Try to push draft to Gmail
    gmail_res = create_gmail_draft(contact_email, subject, body)
    
    status = "Queued"
    if gmail_res.get("success"):
        if gmail_res.get("draft_id"):
            status = "Draft Created"
        else:
            status = "Draft Created (Simulated)"
            
        # Update SQLite email status
        conn = database.get_db_connection()
        try:
            conn.execute("UPDATE emails SET status = ? WHERE id = ?", (status, email_id))
            conn.commit()
        finally:
            conn.close()
            
    print(f"[Email Queue] Queue action completed for {contact_email}. Status: {status}")
    return {
        "email_id": email_id,
        "status": status,
        "gmail_message": gmail_res.get("message")
    }
