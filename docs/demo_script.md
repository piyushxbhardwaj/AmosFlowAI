# AmosFlow AI - Video Demonstration Script

This script outlines the visual action, screen view, and narration voiceover for the AmosFlow AI autonomous GTM pipeline.

---

## Segment 1: Project Overview (0:00 - 0:30)
*   **Visual**: Show the GitHub repository (`https://github.com/piyushxbhardwaj/AmosFlowAI`) and the folder layout structure. Zoom in slightly on the directories: `backend`, `agents`, `services`, `streamlit`.
*   **Narration**:
    > "Hi, I'm Piyush. Today I'm demonstrating AmosFlow AI, an autonomous GTM pipeline built for the HeyAmos GTM Engineer case study. The goal of this system is simple: take a CSV target sheet and automatically enrich leads, find decision makers, write personalized cold emails, update the CRM, and handle follow-up emails for non-responses without manual work. As you can see, the codebase is modular, containing distinct folders for our reasoning agents, operational services, uvicorn API routes, and a Streamlit frontend."

---

## Segment 2: Architecture & LangGraph Design (0:30 - 0:50)
*   **Visual**: Open the `IMPLEMENTATION_PLAN.md` file in the IDE or browser and point to the block diagram.
*   **Narration**:
    > "The system enforces a clear separation of concerns. We use LangGraph to orchestrate the core AI reasoning steps: Enrichment, Analysis, Contact Discovery, and Personalization. Operational adapters for Gmail, Google Sheets, SQLite, and the AP background scheduler are isolated in the service layer. This keeps our code highly modular and testable."

---

## Segment 3: FastAPI Backend & API Docs (0:50 - 1:10)
*   **Visual**: Open browser tab showing Swagger API Docs at `http://127.0.0.1:8000/docs`. Scroll down to show the available endpoints: `POST /run`, `GET /crm`, `GET /emails`, `POST /simulate-reply`, and `POST /run-scheduler`.
*   **Narration**:
    > "The backend is powered by FastAPI. Here in the Swagger docs, we see endpoints that expose pipeline operations: a POST run endpoint to start the bulk campaign, fetch endpoints to retrieve CRM data and emails, and simulation endpoints to trigger contact replies and force scheduler checks."

---

## Segment 4: Streamlit Dashboard Overview (1:10 - 1:40)
*   **Visual**: Switch tab to the Streamlit Dashboard at `http://127.0.0.1:8501`. Highlight the dark mode style and the metric cards: Total Leads, Outreach Emailed, Warm Replies, and Avg Lead Score.
*   **Narration**:
    > "Now let's open the sales dashboard. Built with Streamlit, it displays key high-level operational metrics. We have tabs for our CRM Pipeline tracker, Enriched Company intelligence, target contacts, and the email logs. At the moment, the CRM is empty as we haven't initiated the run yet."

---

## Segment 5: Launching GTM Pipeline & Verification (1:40 - 3:00)
*   **Visual**: Click on the 'Control Panel & Actions' tab. Click the large purple button **Trigger GTM Outreach Pipeline**. Switch to the 'CRM Pipeline' tab, click 'Refresh Data' in the sidebar to see the leads populating. Open the 'Enriched Companies' tab and expand Vercel, showing summary, ICP, news, and confidence metrics. Open 'Target Contacts' to show the discovered contacts. Expand 'Outreach Queue & Logs' to show the generated email draft.
*   **Narration**:
    > "Let's head to the Control Panel and click 'Trigger GTM Outreach Pipeline'. This launches a background task that parses our seed companies list. Clicking refresh, we see the pipeline filling in real-time. In the Enriched Companies tab, we have detailed business profiles, product offerings, ICP analysis, and news signals. Under Target Contacts, we have decision-maker emails, and in the Outreach logs, the system has drafted highly personalized, conversational emails under 120 words."

---

## Segment 6: Reply Simulation & Follow-up Scheduling (3:00 - 3:45)
*   **Visual**: Go to the 'Control Panel' tab. Under 'Simulate Prospect Reply', choose Vercel in the dropdown list and click **Trigger Simulated Reply**. Show that the 'Warm Replies' card increments to 1 and Vercel's stage updates to 'Replied'. Next, click **Execute Follow-up Scheduler Now**. Switch to 'Outreach Queue & Logs' to display the newly generated follow-up draft for Vercel.
*   **Narration**:
    > "To demonstrate automation, let's select Vercel and click 'Trigger Simulated Reply'. Instantly, the dashboard registers a Warm Reply, and follow-ups are halted. For the remaining non-responsive leads, we can trigger the scheduler. Clicking 'Execute Follow-up Scheduler Now' simulates elapsed wait-time, and the system automatically generates and queues a brief, polite follow-up draft referencing our initial outreach."

---

## Segment 7: Workflow Logs & Local Database (3:45 - 4:05)
*   **Visual**: Open a new browser tab to `http://127.0.0.1:8000/logs-view` to display the workflow logs, and highlight lines showing `START NODE` and `COMPLETED NODE` transitions.
*   **Narration**:
    > "Behind the scenes, all operations are logged in workflow.log. Here we see the active node logs and agent transitions as they traverse our LangGraph workflow state machine. All data is backed up persistently in our local SQLite database."

---

## Segment 8: Conclusion (4:05 - 4:20)
*   **Visual**: Load `http://127.0.0.1:8000/demo-closing` to display the beautiful thank-you closing card.
*   **Narration**:
    > "In summary, AmosFlow AI provides a fully autonomous GTM outreach pipeline with stateful LangGraph orchestration, clear operational abstractions, and graceful fallbacks. Thank you for watching the demo!"
