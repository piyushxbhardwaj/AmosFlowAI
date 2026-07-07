import os
import database
from services.sheets_service import sync_crm_to_sheets

def calculate_lead_score(enriched_data: dict) -> float:
    """
    Computes a programmatic GTM Lead Score (0.0 - 1.0) based on weighted parameters.
    """
    score = 0.0
    
    # 1. ICP Fit (30% weight)
    icp_text = str(enriched_data.get("icp_fit", "")).lower()
    icp_keywords = ["saas", "developer", "platform", "b2b", "enterprise", "ops", "marketing", "api"]
    icp_hits = sum(1 for kw in icp_keywords if kw in icp_text)
    icp_score = min(icp_hits / 3.0, 1.0) * 0.30
    score += icp_score
    
    # 2. Funding Status (20% weight)
    funding_text = str(enriched_data.get("funding_signals", "")).lower()
    funding_keywords = ["seed", "series", "raised", "funding", "venture", "backer", "invest", "million"]
    funding_hits = sum(1 for kw in funding_keywords if kw in funding_text)
    funding_score = min(funding_hits / 2.0, 1.0) * 0.20
    score += funding_score
    
    # 3. Hiring Status (20% weight)
    hiring_text = str(enriched_data.get("hiring_insights", "")).lower()
    hiring_keywords = ["hiring", "recruit", "jobs", "careers", "open roles", "engineering", "sales", "growth"]
    hiring_hits = sum(1 for kw in hiring_keywords if kw in hiring_text)
    hiring_score = min(hiring_hits / 2.0, 1.0) * 0.20
    score += hiring_score
    
    # 4. Recent News / Activity (15% weight)
    news_text = str(enriched_data.get("recent_news", "")).lower()
    if news_text and "no news found" not in news_text and "no live search" not in news_text:
        score += 0.15
    elif len(news_text) > 40:
        score += 0.08  # Partial credit for custom/simulated news
        
    # 5. AI Adoption / Maturity (15% weight)
    ai_text = str(enriched_data.get("ai_summary", "")).lower()
    ai_keywords = ["llm", "ai agent", "gpt", "gemini", "openai", "machine learning", "automation", "agentic"]
    ai_hits = sum(1 for kw in ai_keywords if kw in ai_text)
    ai_score = min(ai_hits / 2.0, 1.0) * 0.15
    score += ai_score
    
    return round(score, 2)

def run_crm_agent(company_id: int, enriched_data: dict, contact_id: int = None) -> float:
    """
    Computes lead score, updates SQLite CRM record, and syncs data to Google Sheets.
    """
    print(f"[CRM Agent] Running CRM updates for company ID {company_id}...")
    
    # 1. Calculate lead score
    lead_score = calculate_lead_score(enriched_data)
    
    # 2. Get industry/domain signals
    industry = "AI SaaS" if "ai" in str(enriched_data.get("ai_summary", "")).lower() else "Software & Technology"
    
    # 3. Update database CRM record
    update_data = {
        "lead_score": lead_score,
        "industry": industry
    }
    if contact_id is not None:
        update_data["contact_id"] = contact_id
        
    database.add_or_update_crm(
        company_id=company_id,
        **update_data
    )
    
    # 4. Sync SQLite database contents to Google Sheets (if configured)
    crm_data = database.get_crm()
    sheets_synced = sync_crm_to_sheets(crm_data)
    
    print(f"[CRM Agent] Update completed. Lead Score: {lead_score}. Sheets Synced: {sheets_synced}")
    return lead_score
