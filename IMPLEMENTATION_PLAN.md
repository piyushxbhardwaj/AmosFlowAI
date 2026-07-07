# AmosFlow AI
## AI-Powered GTM Automation System
### Implementation Plan (Lightweight Proof of Concept)

---

## Executive Summary
AmosFlow AI is a lightweight AI-powered GTM automation proof of concept that automates company enrichment, contact discovery, personalized outreach, CRM updates, and follow-up generation from a simple CSV input. The workflow is orchestrated with LangGraph and designed to run with minimal manual intervention while gracefully falling back to simulated components when external APIs are unavailable. 

The system separates AI reasoning (LangGraph agents) from operational services (email, CRM, storage), making the workflow modular, testable, and easy to extend.

**This implementation demonstrates an end-to-end autonomous GTM workflow using AI agents, with a focus on automation, personalization, and minimal manual intervention.**

---

## Technology Stack
- **Backend & Logic**: Python 3.12, FastAPI
- **Workflow Orchestration**: LangGraph
- **LLM Engine**: Gemini or OpenAI GPT-4
- **Database**: SQLite (CRM + Email queue)
- **Dashboard**: Streamlit
- **Enrichment Services**: BeautifulSoup (Scraping), Tavily/Firecrawl (Search APIs, optional)
- **Contact Service**: Apollo API (optional, with simulated fallback)
- **Outreach & CRM Sync**: Gmail API & Google Sheets API (optional, with simulated fallbacks)

*Note: Consistent with the assignment scope, this implementation prioritizes a working end-to-end proof of concept over full production scale.*

---

## Core Design Principle
**Minimal Manual Work**: The workflow is designed to run autonomously after receiving a CSV of target companies. Manual intervention is only required for optional approval before email sending or when external API credentials are unavailable.

---

## Demo Assumptions & Mocks
To facilitate offline running and simple testing:
- **Email Sending**: Simulated by writing to a SQLite queue, or creating Gmail Drafts if OAuth is configured.
- **Reply Detection**: Simulated through an API endpoint and Streamlit buttons.
- **Contact Discovery**: Queries Apollo if configured; falls back to a clearly-labeled, non-person-specific placeholder: `demo-contact@example.com (Simulated Contact)`.
- **Enrichment APIs**: Uses Tavily/Firecrawl if configured; falls back to scrapers (BeautifulSoup) or simulated SaaS information.

---

## Technical Reasoning: Why LangGraph?
We use **LangGraph** because GTM pipelines are stateful, cyclical, and asynchronous.
- **State & Transitions**: Maintains context as a lead moves from "Imported" to "Enriched," "Contact Found," and "Emailed."
- **Conditional Branching**: Routes flow dynamically based on reply status.
- **Idempotency**: Detects existing companies by domain to update rather than duplicate.

---

## Architecture Diagram

```text
                  CSV Companies
                        │
                        ▼
              FastAPI REST API
                        │
                        ▼
             LangGraph Workflow
 ┌──────────────────────────────────────┐
 │ Company Enrichment                   │
 │ Analyze Company                      │
 │ Contact Discovery                    │
 │ Personalized Outreach                │
 │ Follow-up Generation                 │
 └──────────────────────────────────────┘
                        │
                        ▼
              Service Layer
      Gmail │ Sheets │ SQLite │ Scheduler
                        │
                        ▼
              Streamlit Dashboard
```

---

## Repository Structure
```text
AmosFlow-AI/
├── backend/            # FastAPI REST endpoints & background worker
├── agents/             # LangGraph workflow reasoning nodes
├── services/           # Gmail, Google Sheets, SQLite & scrapers
├── streamlit/          # Streamlit live CRM dashboard
├── data/               # Input CSV & template assets
├── logs/               # App run tracking & troubleshooting logs
├── README.md           # Deployment & execution guide
└── requirements.txt    # Third-party dependency definitions
```

---

## Workflow Nodes & Structured Output
1. **`load_csv`**: Reads the target CSV and registers the company in the DB (stage: `Imported`).
2. **`enrich_company`**: Queries APIs or falls back to scraping.
3. **`analyze_company`**: Uses LLM to compile and analyze collected inputs. Returns a structured JSON payload:
   ```json
   {
     "company_summary": "LLM-generated detailed business description...",
     "icp_fit": "Analysis of alignment with target ICP...",
     "hiring_insights": "Analysis of job postings and growth signals...",
     "funding_signals": "Latest funding rounds or capital structure signals...",
     "enrichment_confidence": 0.95
   }
   ```
4. **`find_contact`**: Locates or mocks a target contact (`demo-contact@example.com (Simulated Contact)`).
5. **`personalize_email`**: Crafts a personalized email (< 120 words). Returns a structured JSON payload:
   ```json
   {
     "subject": "Email subject line targeting the business problem...",
     "body": "Conversational email body mentioning the product/news and how HeyAmos helps...",
     "personalization_rationale": "Explanation of why this news or product detail was referenced..."
   }
   ```
6. **`draft_email`**: Saves email to queue and drafts to Gmail if configured.
7. **`update_crm`**: Computes Lead Score and updates status.
8. **`check_reply`**: Monitors/simulates checking replies.
9. **`generate_followup`**: Generates a follow-up draft if no reply.
10. **`queue_followup`**: Queues the follow-up.
11. **`update_crm_followup`**: Finalizes CRM stage.

*Each workflow execution maintains a shared LangGraph state containing company metadata, enrichment results, contact details, CRM status, and generated outreach artifacts.*

---

## Lead Score Computation & Explainability
The lead score (0.0 to 1.0) is based on simple weighted parameters:
1. **ICP Match** (30%): Fit with SaaS/AI solutions.
2. **Funding Status** (20%): Positive signals of budget.
3. **Hiring Status** (20%): Active hiring in growth or tech.
4. **Recent News** (15%): High growth/activity indicators.
5. **AI Maturity** (15%): Explicit adoption of AI.

### Explainability
Every enrichment and analysis result stored in the CRM includes:
- **Summary**: LLM-generated business profiling.
- **Enrichment Confidence**: Score (0.0 - 1.0) rating lead relevance and data completeness.
- **Sources Used**: List of URLs scraped or API search results utilized.

---

## Expected Environment Variables
Create a `.env` file with these values (defaulting to mocks if keys are empty):
```text
OPENAI_API_KEY
GOOGLE_API_KEY
APOLLO_API_KEY
TAVILY_API_KEY
FIRECRAWL_API_KEY
GOOGLE_SHEETS_CREDENTIALS
```

---

## Success Metrics

| Metric | Expected Result |
| --- | --- |
| Companies enriched | All input companies processed |
| Contacts discovered | Apollo or simulated fallback |
| Personalized emails | Generated for every contact |
| CRM updates | Recorded after each workflow stage |
| Follow-up | Automatically queued for non-responses |

---

## Conclusion
AmosFlow AI demonstrates how AI agents can automate the core stages of a GTM workflow—from company research and contact discovery to personalized outreach, CRM updates, and follow-up generation. The architecture emphasizes modularity, graceful fallbacks, and minimal manual intervention while remaining lightweight enough to serve as a practical proof of concept. The modular architecture also allows additional channels, CRM integrations, and richer enrichment services to be incorporated with minimal changes to the core workflow.
