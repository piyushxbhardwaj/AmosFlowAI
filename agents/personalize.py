import os
from services.llm_service import query_llm_json

# Curated simulated outreach emails for our key demo targets
CURATED_EMAILS = {
    "vercel": {
        "subject": "Edge performance and AI search discovery for Vercel",
        "body": "Hi Lee,\n\nI came across Vercel while looking at developer infrastructure companies. Your work around Next.js, the Frontend Cloud, and the v0 UI generator stood out.\n\nAt HeyAmos, we help developer-first brands improve how they are discovered and ranked inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline outbound prospecting for Vercel?\n\nBest,\nPiyush\nAmosFlow AI Team",
        "personalization_rationale": "Addressed Lee Robinson by name and referenced Vercel edge/Next.js infrastructure and v0 tool."
    },
    "cursor": {
        "subject": "AI workflows and discovery optimization for Cursor",
        "body": "Hi Arvid,\n\nI've been following how Cursor is changing software development workflows with AI-assisted coding and codebase-aware editing tools.\n\nAt HeyAmos, we help developer-first brands improve how they are discovered and ranked inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline outbound prospecting for Cursor?\n\nBest,\nPiyush\nAmosFlow AI Team",
        "personalization_rationale": "Hooked on Cursor's AI-assisted coding and codebase-aware editing features."
    },
    "linear": {
        "subject": "Developer issue tracking & GTM flows",
        "body": "Hi Karri,\n\nI've been following Linear's issue tracker development. Your emphasis on speed, clean UI, and streamlined product sprint cycles makes a massive difference for software teams.\n\nAt HeyAmos, we help developer-first brands improve how they are discovered and ranked inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline outbound prospecting for Linear?\n\nBest,\nPiyush\nAmosFlow AI Team",
        "personalization_rationale": "Referenced Linear issue tracking and streamlined product sprint cycles."
    },
    "resend": {
        "subject": "Developer-first email APIs & GTM automation",
        "body": "Hi Zeno,\n\nI really liked how Resend focuses on making developer-first email infrastructure simple with React Email and your transactional delivery API.\n\nAt HeyAmos, we help developer-first brands improve how they are discovered and ranked inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline outbound prospecting for Resend?\n\nBest,\nPiyush\nAmosFlow AI Team",
        "personalization_rationale": "Addressed Zeno Rocha and hooked on React Email and transactional APIs."
    },
    "supabase": {
        "subject": "Postgres embeddings & GTM automation",
        "body": "Hi Paul,\n\nI was reading about Supabase's open-source Firebase alternative, especially your hosted PostgreSQL databases and pgvector vector embeddings support.\n\nAt HeyAmos, we help developer-first brands improve how they are discovered and ranked inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline outbound prospecting for Supabase?\n\nBest,\nPiyush\nAmosFlow AI Team",
        "personalization_rationale": "Hooked on open-source Firebase alternative pgvector database embeddings."
    },
    "langchain": {
        "subject": "Context-aware agent workflows & GTM discovery",
        "body": "Hi Harrison,\n\nI've been building with the LangChain framework and LangGraph orchestrator to build context-aware reasoning applications and agents.\n\nAt HeyAmos, we help developer-first brands improve how they are discovered and ranked inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline outbound prospecting for LangChain?\n\nBest,\nPiyush\nAmosFlow AI Team",
        "personalization_rationale": "Addressed Harrison Chase and referenced LangChain framework and LangGraph agents."
    }
}

def run_personalize_agent(company_name: str, contact_name: str, contact_role: str, enriched_data: dict) -> dict:
    """
    Generates a highly personalized cold outreach email targeting the decision maker.
    """
    print(f"[{company_name}] Generating personalized outreach for {contact_name} ({contact_role})...")
    
    first_name = contact_name.split()[0] if contact_name else "there"
    
    system_prompt = """You are an elite outbound copywriter at HeyAmos. HeyAmos helps developer-first brands improve how they are discovered and ranked inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.
    
    Your task is to write a highly personalized, conversational, and direct cold outreach email.
    
    CRITICAL Email Rules:
    1. Length: The email body must be under 120 words (aim for 70-100 words). Be concise!
    2. Tone: Conversational, friendly, and human. Avoid stuffy business templates (never say 'Hope this email finds you well' or 'Dear X'). Use 'Hi X,'.
    3. Hyper-Personalized: Reference their specific product details, website title, or news. Avoid generic compliments.
    4. Value Proposition: Explain why HeyAmos can help them specifically. HeyAmos helps companies index and optimize their discovery footprint in conversational AI engines (ChatGPT, Perplexity) and drafts context-rich prospecting outbound messages.
    5. Call to Action (CTA): Keep it low friction, e.g., asking if they have 5 minutes to chat.
    
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
    
    # Check if we have a curated, bespoke fallback template
    comp_key = company_name.strip().lower()
    if comp_key in CURATED_EMAILS:
        mock_fallback = CURATED_EMAILS[comp_key]
    else:
        # Standard dynamic mock fallback (fixed double periods and updated value prop)
        product_info = enriched_data.get('product', 'product offering').rstrip('.')
        mock_fallback = {
            "subject": f"Automating outreach and AI discovery for {company_name}",
            "body": f"Hi {first_name},\n\nI was looking at {company_name}'s website and noticed you are scaling your {product_info}.\n\nAt HeyAmos, we help brands optimize how they are discovered inside AI search engines like ChatGPT and Perplexity, while automating outbound prospecting with context-aware GTM workflows.\n\nAre you open to a quick 5-minute chat next week to see how we could streamline your team's outreach?\n\nBest,\nPiyush\nAmosFlow AI Team",
            "personalization_rationale": "Referenced their core product scaling and updated outbound value proposition."
        }
    
    result = query_llm_json(system_prompt, user_prompt, mock_fallback)
    
    # Ensure fields are present
    for field, default in mock_fallback.items():
        if field not in result:
            result[field] = default
            
    print(f"[{company_name}] Personalized email generated.")
    return result
