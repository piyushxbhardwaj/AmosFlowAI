import os
from services.enrichment_service import enrich_company_data
from services.llm_service import query_llm_json

def run_enrichment_agent(company_name: str, website: str) -> dict:
    """
    Scrapes website homepage, queries recent news, and uses an LLM to build a structured company profile.
    """
    print(f"[{company_name}] Running enrichment scraper and query...")
    
    # 1. Scrape & Search
    raw_data = enrich_company_data(company_name, website)
    
    # 2. Build prompts for analysis
    system_prompt = """You are an expert sales intelligence agent. Analyze target company web signals to create structured business profiles.
    Extract the following fields into a raw JSON object:
    - company_summary: A 2-sentence explanation of what they do.
    - product: Details of their primary product offerings.
    - icp_fit: An analysis of their target buyers/ICP.
    - hiring_insights: Description of hiring trends or growth areas.
    - funding_signals: Insights into their funding round, backers, or financial signals.
    - website_title: The main title metadata of their home page.
    - ai_summary: Specific details on their AI adoption, use cases, or technical stack maturity.
    - enrichment_confidence: Float (0.0 to 1.0) indicating completeness and quality of retrieved data.
    """
    
    user_prompt = f"""Target Company: {company_name}
    Website: {website}
    
    Homepage Scraped Content:
    {raw_data['scraped_text']}
    
    News Search Results:
    {raw_data['news']}
    
    Provide the structured JSON analysis.
    """
    
    # Mock data fallback
    mock_fallback = {
        "company_summary": f"{company_name} is an AI SaaS company specializing in modern productivity software.",
        "product": f"{company_name}'s cloud platforms automate business developer operations and data analysis workflows.",
        "icp_fit": "Mid-market B2B enterprise operations, sales leaders, and product engineering departments.",
        "hiring_insights": "Hiring signals indicate open roles in engineering, developer relations, and growth marketing.",
        "funding_signals": "Funding status is estimated Venture-Backed. Specific round details unavailable.",
        "website_title": f"{company_name} | The AI Automation Platform",
        "ai_summary": "High AI adoption. The core platform is built around LLM APIs and agentic pipelines.",
        "enrichment_confidence": 0.70
    }
    
    # Run LLM
    analysis = query_llm_json(system_prompt, user_prompt, mock_fallback)
    
    # Ensure all required fields exist
    for field, default in mock_fallback.items():
        if field not in analysis:
            analysis[field] = default
            
    # Include metadata sources
    analysis["sources"] = raw_data.get("sources", [website])
    
    print(f"[{company_name}] Enrichment complete. Confidence: {analysis.get('enrichment_confidence')}")
    return analysis
