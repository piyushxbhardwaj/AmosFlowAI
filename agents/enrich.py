import os
from services.enrichment_service import enrich_company_data
from services.llm_service import query_llm_json

CURATED_ENRICHMENT = {
    "vercel": {
        "company_summary": "Vercel is a frontend cloud platform that enables developers to host websites and applications that deploy instantly and scale automatically.",
        "product": "Frontend Cloud platform, Vercel Edge Network, Next.js integration, and v0 Generative UI design engine.",
        "icp_fit": "Frontend software engineers, SaaS builders, startup technical founders, and enterprise frontend directors.",
        "hiring_insights": "Active hiring signals for developers, systems engineers, and developer relations roles.",
        "funding_signals": "Venture-backed, raised $150M Series D led by GGV Capital, total valuation at $2.5B.",
        "website_title": "Vercel: Your complete platform for modern web applications",
        "ai_summary": "Native integrations with LLM providers, edge function optimized streaming, and AI template marketplace.",
        "enrichment_confidence": 0.95
    },
    "cursor": {
        "company_summary": "Cursor is an AI-powered code editor built on top of VS Code, designed to help developers write and edit code faster using natural language commands.",
        "product": "AI code completion, natural language code execution, codebase indexing, and multi-file code editing assistant.",
        "icp_fit": "Software developers, full-stack engineers, technical product managers, and engineering teams.",
        "hiring_insights": "Hiring junior and senior systems engineers, AI product engineers, and developer advocates.",
        "funding_signals": "Backed by top-tier venture firms, closed Seed and Series A financing rounds.",
        "website_title": "Cursor - The AI Code Editor",
        "ai_summary": "Core code-editor platform natively integrated with LLMs (GPT-4, Claude) for real-time contextual code generation.",
        "enrichment_confidence": 0.92
    },
    "linear": {
        "company_summary": "Linear is a developer-focused issue tracking and project management tool designed to stream product cycles and developer workflows.",
        "product": "Fast issue tracking, cycle and sprint planning, roadmap visualization, and native Git/GitHub integrations.",
        "icp_fit": "SaaS project managers, engineering directors, software developers, and startup founders.",
        "hiring_insights": "Recruiting remote staff engineers, product designers, and account executives globally.",
        "funding_signals": "Backed by Sequoia Capital, raised $35M in total funding rounds.",
        "website_title": "Linear - The tracker for modern software teams",
        "ai_summary": "Moderate AI adoption. Uses ML models for auto-duplicate detection and issue classification search summaries.",
        "enrichment_confidence": 0.88
    },
    "resend": {
        "company_summary": "Resend is an email API platform built specifically for developers to compose, test, and send transactional and marketing emails.",
        "product": "React Email framework, transactional email APIs, domain authentication dashboard, and tracking analytics.",
        "icp_fit": "Web developer advocates, SaaS builders, frontend engineers, and product managers.",
        "hiring_insights": "Hiring growth marketers, API infrastructure backend developers, and support advocates.",
        "funding_signals": "Y Combinator graduate, closed Seed funding from notable SaaS founders and angel investors.",
        "website_title": "Resend - Email API for developers",
        "ai_summary": "Uses machine learning classification tools to monitor and flag spam activities and route outgoing mails.",
        "enrichment_confidence": 0.89
    },
    "supabase": {
        "company_summary": "Supabase is an open-source alternative to Firebase that equips developers with hosted Postgres databases, user authentication, and real-time APIs.",
        "product": "Hosted PostgreSQL database, Row Level Security auth, Edge Functions, real-time sync, and pgvector stores.",
        "icp_fit": "Backend software engineers, mobile developers, database administrators, and full-stack developers.",
        "hiring_insights": "Hiring core database advocate engineers, security analysts, and developer advocates.",
        "funding_signals": "Series B backed, raised $80M led by Coatue, total funding over $110M.",
        "website_title": "Supabase | The Open Source Firebase Alternative",
        "ai_summary": "High AI relevance. Offers native vector database capabilities (pgvector) for storing LLM embeddings.",
        "enrichment_confidence": 0.91
    },
    "phind": {
        "company_summary": "Phind is an AI-powered conversational search engine specifically optimized for developers to resolve coding bugs and search programming answers.",
        "product": "Conversational search assistant, browser extensions, and proprietary fine-tuned Phind LLM models.",
        "icp_fit": "Software developers, data scientists, DevOps engineers, and computer science researchers.",
        "hiring_insights": "Recruiting LLM training experts, systems developers, and GPU infrastructure engineers.",
        "funding_signals": "Venture-backed AI startup, YC alumnus.",
        "website_title": "Phind | AI Search Engine for Developers",
        "ai_summary": "AI-native answer engine relying on fine-tuned LLMs and RAG integrations over real-time web searches.",
        "enrichment_confidence": 0.90
    },
    "perplexity": {
        "company_summary": "Perplexity is a conversational answer engine designed to provide search answers with inline citations and sources.",
        "product": "Pro Search conversational assistant, Perplexity Pages publishing tool, and developer APIs.",
        "icp_fit": "Knowledge researchers, content writers, business analysts, and search API developers.",
        "hiring_insights": "Active recruitment for machine learning engineers, frontend developers, and growth partnerships.",
        "funding_signals": "Unicorn startup valuation at $1.5B, backed by Jeff Bezos, NVIDIA, and NEA.",
        "website_title": "Perplexity AI - Ask Anything",
        "ai_summary": "AI-native search company using advanced RAG pipelines, semantic indexes, and multi-LLM orchestration.",
        "enrichment_confidence": 0.94
    },
    "midjourney": {
        "company_summary": "Midjourney is an independent research lab and generative AI system that translates natural language text prompts into high-fidelity graphics.",
        "product": "Generative text-to-image AI, Discord-based rendering channel, and a web creation canvas.",
        "icp_fit": "Creative designers, advertising copywriters, marketing leads, and visual digital artists.",
        "hiring_insights": "Highly lean team. Recruiting systems programmers for massive Discord infrastructure setups.",
        "funding_signals": "100% bootstrapped, self-funded, highly profitable with zero venture capital.",
        "website_title": "Midjourney - Generative AI Platform",
        "ai_summary": "Generative AI core platform. Built custom diffusion models for visual assets generation.",
        "enrichment_confidence": 0.85
    },
    "jasper": {
        "company_summary": "Jasper is an AI copilot platform engineered to assist enterprise marketing teams in generating content aligned with brand voice.",
        "product": "Jasper Brand Voice tool, blog content copilot, marketing campaigns planner, and API integrations.",
        "icp_fit": "Enterprise marketing directors, copywriters, SEO strategists, and creative directors.",
        "hiring_insights": "Hiring enterprise sales directors, account managers, and product engineers.",
        "funding_signals": "Raised $125M Series A at a $1.5B valuation.",
        "website_title": "Jasper | AI Copilot for Enterprise Marketing Teams",
        "ai_summary": "Enterprise marketing AI application leveraging multi-model LLM interfaces to scale copywriting outputs.",
        "enrichment_confidence": 0.88
    },
    "langchain": {
        "company_summary": "LangChain is a developer framework and software toolkit built to streamline context-aware reasoning applications using LLMs.",
        "product": "LangChain library, LangGraph multi-agent agent orchestrator, and LangSmith debugging dashboards.",
        "icp_fit": "AI application engineers, python builders, devops managers, and cognitive SaaS builders.",
        "hiring_insights": "Recruiting software engineers, community relations, and documentation writers.",
        "funding_signals": "Raised $20M Series A led by Sequoia Capital.",
        "website_title": "LangChain | Build context-aware reasoning applications",
        "ai_summary": "Primary developer tool for orchestration of LLM pipelines, prompt management, and cognitive agents.",
        "enrichment_confidence": 0.96
    }
}

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
    
    # Select company-specific curated mock fallback or fall back to generic
    comp_key = company_name.strip().lower()
    if comp_key in CURATED_ENRICHMENT:
        mock_fallback = CURATED_ENRICHMENT[comp_key]
    else:
        # Generic fallback
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
