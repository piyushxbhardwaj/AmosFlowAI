import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "gtm_crm.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Companies Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        website TEXT NOT NULL UNIQUE,
        summary TEXT,
        product TEXT,
        icp TEXT,
        recent_news TEXT,
        hiring_status TEXT,
        funding TEXT,
        website_title TEXT,
        ai_summary TEXT,
        enrichment_confidence REAL,
        enriched_at TEXT
    );
    """)

    # 2. Contacts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT,
        role TEXT,
        email TEXT,
        linkedin TEXT,
        discovery_confidence REAL,
        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
    );
    """)

    # 3. CRM Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL UNIQUE,
        contact_id INTEGER,
        current_stage TEXT NOT NULL, -- 'Imported', 'Enriched', 'Contact Found', 'Emailed', 'Replied', 'Follow-up Sent', 'No Reply'
        lead_score REAL,
        industry TEXT,
        last_activity TEXT,
        last_contact_date TEXT,
        next_action TEXT,
        reply_count INTEGER DEFAULT 0,
        reply_status TEXT DEFAULT 'Waiting', -- 'Waiting', 'Replied'
        next_followup_date TEXT,
        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
        FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE SET NULL
    );
    """)

    # 4. Emails Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crm_id INTEGER NOT NULL,
        subject TEXT,
        body TEXT,
        status TEXT NOT NULL, -- 'Queued', 'Sent', 'Draft Created'
        email_type TEXT NOT NULL, -- 'Initial', 'Followup'
        created_at TEXT,
        FOREIGN KEY(crm_id) REFERENCES crm(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# CRUD Helpers

def add_company(name: str, website: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clean up website URL structure
    website = website.strip().lower()
    
    try:
        cursor.execute("SELECT id FROM companies WHERE website = ?", (website,))
        row = cursor.fetchone()
        if row:
            company_id = row['id']
            # Update name if it changed
            cursor.execute("UPDATE companies SET name = ? WHERE id = ?", (name, company_id))
            conn.commit()
            return company_id
        
        cursor.execute("INSERT INTO companies (name, website) VALUES (?, ?)", (name, website))
        conn.commit()
        company_id = cursor.lastrowid
        
        # Also auto-initialize in CRM table
        cursor.execute(
            "INSERT OR IGNORE INTO crm (company_id, current_stage, reply_status, reply_count) VALUES (?, ?, ?, ?)",
            (company_id, "Imported", "Waiting", 0)
        )
        conn.commit()
        return company_id
    finally:
        conn.close()

def update_company_enrichment(company_id: int, data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE companies 
            SET summary = ?, 
                product = ?, 
                icp = ?, 
                recent_news = ?, 
                hiring_status = ?, 
                funding = ?, 
                website_title = ?, 
                ai_summary = ?, 
                enrichment_confidence = ?,
                enriched_at = ?
            WHERE id = ?
        """, (
            data.get("company_summary"),
            data.get("product"),
            data.get("icp_fit"),
            data.get("recent_news"),
            data.get("hiring_insights"),
            data.get("funding_signals"),
            data.get("website_title"),
            data.get("ai_summary"),
            data.get("enrichment_confidence", 0.0),
            datetime.utcnow().isoformat(),
            company_id
        ))
        
        # Update CRM stage
        cursor.execute("""
            UPDATE crm 
            SET current_stage = 'Enriched',
                last_activity = 'Company enriched with business information',
                next_action = 'Find decision maker contact'
            WHERE company_id = ?
        """, (company_id,))
        
        conn.commit()
    finally:
        conn.close()

def add_contact(company_id: int, name: str, role: str, email: str, linkedin: str, confidence: float) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if contact already exists for company
        cursor.execute("SELECT id FROM contacts WHERE company_id = ?", (company_id,))
        row = cursor.fetchone()
        if row:
            contact_id = row['id']
            cursor.execute("""
                UPDATE contacts 
                SET name = ?, role = ?, email = ?, linkedin = ?, discovery_confidence = ?
                WHERE id = ?
            """, (name, role, email, linkedin, confidence, contact_id))
        else:
            cursor.execute("""
                INSERT INTO contacts (company_id, name, role, email, linkedin, discovery_confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, name, role, email, linkedin, confidence))
            contact_id = cursor.lastrowid
            
        # Update CRM with contact_id and advance stage
        cursor.execute("""
            UPDATE crm 
            SET contact_id = ?,
                current_stage = 'Contact Found',
                last_activity = 'Identified decision maker: ' || ?,
                next_action = 'Generate personalized outreach email'
            WHERE company_id = ?
        """, (contact_id, f"{name} ({role})", company_id))
        
        conn.commit()
        return contact_id
    finally:
        conn.close()

def add_or_update_crm(company_id: int, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(company_id)
    
    query = f"UPDATE crm SET {', '.join(fields)} WHERE company_id = ?"
    
    try:
        cursor.execute(query, tuple(values))
        conn.commit()
    finally:
        conn.close()

def add_email(crm_id: int, subject: str, body: str, status: str, email_type: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO emails (crm_id, subject, body, status, email_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (crm_id, subject, body, status, email_type, datetime.utcnow().isoformat()))
        email_id = cursor.lastrowid
        
        # Update CRM status based on email sent
        stage = 'Emailed' if email_type == 'Initial' else 'Follow-up Sent'
        next_followup = (datetime.utcnow() + timedelta(days=3)).isoformat()
        
        cursor.execute("""
            UPDATE crm 
            SET current_stage = ?,
                last_activity = ?,
                last_contact_date = ?,
                next_action = ?,
                next_followup_date = ?
            WHERE id = ?
        """, (
            stage,
            f"{email_type} outreach email drafted/queued",
            datetime.utcnow().isoformat(),
            "Wait for reply (simulation active)" if email_type == 'Initial' else "Wait for reply / No further action scheduled",
            next_followup,
            crm_id
        ))
        
        conn.commit()
        return email_id
    finally:
        conn.close()

def simulate_reply(crm_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE crm 
            SET current_stage = 'Replied',
                reply_status = 'Replied',
                reply_count = reply_count + 1,
                last_activity = 'Contact replied to email outreach',
                next_action = 'Trigger human handoff / sales conversation',
                next_followup_date = NULL
            WHERE id = ?
        """, (crm_id,))
        conn.commit()
    finally:
        conn.close()

def get_companies():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def get_contacts():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def get_crm():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                crm.*,
                comp.name as company_name,
                comp.website as company_website,
                cont.name as contact_name,
                cont.role as contact_role,
                cont.email as contact_email
            FROM crm
            JOIN companies comp ON crm.company_id = comp.id
            LEFT JOIN contacts cont ON crm.contact_id = cont.id
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def get_emails():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                e.*,
                comp.name as company_name,
                cont.name as contact_name,
                cont.email as contact_email
            FROM emails e
            JOIN crm c ON e.crm_id = c.id
            JOIN companies comp ON c.company_id = comp.id
            LEFT JOIN contacts cont ON c.contact_id = cont.id
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
