import os
from services.llm_service import query_llm_json

def run_personalize_agent(company_name: str, contact_name: str, contact_role: str, enriched_data: dict) -> dict:
    """
    Generates a highly personalized cold outreach email targeting the decision maker.
    """
    print(f"[{company_name}] Generating personalized outreach for {contact_name} ({contact_role})...")
    
    first_name = contact_name.split()[0] if contact_name else "there"
    
    system_prompt = """You are an elite outbound copywriter at HeyAmos. HeyAmos builds autonomous GTM systems that automate company enrichment, contact discovery, and personalization to help sales teams save hundreds of hours of manual prospecting.
    
    Your task is to write a highly personalized, conversational, and direct cold outreach email.
    
    CRITICAL Email Rules:
    1. Length: The email body must be under 120 words (aim for 70-100 words). Be concise!
    2. Tone: Conversational, friendly, and human. Avoid stuffy business templates (never say 'Hope this email finds you well' or 'Dear X'). Use 'Hi X,'.
    3. Hyper-Personalized: Reference their specific product details, website title, or news. Avoid generic compliments like 'I love your platform'.
    4. Value Proposition: Explain why HeyAmos can help them specifically. HeyAmos automates GTM pipelines from CSV inputs directly to email drafts and CRMs, reducing list building work.
    5. Call to Action (CTA): Keep it low friction, e.g., asking if they have 5 minutes or if they handle outbound workflows.
    
    Output JSON format:
    {
      "subject": "Email subject line...",
      "body": "Hi [First Name],\n\n[Email body paragraphs]...\n\nBest,\n[Your Name]",
      "personalization_rationale": "A short sentence explaining why you chose this specific hook..."
    }
    """
    
    user_prompt = f"""
    Target Company: {company_name}
    Contact Person: {contact_name}
    Contact Role: {contact_role}
    
    Enriched Company Info:
    - Product: {enriched_data.get('product', 'Unknown')}
    - ICP: {enriched_data.get('icp_fit', 'Unknown')}
    - Title: {enriched_data.get('website_title', 'Unknown')}
    - Summary: {enriched_data.get('company_summary', 'Unknown')}
    - Recent News: {enriched_data.get('recent_news', 'Unknown')}
    - Hiring / Growth Info: {enriched_data.get('hiring_insights', 'Unknown')}
    
    Write the email from 'Piyush at HeyAmos' targeting first name: {first_name}.
    """
    
    mock_fallback = {
        "subject": f"Automating outbound for {company_name}",
        "body": f"Hi {first_name},\n\nI was looking at {company_name}'s website and noticed you are scaling your {enriched_data.get('product', 'product offering')}.\n\nAt HeyAmos, we help teams automate the manual work of prospecting. We sync with tools like Apollo to pull decision makers, write personalized drafts referencing their products, and push them to a CRM automatically.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline your team's outreach?\n\nBest,\nPiyush\nAmosFlow AI Team",
        "personalization_rationale": "Referenced their core product scaling and addressed their role directly."
    }
    
    result = query_llm_json(system_prompt, user_prompt, mock_fallback)
    
    # Ensure fields are present
    for field, default in mock_fallback.items():
        if field not in result:
            result[field] = default
            
    print(f"[{company_name}] Personalized email generated.")
    return result
