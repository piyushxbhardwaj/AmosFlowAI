import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def get_gmail_service():
    """
    Returns the Gmail service object using local credentials.
    Returns None if not configured.
    """
    creds = None
    token_path = 'token.json'
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS") or 'credentials.json'
    
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            pass
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
                
        if not creds:
            if not os.path.exists(creds_path):
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error initializing Gmail OAuth: {e}")
                return None
                
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None

def create_gmail_draft(to_email: str, subject: str, body: str) -> dict:
    """
    Creates a draft in Gmail. Fallback to simulation if credentials do not exist.
    """
    service = get_gmail_service()
    if not service:
        # Fallback to simulation
        return {
            "success": True,
            "status": "Simulated Draft Created",
            "message": f"Draft created in SQLite database for {to_email}. Gmail OAuth credentials unavailable.",
            "draft_id": None
        }
        
    try:
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        draft = {
            'message': {
                'raw': raw_message
            }
        }
        
        draft_response = service.users().drafts().create(userId='me', body=draft).execute()
        return {
            "success": True,
            "status": "Gmail Draft Created",
            "message": f"Gmail draft created with ID: {draft_response.get('id')}",
            "draft_id": draft_response.get('id')
        }
    except Exception as e:
        print(f"Failed to create Gmail draft: {e}")
        return {
            "success": False,
            "status": "Draft Failed",
            "message": str(e),
            "draft_id": None
        }
