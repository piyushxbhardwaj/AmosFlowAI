# AmosFlow AI
## An Autonomous GTM Pipeline for AI-Powered Company Research, Personalized Outreach, and Follow-Up Automation

AmosFlow AI is a lightweight GTM (Go-To-Market) automation system that automates company enrichment, decision-maker discovery, personalized cold outreach, CRM updates, and follow-up generation from a simple CSV input. 

This repository implements the complete end-to-end workflow using **LangGraph** for AI reasoning agent state orchestration, **FastAPI** for core REST API routes, and **Streamlit** for a visual sales pipeline dashboard.

---

## Architecture Diagram

The system is designed with a strict separation of concerns, separating the AI reasoning graph from operational service interfaces:

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

## Features
- **Idempotent Leads Loader**: Reads seed targets from `companies.csv` and skips or updates existing entries using domain checking to prevent duplication.
- **AI-Powered Company Analysis**: Queries enrichment APIs (Tavily/Firecrawl fallbacks) and scrapes website content using BeautifulSoup, then feeds findings into a Gemini or OpenAI LLM to parse GTM insights (ICPs, hiring, funding, product offerings).
- **Contact Discovery**: Queries Apollo APIs to find relevant executive contacts (CEO, Founder, Growth Leads), falling back to a structured and clearly labeled simulated placeholder (`demo-contact@example.com (Simulated Contact)`) if credentials are absent.
- **Explainable Lead Scoring**: Programmatically computes a GTM fit score (0.0 to 1.0) based on weighted parameters (ICP fit, funding signals, hiring status, news, AI adoption indicators) and saves a confidence metric.
- **Hyper-Personalized Copywriting**: Generates friendly, human-sounding outreach emails (< 120 words) referencing target products and news while strictly omitting generic praise or boilerplate merge words.
- **Email Dispatch & Queueing**: Saves emails to a SQLite dispatch queue. If Gmail OAuth credentials are configured, it automatically drafts them in the user's Gmail box.
- **Syncable CRM Database**: Tracks company profiles, contacts, lead score, current pipeline stages, reply state, and activities in SQLite, auto-syncing to Google Sheets.
- **Reply monitoring & Automation**: Implements a background APScheduler that polls for replies. If a prospect replies (simulated via API or UI), outreach stops. If there is no response, the system automatically drafts a shorter polite follow-up.

---

## Workflow Nodes
1. `load_csv`: Reads targets and imports them as `Imported` leads.
2. `enrich_company`: Scrapes target homepages and crawls news signals.
3. `analyze_company`: Extracts GTM insights returning a structured JSON schema.
4. `find_contact`: Discovers a decision-maker email and social profiles.
5. `personalize_email`: Drafts a tailored cold outreach email (< 120 words) with subject and copy.
6. `draft_email`: Places email in SQLite queue and syncs to Gmail drafts.
7. `update_crm`: Updates lead score and sets pipeline stage to `Emailed`.
8. `check_reply`: Periodically checks reply state.
9. `generate_followup`: Crafts a polite, shorter follow-up email if no reply is detected after 3 days.
10. `queue_followup`: Queues the follow-up draft.
11. `update_crm_followup`: Updates CRM stage to `Follow-up Sent`.

---

## Technology Stack
- **Backend Framework**: Python 3.12, FastAPI, Uvicorn
- **Agent Orchestration**: LangGraph, LangChain Core
- **LLM Connectivity**: LangChain Google GenAI (Gemini 1.5 Flash / Gemini Pro) or LangChain OpenAI (GPT-4o / GPT-4o-mini)
- **Database**: SQLite3 (built-in)
- **Dashboard**: Streamlit
- **Enrichment & Scraping**: BeautifulSoup4, Requests, Tavily API (optional)
- **Scheduler**: APScheduler
- **Google Integrations**: Google API Client, Google Auth (for Sheets and Gmail, optional)

---

## Installation

### 1. Clone the repository
Navigate into the workspace folder `d:/Project/AmosFlow AI/`.

### 2. Install Dependencies
Make sure you have python 3.12 installed. Run the command to install packages:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Setup
Copy `.env.example` to a new file named `.env` and set your API keys:
```text
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-gemini-api-key
TAVILY_API_KEY=your-tavily-search-key
APOLLO_API_KEY=your-apollo-person-search-key
GOOGLE_SHEETS_CREDENTIALS=path/to/sheets-credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-google-spreadsheet-id
```
*Note: If no API keys are provided, the system gracefully falls back to mock engines, BeautifulSoup scraping, and demo placeholder profiles, making it 100% runnable out of the box.*

---

## Execution Guide

To run the full pipeline locally:

### 1. Launch FastAPI Backend
Start the backend server on `http://127.0.0.1:8000`:
```bash
uvicorn backend.main:app --reload --port 8000
```

### 2. Launch Streamlit Dashboard
In another terminal window, run the dashboard:
```bash
streamlit run streamlit/app.py
```
Open `http://localhost:8501` in your browser.

---

## Simulated Demonstration Scenario
1. Navigate to the **Control Panel & Actions** tab on Streamlit.
2. Click **Trigger GTM Outreach Pipeline**. This reads the seed companies from `data/companies.csv`, processes them through LangGraph agents, updates SQLite, and creates outreach drafts.
3. Refresh data or click tabs (**CRM Pipeline**, **Enriched Companies**, **Target Contacts**, **Outreach Logs**) to see live outputs.
4. Select a company and click **Trigger Simulated Reply** on the control panel. Refreshing will show that lead as `Replied`, stopping the follow-up flow.
5. For other emailed leads, click **Execute Follow-up Scheduler Now** to simulate time passing. The system will detect no reply and automatically queue a polite, short follow-up draft.
