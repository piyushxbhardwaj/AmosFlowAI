import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """
    Returns the Google Sheets API service object using service account credentials.
    """
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    
    if not creds_path or not spreadsheet_id:
        return None, None
        
    if not os.path.exists(creds_path):
        print(f"Google Sheets credentials file not found at: {creds_path}")
        return None, None
        
    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        return service, spreadsheet_id
    except Exception as e:
        print(f"Error initializing Google Sheets API: {e}")
        return None, None

def sync_crm_to_sheets(crm_rows: list) -> bool:
    """
    Syncs the CRM SQLite data directly to Google Sheets.
    """
    service, spreadsheet_id = get_sheets_service()
    if not service or not spreadsheet_id:
        print("Google Sheets sync skipped: Credentials or Spreadsheet ID not configured.")
        return False
        
    try:
        # Define headers
        headers = [
            "CRM ID", "Company Name", "Website", "Contact Name", "Role", "Email", 
            "Current Stage", "Lead Score", "Reply Status", "Reply Count", 
            "Last Activity", "Last Contact Date", "Next Action", "Next Follow-up Date"
        ]
        
        values = [headers]
        for row in crm_rows:
            values.append([
                row.get("id"),
                row.get("company_name"),
                row.get("company_website"),
                row.get("contact_name") or "N/A",
                row.get("contact_role") or "N/A",
                row.get("contact_email") or "N/A",
                row.get("current_stage"),
                row.get("lead_score"),
                row.get("reply_status"),
                row.get("reply_count"),
                row.get("last_activity"),
                row.get("last_contact_date"),
                row.get("next_action"),
                row.get("next_followup_date")
            ])
            
        # Write to Sheet1 (overwrite entire content for simplicity in PoC)
        range_name = 'Sheet1!A1'
        body = {
            'values': values
        }
        
        # Clear sheet first
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A:Z'
        ).execute()
        
        # Update sheet values
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print("Google Sheets CRM synchronized successfully.")
        return True
    except Exception as e:
        print(f"Failed to sync CRM to Google Sheets: {e}")
        return False
