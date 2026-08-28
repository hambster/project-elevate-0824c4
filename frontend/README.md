# Decoupled Web Frontend UI Service — HR Agentic Solution (MVP 1)

This is the decoupled web presentation frontend for the HR Agentic Solution (MVP 1). It is designed to run as an independent web service parallel to the `my-agent/` backend agent service.

---

## 🌟 Key Features

1. **Screen 1 — Employee Auth & Delegation Token Login:**
   - Accepts employee tokens (`WW-10928`, `WW-88888`, or custom tokens).
   - Pre-loaded with demo employee test profiles for rapid evaluation.
   - Enforces zero-trust token delegation passed to downstream WorkWeek HCM & ServiceImmediately MCP services via `X-Employee-Token` HTTP headers.

2. **Screen 2 — Interactive Conversational Assistant Workspace:**
   - Polished glassmorphic dark/light UI design.
   - **Quick Action Prompt Chips:** 1-click execution for standard use cases (PTO balance check, leave submission, UC-2.1 equipment procurement, UC-2.2 medical leave, UC-2.3 relocation, ticket status check).
   - **Markdown & Citations:** Renders formatted answers with clickable links to authoritative policy URLs.
   - **Security Metadata:** Displays Model Armor gate and Cloud DLP redaction status.
   - **Human Warm-Handoff Escalation Cards:** Renders escalation cards with ticket reference IDs, SLA timers, and live chat links when escalation is triggered.

---

## 🚀 Running the Frontend Service

### Step 1: Install Dependencies
```bash
pip install -e .
```

### Step 2: Start Frontend Server
```bash
python app.py
```
The frontend service will start at `http://localhost:8080`.

### Step 3: Decoupled Backend Architecture
By default, the frontend forwards chat requests to the backend agent running at `http://localhost:8000/api/chat`.
To change the backend URL:
```bash
export BACKEND_AGENT_URL="https://my-backend-agent.cloudrun.app/api/chat"
python app.py
```
