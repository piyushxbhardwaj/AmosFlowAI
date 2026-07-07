import os
from services.llm_service import query_llm_json

def run_followup_agent(company_name: str, contact_name: str, previous_subject: str, previous_body: str) -> dict:
    """
    Generates a brief, polite follow-up email (< 60 words) referencing the previous outreach.
    """
    print(f"[{company_name}] Generating follow-up for {contact_name}...")
    
    first_name = contact_name.split()[0] if contact_name else "there"
    
    system_prompt = """You are an outbound specialist at HeyAmos. You are sending a short, polite follow-up email to a contact who has not yet replied to your initial message.
    
    CRITICAL Follow-up Rules:
    1. Length: Keep the body under 60 words (extremely brief and punchy!).
    2. Reference: Politely reference the previous message we sent about automating GTM pipelines.
    3. Low friction: Ask for a quick 5-minute call or if they would prefer a quick demo link.
    4. Conversational: Natural and polite.
    
    Output JSON format:
    {
      "subject": "Re: [previous email subject]...",
      "body": "Hi [First Name],\n\n[Brief follow-up body]...\n\nBest,\n[Your Name]",
      "personalization_rationale": "A short note on why this follow-up angle is appropriate..."
    }
    """
    
    user_prompt = f"""
    Target Company: {company_name}
    Contact Person: {contact_name}
    
    Previous Email Subject: {previous_subject}
    Previous Email Body:
    {previous_body}
    
    Generate the follow-up email from 'Piyush at HeyAmos' targeting first name: {first_name}.
    """
    
    # Generate clean Re: subject line
    re_subject = previous_subject if previous_subject.lower().startswith("re:") else f"Re: {previous_subject}"
    
    mock_fallback = {
        "subject": re_subject,
        "body": f"Hi {first_name},\n\nI wanted to follow up quickly on my last email. I know you're busy, but I thought HeyAmos could really help {company_name} automate your outreach list building.\n\nDo you have 5 minutes for a brief call next Tuesday morning?\n\nBest,\nPiyush",
        "personalization_rationale": "Kept it direct, polite, and checked in on the previous proposal."
    }
    
    result = query_llm_json(system_prompt, user_prompt, mock_fallback)
    
    # Ensure fields are present
    for field, default in mock_fallback.items():
        if field not in result:
            result[field] = default
            
    print(f"[{company_name}] Follow-up email generated.")
    return result
