# PROJECT ELEVATE: ENTERPRISE AI AGENT IMPLEMENTATION PLAN
**Authoritative Technical Implementation Blueprint for HR Agentic Solution (MVP 1)**  
**Document Version:** 2.1.0  
**Aligned Specs:** `HRAgenticSolutionBRD.md` & `SDD.MD`  
**Target Architecture:** Google Agent Development Kit (ADK) Multi-Agent System on Google Cloud Run  

---

## 1. Executive Summary & Architecture Foundation

The **HR Agentic Solution (Project Elevate MVP 1)** is an enterprise conversational AI assistant designed to deflect $\ge 40\%$ of routine Tier 1 HR/IT inquiries and automate core employee self-service workflows across **WorkWeek HCM**, **ServiceImmediately ITSM**, and a curated **HR Policy Document Repository**.

This implementation plan translates all business, functional, and non-functional requirements from `HRAgenticSolutionBRD.md` and `SDD.MD` into concrete, testable Python code modules, tool contracts, guardrails, and automated evaluation harnesses built on the **Google Agent Development Kit (ADK)** and deployed on **Google Cloud Run**.

```
                                  ┌────────────────────────┐
                                  │      Web Chat UI       │
                                  │ (ADK Web / Component)  │
                                  └───────────┬────────────┘
                                              │ HTTPS / WAF (Cloud Armor)
                                              ▼
                                  ┌────────────────────────┐
                                  │    Cloud Run Ingress   │
                                  │   API Gateway (FastAPI)│
                                  └───────────┬────────────┘
                                              │ OIDC JWT Auth + Scoped Delegation (FR-3.1, FR-1.2)
                                              ▼
                         ┌──────────────────────────────────────────┐
                         │   Pre-Execution Safety Pipeline (<150ms) │
                         │   - Model Armor Prompt Injection / Jailbreak  │
                         │   - Domain Containment (Reject non-HR)   │
                         │   - Ephemeral Input SPII Masking (DLP)   │
                         └────────────────────┬─────────────────────┘
                                              │ Sanitized Query + Authenticated User Context
                                              ▼
                         ┌──────────────────────────────────────────┐
                         │   Root Supervisor Agent (Google ADK)     │
                         │      Model: Gemini 2.5 / 3.0 Flash        │
                         │  - NLU, Multi-Turn State & Routing       │
                         │  - Saga Transaction Coordinator (UC-2.x) │
                         └──────┬─────────────┼─────────────┬───────┘
                                │             │             │
                 ┌──────────────┘             │             └──────────────┐
                 ▼                            ▼                            ▼
   ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
   │       Policy Agent       │ │      WorkWeek Agent      │ │ServiceImmediately Agent│
   │  - Vertex AI Search RAG  │ │  - Profile & Leave Read  │ │  - Incident Status/Read│
   │  - Strict Grounding Mode │ │  - Contact & Leave Write │ │  - Incident Create/Post│
   │  - Clickable Citations   │ │  - Real-Time Live Fetch  │ │  - Status Transitions  │
   └─────────────┬────────────┘ └─────────────┬────────────┘ └─────────────┬────────────┘
                 │                            │                            │
                 │ Search Client SDK (gRPC)   │ FastMCP (JSON-RPC 2.0/SSE) │ FastMCP (JSON-RPC 2.0/SSE)
                 ▼                            ▼                            ▼
   ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
   │ Vertex AI Search Engine  │ │  WorkWeek HCM MCP Server │ │ServiceImmediately Server │
   │ (HR Document Data Store) │ │ (Cloud Run / Mock / API) │ │ (Cloud Run / Mock / API) │
   └──────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘
                 │                            │                            │
                 └────────────────────────────┼────────────────────────────┘
                                              │ Raw Execution Payloads
                                              ▼
                         ┌──────────────────────────────────────────┐
                         │  Post-Execution Safety Pipeline (<150ms) │
                         │   - Vertex AI Grounding Verifier (>0.85) │
                         │   - Deterministic Entity & ID Validator  │
                         │   - Citation Integrity & Deep Link Check │
                         │   - Async Cloud DLP Masking -> BigQuery  │
                         └────────────────────┬─────────────────────┘
                                              │ Verified Response Stream
                                              ▼
                                  ┌────────────────────────┐
                                  │   Client Chat Stream   │
                                  └────────────────────────┘
```

---

## 2. Business Requirements Traceability Matrix (RTM)

| BRD Requirement ID | Requirement Name | Architecture & Code Implementation Mapping | Target Validation Suite |
|---|---|---|---|
| **FR-1.1** | Capability & Lifecycle Governance | `elevate_agent/agent.py` restricts callable tools to explicit MCP tool registry; blocks unauthorized actions. | `tests/unit/test_agent_governance.py` |
| **FR-1.2** | Verification of Request Origin | `identity/jwt_extractor.py` & `telemetry/bq_audit_sink.py` tag all actions with `origin: "AUTOMATION"` vs `"USER"`. | `tests/unit/test_audit_origin.py` |
| **FR-1.3** | Conversation Safety (Input/Output) | `guardrails/model_armor.py` (injection/jailbreak) & `guardrails/domain_containment.py` (reject non-HR). | `tests/unit/test_guardrails.py` & Adversarial Eval |
| **FR-1.4** | Data Masking / Redaction | `guardrails/dlp_sanitizer.py` dynamically masks SPII (national IDs, addresses, phones) before logging. | `tests/unit/test_dlp_masking.py` |
| **FR-1.5** | RBAC & Data Isolation | Scopes all queries to caller's `employee_id` via context injection (`_meta.user_id`); blocks cross-user reads. | `tests/unit/test_identity_isolation.py` |
| **FR-2.1** | NLU & Typo Robustness | Google ADK with Gemini 2.5/3.0 Flash prompt engineering with few-shot routing examples. | `eval/evalset.json` (Tier 2/3) |
| **FR-2.2** | Multi-Turn Dialog | `identity/session_store.py` manages ephemeral conversation state in Redis/Firestore with 24h TTL; zero cross-user cache. | `tests/integration/test_multi_turn.py` |
| **FR-3.1** | Delegated Authorization | `identity/jwt_extractor.py` decodes OIDC token and injects signed user claim into MCP transport headers. | `tests/integration/test_workweek_auth.py` |
| **FR-3.2** | WorkWeek Core Actions | `mcp_clients/workweek_client.py` implements profile read, contact update, leave balances query, and leave submission. | `tests/integration/test_single_domain_hcm.py` |
| **FR-3.3** | WorkWeek Operation Guardrails | `guardrails/business_rules.py` validates accrual balance, date chronology (end $\ge$ start, future dates), and phone regex. | `tests/unit/test_workweek_guardrails.py` |
| **FR-3.4** | Real-Time Data Fetch | Sub-agent invokes live MCP tool on every query; strictly no persistent caching of employee profile/PTO in AI layer. | `tests/unit/test_no_caching.py` |
| **FR-4.1** | Auditable Ticket Creation | MCP tool `create_incident` logs caller ID, category, priority, and verified automation source flag. | `tests/integration/test_itsm_audit.py` |
| **FR-4.2** | ServiceImmediately Actions | `mcp_clients/service_client.py` implements ticket details query, incident creation, comment posting, and status update. | `tests/integration/test_single_domain_itsm.py` |
| **FR-4.3** | ITSM Operation Guardrails | Enforces lifecycle transitions (no `New` $\to$ `Closed`), duplicate ticket deduplication, and priority validation. | `tests/unit/test_itsm_guardrails.py` |
| **FR-5.1** | Policy Document Ingestion | Cloud Run event-driven ingestion worker indexing GCS PDF/Text policies into Vertex AI Search with metadata. | `tests/integration/test_ingestion_pipeline.py` |
| **FR-5.2** | Grounded Answers | System prompt grounding + `guardrails/grounding_verifier.py` enforcing $\ge 0.85$ confidence score. | `eval/run_evals.py` (Policy RAG Benchmark) |
| **FR-5.3** | Source Citation | `subagents/policy_agent.py` generates structured citations with document title, section, and deep-link URL. | `tests/unit/test_citations.py` |
| **FR-5.4** | Policy Retrieval Guardrails | Strict grounding fallback if context is missing; domain containment blocks off-topic coding/general queries. | `tests/unit/test_policy_guardrails.py` |
| **FR-5.5** | Document Sync Latency | GCS Pub/Sub notifications trigger index updates in $<5$ minutes; nightly reconciliation at 02:00 UTC. | `deploy/terraform/pubsub_ingestion.tf` |
| **UC-1.1** | Single-Domain: Policy Q&A | Policy Agent queries Vertex AI Search and returns grounded answer with deep link citation. | `tests/integration/test_policy_rag.py` |
| **UC-1.2** | Single-Domain: WorkWeek | WorkWeek Agent reads profile/PTO balances or submits PTO with balance checks. | `tests/integration/test_single_domain_hcm.py` |
| **UC-1.3** | Single-Domain: ITSM | ServiceImmediately Agent queries ticket status, posts comments, or creates incidents. | `tests/integration/test_single_domain_itsm.py` |
| **UC-2.1** | Cross-System: Equipment | Policy check $\to$ WorkWeek remote status verify $\to$ ServiceImmediately hardware loaner ticket creation. | `tests/integration/test_cross_system_saga.py` |
| **UC-2.2** | Cross-System: Medical Leave | Policy check $\to$ WorkWeek Leave of Absence submit $\to$ ServiceImmediately email routing ticket creation. | `tests/integration/test_cross_system_saga.py` |
| **UC-2.3** | Cross-System: Relocation | Policy check $\to$ WorkWeek address update $\to$ ServiceImmediately facilities badge ticket creation. | `tests/integration/test_cross_system_saga.py` |
| **NFR-1.1** | AI Interaction Safety | Pre/post safety pipelines intercept malicious prompt injection, toxic outputs, and unauthorized system access. | `eval/run_evals.py` (Red Team Suite) |
| **NFR-1.2** | 100% Audit Logging | `telemetry/bq_audit_sink.py` records every conversation turn, tool call, denied attempt, latency, and masked payload. | `tests/unit/test_audit_sink.py` |
| **NFR-2.1** | Latency Performance | Total response start $<10.0\text{s}$; Safety scanning overhead $<300\text{ms}$ per turn. | Load testing with Cloud Trace profiling |
| **NFR-2.2** | 99.9% Availability | Cloud Run serverless auto-scaling (min 5 instances, max 200) with multi-zone resilience. | Cloud Monitoring SLA dashboard |
| **NFR-2.3** | Async Processing | Background worker pools for Cloud DLP and BigQuery audit streaming; SSE streaming for chat responses. | `elevate_agent/gateway/routes.py` |
| **NFR-3.1** | >95% Policy Accuracy | Stratified golden dataset evaluation achieving $\ge 95\%$ accuracy and $0\%$ hallucination rate. | `eval/run_evals.py` |
| **NFR-4.1** | Graceful Failure Handling | Non-technical fallback messages; absolute suppression of stack traces and internal error codes. | `tests/unit/test_error_handlers.py` |
| **NFR-4.2** | Transient Fault Tolerance | Client connection pool implements exponential backoff retry (3 attempts: 500ms, 1.5s, 3.0s) and circuit breaker. | `tests/unit/test_mcp_client_pool.py` |
| **NFR-4.3** | Saga Consistency & Rollback | Automated compensating actions (`cancel_leave_request`, incident notes) on multi-hop step failure. | `tests/integration/test_cross_system_saga.py` |

---

## 3. WorkWeek HCM API & MCP Server Specification

### 3.1 Underlying WorkWeek REST Endpoints (Wrapped by FastMCP)

| HTTP Method | REST Endpoint | Description | Request Payload / Params | Response Payload / Status |
|---|---|---|---|---|
| `GET` | `/api/v1/workers/{employee_id}` | Retrieve employee profile and contact info | Headers: `Authorization: Bearer <token>` | `200 OK`: `EmployeeProfile` JSON<br>`404 Not Found`: Worker does not exist |
| `PATCH` | `/api/v1/workers/{employee_id}/contact` | Update personal home address & phone | `{"personal_address": "...", "personal_phone": "+65..."}` | `200 OK`: Updated contact record<br>`422 Unprocessable`: Invalid phone format |
| `GET` | `/api/v1/workers/{employee_id}/time_off/balances` | Retrieve real-time Vacation & Sick balances | Query: `leave_type` (optional) | `200 OK`: `List[LeaveBalance]`<br>`401 Unauthorized` |
| `POST` | `/api/v1/workers/{employee_id}/time_off/requests` | Submit PTO / Sick Leave request | `{"leave_type": "Vacation", "start_date": "2026-09-01", "end_date": "2026-09-05", "work_days": 5, "reason": "..."}` | `201 Created`: `{"request_id": "WW-REQ-9921", "status": "SUBMITTED"}`<br>`409 Conflict`: Insufficient balance |
| `POST` | `/api/v1/workers/{employee_id}/time_off/requests/{request_id}/cancel` | Cancel pending or approved leave request | `{"cancellation_reason": "Rollback due to downstream ticket failure"}` | `200 OK`: `{"request_id": "WW-REQ-9921", "status": "CANCELLED"}`<br>`404 Not Found` |

### 3.2 FastMCP Tool Declarations for WorkWeek (`elevate_agent/mcp_clients/workweek_client.py`)

```python
"""WorkWeek FastMCP Client Tools for Google ADK Agent Integration."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from elevate_agent.mcp_clients.client_pool import get_mcp_client

class WorkWeekClient:
    def __init__(self, mcp_server_url: str):
        self.client = get_mcp_client("workweek", mcp_server_url)

    async def get_employee_profile(self, employee_id: str) -> Dict[str, Any]:
        """Fetch worker metadata, location, role, and manager details.
        
        Args:
            employee_id: Authenticated WorkWeek Employee ID (e.g. WW-10928).
        """
        return await self.client.call_tool("get_employee_profile", {"employee_id": employee_id})

    async def update_contact_info(
        self, 
        employee_id: str, 
        personal_address: Optional[str] = None, 
        personal_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update personal home address and/or phone number in WorkWeek.
        
        Args:
            employee_id: Authenticated Employee ID.
            personal_address: Formatted street address.
            personal_phone: E.164 compliant phone number string.
        """
        return await self.client.call_tool("update_contact_info", {
            "employee_id": employee_id,
            "personal_address": personal_address,
            "personal_phone": personal_phone
        })

    async def get_leave_balances(self, employee_id: str, leave_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve real-time accrued, used, and remaining hours for Vacation and Sick leave.
        
        Args:
            employee_id: Authenticated Employee ID.
            leave_type: Optional filter ('Vacation' or 'Sick').
        """
        return await self.client.call_tool("get_leave_balances", {
            "employee_id": employee_id,
            "leave_type": leave_type
        })

    async def submit_leave_request(
        self, 
        employee_id: str, 
        leave_type: str, 
        start_date: str, 
        end_date: str, 
        work_days: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a formal PTO or Sick Leave request in WorkWeek.
        
        Args:
            employee_id: Authenticated Employee ID.
            leave_type: 'Vacation' | 'Sick' | 'Parental' | 'Unpaid'.
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).
            work_days: Number of working days requested.
            reason: Optional explanation note.
        """
        return await self.client.call_tool("submit_leave_request", {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "work_days": work_days,
            "reason": reason
        })

    async def cancel_leave_request(self, employee_id: str, request_id: str, reason: str) -> Dict[str, Any]:
        """Saga Compensation Action: Cancel a previously submitted leave request."""
        return await self.client.call_tool("cancel_leave_request", {
            "employee_id": employee_id,
            "request_id": request_id,
            "reason": reason
        })
```

---

## 4. ServiceImmediately ITSM API & MCP Server Specification

### 4.1 Underlying ServiceImmediately REST Table Endpoints (Wrapped by FastMCP)

| HTTP Method | REST Endpoint | Description | Request Payload / Params | Response Payload / Status |
|---|---|---|---|---|
| `GET` | `/api/v1/table/incident/{ticket_id}` | Retrieve incident details, status, priority, and timeline | Format: `INC\d{6}` | `200 OK`: `IncidentTicket` JSON<br>`404 Not Found`: Ticket does not exist |
| `POST` | `/api/v1/table/incident` | Create a new IT incident or hardware request | `{"caller_id": "sys_usr_...", "short_description": "...", "detailed_description": "...", "category": "Hardware", "priority": "2 - High", "origin": "AUTOMATION"}` | `201 Created`: `{"ticket_id": "INC009124", "status": "New", "created_at": "..."}`<br>`400 Bad Request` |
| `POST` | `/api/v1/table/incident/{ticket_id}/comments` | Append note/comment to ticket activity stream | `{"author_id": "WW-10928", "author_type": "AUTOMATION", "content": "..."}` | `201 Created`: `{"comment_id": "CMT-441", "timestamp": "..."}` |
| `PATCH` | `/api/v1/table/incident/{ticket_id}` | Transition lifecycle status (e.g. to 'Resolved') | `{"status": "Resolved", "resolution_notes": "..."}` | `200 OK`: Updated incident record<br>`422 Unprocessable`: Invalid lifecycle transition |

### 4.2 FastMCP Tool Declarations for ServiceImmediately (`elevate_agent/mcp_clients/service_client.py`)

```python
"""ServiceImmediately FastMCP Client Tools for Google ADK Agent Integration."""
from typing import Optional, Dict, Any, List
from elevate_agent.mcp_clients.client_pool import get_mcp_client

class ServiceImmediatelyClient:
    def __init__(self, mcp_server_url: str):
        self.client = get_mcp_client("service_immediately", mcp_server_url)

    async def get_ticket_details(self, ticket_id: str) -> Dict[str, Any]:
        """Fetch status, category, priority, assignee, and comments for an incident ticket.
        
        Args:
            ticket_id: Incident ID formatted as INC followed by 6 digits (e.g. INC009124).
        """
        return await self.client.call_tool("get_ticket_details", {"ticket_id": ticket_id})

    async def create_incident(
        self,
        caller_id: str,
        category: str,
        priority: str,
        short_description: str,
        detailed_description: str
    ) -> Dict[str, Any]:
        """Open a new IT support incident, hardware procurement, or badge access ticket.
        
        Args:
            caller_id: Authenticated user's ServiceImmediately caller/sys_id.
            category: 'Hardware' | 'Software' | 'Access' | 'General_HRSD'.
            priority: '1 - Critical' | '2 - High' | '3 - Moderate' | '4 - Low'.
            short_description: Brief summary title of the request.
            detailed_description: Full specification, shipping address, or error details.
        """
        return await self.client.call_tool("create_incident", {
            "caller_id": caller_id,
            "category": category,
            "priority": priority,
            "short_description": short_description,
            "detailed_description": detailed_description,
            "author_type": "AUTOMATION"
        })

    async def post_ticket_comment(
        self,
        ticket_id: str,
        author_id: str,
        comment: str,
        author_type: str = "AUTOMATION"
    ) -> Dict[str, Any]:
        """Append an update note or comment to an active incident ticket timeline."""
        return await self.client.call_tool("post_ticket_comment", {
            "ticket_id": ticket_id,
            "author_id": author_id,
            "author_type": author_type,
            "comment": comment
        })

    async def update_ticket_status(
        self,
        ticket_id: str,
        new_status: str,
        resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transition incident state (e.g. In Progress -> Resolved -> Closed).
        
        Args:
            ticket_id: Ticket ID (INCxxxxxx).
            new_status: 'In Progress' | 'On Hold' | 'Resolved' | 'Closed'.
            resolution_notes: Required if transitioning to 'Resolved' or 'Closed'.
        """
        return await self.client.call_tool("update_ticket_status", {
            "ticket_id": ticket_id,
            "new_status": new_status,
            "resolution_notes": resolution_notes
        })
```

---

## 5. Agent-to-API Integration Architecture & Middleware

### 5.1 Connection Pooling & Resilience Protocol (`elevate_agent/mcp_clients/client_pool.py`)

The ADK sub-agents connect to the containerized FastMCP servers over persistent HTTP/Server-Sent Events (SSE) connections managed by a thread-safe connection pool:

```python
"""MCP Client Connection Pool with Exponential Backoff, Timeout, and Circuit Breaking."""
import httpx
import asyncio
from typing import Dict, Any

class FastMCPClientPool:
    def __init__(self, base_url: str, timeout_seconds: float = 4.0):
        self.base_url = base_url
        self.timeout = timeout_seconds
        self.consecutive_failures = 0
        self.circuit_open = False

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], context_meta: Dict[str, Any]) -> Dict[str, Any]:
        if self.circuit_open:
            raise RuntimeError(f"Circuit breaker OPEN for {self.base_url}. Service temporarily degraded.")

        headers = {
            "Content-Type": "application/json",
            "X-Authenticated-User-Id": context_meta.get("user_id", ""),
            "X-Origin-Entity": "AUTOMATION-AGENT"
        }
        
        # Exponential backoff retry loop (500ms, 1500ms, 3000ms)
        delays = [0.5, 1.5, 3.0]
        for attempt, delay in enumerate(delays, start=1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/tools/{tool_name}/invoke",
                        json={"arguments": arguments},
                        headers=headers
                    )
                    if response.status_code == 200:
                        self.consecutive_failures = 0
                        return response.json()
                    elif response.status_code in [400, 404, 422, 409]:
                        # Non-transient business rule error -> do not retry
                        return response.json()
                    elif response.status_code in [429, 502, 503, 504]:
                        await asyncio.sleep(delay)
            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt == len(delays):
                    self.consecutive_failures += 1
                    if self.consecutive_failures >= 5:
                        self.circuit_open = True
                    raise TimeoutError(f"Tool {tool_name} timed out after {self.timeout}s across {len(delays)} retries.")
                await asyncio.sleep(delay)
```

### 5.2 Error Code Mapping to Conversational Fallbacks (NFR-4.1)

To strictly enforce **NFR-4.1** (suppression of technical error codes and stack traces), the API Gateway and Agent Handlers map backend status codes to user-friendly conversational guidance:

| Backend Status / Failure Mode | Root Cause Detection | Conversational User Fallback Message |
|---|---|---|
| `HTTP 409 Conflict` (WorkWeek) | Accrual balance exceeded ($> \text{remaining\_hours}$) | *"You requested 24 hours of PTO, but your available Vacation balance is 16 hours. Would you like to submit a request for 16 hours instead?"* |
| `HTTP 422 Unprocessable` (WorkWeek) | End date precedes start date or past date | *"The requested leave end date cannot be earlier than the start date. Please provide valid dates for your time-off request."* |
| `HTTP 422 Unprocessable` (WorkWeek) | Phone number fails E.164 regex format | *"The phone number format provided is invalid. Please provide a standard international phone number (e.g. +65 9123 4567)."* |
| `HTTP 422 Unprocessable` (ITSM) | Invalid transition (e.g. `New` $\to$ `Closed`) | *"Ticket INC008912 is currently in 'In Progress' status and cannot be closed directly without resolution notes. Would you like to add a comment instead?"* |
| `HTTP 409 Conflict` (ITSM) | Duplicate ticket submitted within 5 minutes | *"A similar ticket (#INC009110) was recently created for this issue. I have added your update as a comment to that ticket rather than opening a duplicate."* |
| `HTTP 503 / Timeout` (WorkWeek) | WorkWeek service unavailable after 3 retries | *"WorkWeek services are temporarily unreachable. Your request could not be processed at this moment. Please try again in a few minutes."* |
| `HTTP 503 / Timeout` (ITSM) | ServiceImmediately unavailable after 3 retries | *"ServiceImmediately support desk is currently experiencing a delay. Your ticket details could not be retrieved right now."* |
| `Grounding < 0.85` (Vertex AI) | Insufficient or unindexed policy content | *"I could not find an authoritative answer to this question in our approved HR policy documents. Please contact the HR Direct support desk for assistance."* |

---

## 6. Directory Structure & Key Package Files

```
project-elevate-0824c4/
├── SDD.MD                               # Solution Design Document (Reference Architecture)
├── HRAgenticSolutionBRD.md              # Business Requirements Document (Source Spec)
├── IMPLEMENTATION_PLAN.md               # Authoritative Implementation Guide
├── pyproject.toml                       # Python dependencies (ADK, FastAPI, Pydantic, FastMCP)
├── Dockerfile                           # Multi-stage production container build
├── Makefile                             # Automation commands (setup, test, lint, eval, run)
├── .env.example                         # Environment configuration template
│
├── elevate_agent/                       # Core Python Package
│   ├── __init__.py
│   ├── config.py                        # Pydantic BaseSettings (GCP Project, Model, IAM, Secret Mgr)
│   ├── agent.py                         # Root Supervisor Agent (Google ADK Router)
│   │
│   ├── models/                          # Pydantic Schemas & Domain Entities
│   │   ├── __init__.py
│   │   ├── employee.py                  # EmployeeProfile, ContactInfoUpdate
│   │   ├── leave.py                     # LeaveBalance, LeaveRequest, LeaveType
│   │   ├── incident.py                  # IncidentTicket, IncidentPriority, TicketStatus
│   │   ├── policy.py                    # PolicyQuery, PolicyCitation, GroundingMetadata
│   │   └── session.py                   # UserSessionContext, SessionState, ActiveSaga
│   │
│   ├── subagents/                       # Specialized Persona Agents (ADK Sub-Agents)
│   │   ├── __init__.py
│   │   ├── policy_agent.py              # Vertex AI Search RAG Specialist
│   │   ├── workweek_agent.py            # WorkWeek HCM Specialist (Profile, PTO, Contact)
│   │   └── service_agent.py             # ServiceImmediately ITSM Specialist (Incidents, Comments)
│   │
│   ├── saga/                            # Cross-System Multi-Hop Orchestration (UC-2.x)
│   │   ├── __init__.py
│   │   ├── coordinator.py               # Distributed Saga State Machine & Runner
│   │   ├── states.py                    # Saga Transaction Lifecycle Enums & Models
│   │   └── compensations.py             # Automated Rollback & Compensating Actions
│   │
│   ├── mcp_clients/                     # MCP Connectors & Client Pool
│   │   ├── __init__.py
│   │   ├── client_pool.py               # FastMCP Client Session Pool (JSON-RPC over HTTP/SSE)
│   │   ├── workweek_client.py           # Typed Tool Wrappers for WorkWeek HCM
│   │   └── service_client.py            # Typed Tool Wrappers for ServiceImmediately ITSM
│   │
│   ├── guardrails/                      # Pre & Post Safety, DLP & Validation Middleware
│   │   ├── __init__.py
│   │   ├── model_armor.py               # Pre-Execution Prompt Injection / Jailbreak Filter (<150ms)
│   │   ├── domain_containment.py        # Out-of-Scope Intent Filter (Reject non-HR queries)
│   │   ├── business_rules.py            # WorkWeek & ITSM Transaction Constraints (FR-3.3, FR-4.3)
│   │   ├── grounding_verifier.py        # Vertex RAG Grounding Evaluator (Confidence >= 0.85)
│   │   ├── dlp_sanitizer.py             # Cloud DLP / Regex Ephemeral SPII Masker
│   │   └── hallucination_checker.py     # Heuristic Entity & ID Deterministic Validator
│   │
│   ├── identity/                        # Identity Delegation & Context Propagation
│   │   ├── __init__.py
│   │   ├── jwt_extractor.py             # OIDC JWT Claims Decoder & Signature Validator
│   │   ├── identity_translator.py       # Claims to Backend System IDs (WW & ServiceNow)
│   │   └── session_store.py             # Ephemeral Session Store (Redis / MemoryStore / Firestore)
│   │
│   ├── gateway/                         # Ingress API Gateway (FastAPI / Cloud Run)
│   │   ├── __init__.py
│   │   ├── app.py                       # FastAPI Application Factory & Lifespan
│   │   ├── routes.py                    # REST / SSE Endpoints (/api/v1/chat/stream, /health)
│   │   └── error_handlers.py            # Non-technical Fallbacks & Warm-Handoff Cards
│   │
│   └── telemetry/                       # Observability, Audit Logging & Tracing
│       ├── __init__.py
│       ├── bq_audit_sink.py             # Async Cloud Logging -> BigQuery Audit Sink (NFR-1.2)
│       └── tracer.py                    # OpenTelemetry / Cloud Trace Integration
│
├── mock_servers/                        # Containerized FastMCP Mock Backends for Local/CI Testing
│   ├── workweek_mcp/
│   │   ├── __init__.py
│   │   ├── server.py                    # FastMCP Server (Profile, Leave, Contact Updates)
│   │   └── data_store.py                # In-Memory Seeded Employee & Leave DB
│   └── service_immediately_mcp/
│       ├── __init__.py
│       ├── server.py                    # FastMCP Server (Incidents, Comments, Status Transitions)
│       └── ticket_store.py              # In-Memory Seeded ITSM Ticket DB
│
├── tests/                               # Comprehensive Automated Test Suites
│   ├── unit/
│   │   ├── test_guardrails.py           # Model Armor, Domain Containment, Business Rules
│   │   ├── test_saga_coordinator.py     # State transitions & Compensation logic
│   │   ├── test_identity_translation.py # JWT decoding & Scoped delegation
│   │   └── test_tools.py                # Parameter validation & tool signatures
│   ├── integration/
│   │   ├── test_policy_rag.py           # Vertex AI Search & Citations (UC-1.1)
│   │   ├── test_single_domain_hcm.py    # WorkWeek Profile & PTO (UC-1.2)
│   │   ├── test_single_domain_itsm.py   # ServiceImmediately Incidents (UC-1.3)
│   │   └── test_cross_system_saga.py    # Multi-Hop Sagas (UC-2.1, UC-2.2, UC-2.3)
│   └── e2e/
│       ├── test_gateway_stream.py       # Full SSE stream round-trip
│       └── test_warm_handoff.py         # Warm-handoff card generation on failure
│
├── eval/                                # 4-Tier Stratified Golden Evaluation Suite
│   ├── evalset.json                     # Ground Truth Golden Dataset (100+ stratified cases)
│   ├── eval_config.json                 # ADK / Agent Platform Evaluation Config
│   └── run_evals.py                     # Quantitative Benchmark Test Runner & Rubric Assertion
│
└── deploy/                              # Infrastructure as Code & CI/CD
    ├── terraform/                       # GCP Infrastructure (Cloud Run, Vertex, Pub/Sub, IAM)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── cloudbuild.yaml                  # Automated Build, Test, Eval & Deploy Pipeline
```

---

## 7. FastMCP Mock Server Implementations (`mock_servers/`)

### 7.1 WorkWeek Mock FastMCP Server (`mock_servers/workweek_mcp/server.py`)
```python
"""Containerized WorkWeek Mock FastMCP Server for Local & CI Testing."""
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
from mock_servers.workweek_mcp.data_store import (
    EMPLOYEE_DB, LEAVE_BALANCE_DB, LEAVE_REQUEST_DB
)

mcp = FastMCP("WorkWeek-HCM-Mock", host="0.0.0.0", port=8081)

@mcp.tool()
def get_employee_profile(employee_id: str) -> Dict[str, Any]:
    """Retrieve full employee profile including manager, role, address, and phone."""
    if employee_id not in EMPLOYEE_DB:
        raise ValueError(f"Worker {employee_id} not found in WorkWeek database.")
    return EMPLOYEE_DB[employee_id]

@mcp.tool()
def update_contact_info(
    employee_id: str, 
    personal_address: Optional[str] = None, 
    personal_phone: Optional[str] = None
) -> Dict[str, Any]:
    """Update employee personal address and/or phone number."""
    if employee_id not in EMPLOYEE_DB:
        raise ValueError(f"Worker {employee_id} not found.")
    record = EMPLOYEE_DB[employee_id]
    if personal_address:
        record["home_address"] = personal_address
    if personal_phone:
        record["phone_number"] = personal_phone
    return {"status": "SUCCESS", "updated_record": record}

@mcp.tool()
def get_leave_balances(employee_id: str, leave_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve Vacation and Sick leave accruals, used hours, and remaining balances."""
    if employee_id not in LEAVE_BALANCE_DB:
        raise ValueError(f"No leave balances found for worker {employee_id}.")
    balances = LEAVE_BALANCE_DB[employee_id]
    if leave_type:
        balances = [b for b in balances if b["leave_type"].lower() == leave_type.lower()]
    return balances

@mcp.tool()
def submit_leave_request(
    employee_id: str, 
    leave_type: str, 
    start_date: str, 
    end_date: str, 
    work_days: int,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """Submit PTO / Sick leave with balance constraints and chronological check."""
    balances = {b["leave_type"]: b for b in LEAVE_BALANCE_DB.get(employee_id, [])}
    if leave_type not in balances:
        raise ValueError(f"Invalid leave category {leave_type}.")
    
    available_hours = balances[leave_type]["remaining_hours"]
    requested_hours = work_days * 8.0
    if requested_hours > available_hours:
        raise ValueError(
            f"Insufficient leave balance. Requested {requested_hours}h, but available balance is {available_hours}h."
        )
    
    req_id = f"WW-REQ-{len(LEAVE_REQUEST_DB) + 1001}"
    req_record = {
        "request_id": req_id,
        "employee_id": employee_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "work_days": work_days,
        "status": "SUBMITTED"
    }
    LEAVE_REQUEST_DB[req_id] = req_record
    balances[leave_type]["remaining_hours"] -= requested_hours
    balances[leave_type]["used_hours"] += requested_hours
    return {"status": "SUCCESS", "request_id": req_id, "details": req_record}

@mcp.tool()
def cancel_leave_request(employee_id: str, request_id: str, reason: str) -> Dict[str, Any]:
    """Compensating action: Rollback a submitted leave request."""
    if request_id not in LEAVE_REQUEST_DB:
        raise ValueError(f"Request {request_id} does not exist.")
    record = LEAVE_REQUEST_DB[request_id]
    if record["employee_id"] != employee_id:
        raise ValueError("Unauthorized cancellation attempt.")
    record["status"] = "CANCELLED"
    record["cancellation_reason"] = reason
    return {"status": "CANCELLED", "request_id": request_id}

if __name__ == "__main__":
    mcp.run()
```

### 7.2 ServiceImmediately Mock FastMCP Server (`mock_servers/service_immediately_mcp/server.py`)
```python
"""Containerized ServiceImmediately Mock FastMCP Server for Local & CI Testing."""
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
from datetime import datetime
from mock_servers.service_immediately_mcp.ticket_store import INCIDENT_DB

mcp = FastMCP("ServiceImmediately-ITSM-Mock", host="0.0.0.0", port=8082)

@mcp.tool()
def get_ticket_details(ticket_id: str) -> Dict[str, Any]:
    """Retrieve ticket status, priority, category, assignee, and comments."""
    if ticket_id not in INCIDENT_DB:
        raise ValueError(f"Ticket {ticket_id} not found in ITSM database.")
    return INCIDENT_DB[ticket_id]

@mcp.tool()
def create_incident(
    caller_id: str,
    category: str,
    priority: str,
    short_description: str,
    detailed_description: str,
    author_type: str = "AUTOMATION"
) -> Dict[str, Any]:
    """Create a support incident or loaner hardware ticket."""
    ticket_id = f"INC{len(INCIDENT_DB) + 100001:06d}"
    incident_record = {
        "ticket_id": ticket_id,
        "caller_id": caller_id,
        "short_description": short_description,
        "detailed_description": detailed_description,
        "category": category,
        "priority": priority,
        "status": "New",
        "assignee": "Unassigned",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "comments": [
            {
                "comment_id": "CMT-001",
                "author_id": caller_id,
                "author_type": author_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "content": f"Ticket automatically opened by Elevate AI Agent: {short_description}"
            }
        ]
    }
    INCIDENT_DB[ticket_id] = incident_record
    return {"status": "SUCCESS", "ticket_id": ticket_id, "details": incident_record}

@mcp.tool()
def post_ticket_comment(ticket_id: str, author_id: str, comment: str, author_type: str = "AUTOMATION") -> Dict[str, Any]:
    """Append notes or updates to the incident timeline."""
    if ticket_id not in INCIDENT_DB:
        raise ValueError(f"Ticket {ticket_id} does not exist.")
    ticket = INCIDENT_DB[ticket_id]
    cmt_id = f"CMT-{len(ticket['comments']) + 1:03d}"
    cmt = {
        "comment_id": cmt_id,
        "author_id": author_id,
        "author_type": author_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "content": comment
    }
    ticket["comments"].append(cmt)
    ticket["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"status": "SUCCESS", "comment_id": cmt_id, "ticket_id": ticket_id}

@mcp.tool()
def update_ticket_status(ticket_id: str, new_status: str, resolution_notes: Optional[str] = None) -> Dict[str, Any]:
    """Transition ticket state with lifecycle constraint validation."""
    if ticket_id not in INCIDENT_DB:
        raise ValueError(f"Ticket {ticket_id} not found.")
    ticket = INCIDENT_DB[ticket_id]
    curr_status = ticket["status"]
    
    # Lifecycle validation rule: Cannot transition directly from New to Closed
    if curr_status == "New" and new_status == "Closed":
        raise ValueError("Invalid transition: Incident in 'New' status cannot transition directly to 'Closed'. Must move to 'In Progress' or 'Resolved'.")
    
    if new_status in ["Resolved", "Closed"] and not resolution_notes:
        raise ValueError("Resolution notes are required when resolving or closing an incident.")
        
    ticket["status"] = new_status
    ticket["updated_at"] = datetime.utcnow().isoformat() + "Z"
    if resolution_notes:
        ticket["resolution_notes"] = resolution_notes
    return {"status": "SUCCESS", "ticket_id": ticket_id, "new_status": new_status}

if __name__ == "__main__":
    mcp.run()
```

---

## 8. Phased Implementation Roadmap & Engineering Sprints

### Phase 1: Environment Setup, Scaffolding & Policy RAG Pipeline (Weeks 1–3)
- **Deliverables:**
  1. Python 3.11 virtual environment configured (`test.env`).
  2. GCP Foundation: Cloud Storage policy bucket (`gs://elevate-hr-policies`), Secret Manager, Pub/Sub ingestion topic, Vertex AI Search Datastore.
  3. Scaffolding of package `elevate_agent` with ADK dependencies.
  4. Implementation of `mock_servers/workweek_mcp` and `mock_servers/service_immediately_mcp` using FastMCP with realistic mock datasets.
  5. Policy Agent implementation querying Vertex AI Search with layout-aware chunking and citation metadata.
- **Verification Command:** `pytest tests/integration/test_policy_rag.py -v`

### Phase 2: Specialized Sub-Agents, Tools & Scoped Identity (Weeks 4–6)
- **Deliverables:**
  1. `identity/jwt_extractor.py` and `identity/identity_translator.py` with memory cache.
  2. Sub-agents: `WorkWeekAgent` and `ServiceImmediatelyAgent` with full tool coverage.
  3. `guardrails/business_rules.py` enforcing leave balance constraints, chronological validation, phone formatting, and ticket transition rules.
  4. Context propagation: inject authenticated `employee_id` and `caller_id` via MCP `_meta` headers.
- **Verification Command:** `pytest tests/integration/test_single_domain_hcm.py tests/integration/test_single_domain_itsm.py -v`

### Phase 3: Root Supervisor, Saga Coordinator & Safety Guardrails (Weeks 7–9)
- **Deliverables:**
  1. `elevate_agent/agent.py` Root Supervisor Agent managing intent classification and sub-agent routing.
  2. `saga/coordinator.py` executing UC-2.1, UC-2.2, and UC-2.3 with automated compensating rollbacks.
  3. Pre-execution safety: `guardrails/model_armor.py` and `guardrails/domain_containment.py`.
  4. Post-execution safety: `guardrails/grounding_verifier.py` (threshold $\ge 0.85$) and deterministic ID checking.
  5. Warm-Handoff Protocol: automated ServiceImmediately escalation ticket and user UI card dispatch.
  6. `telemetry/bq_audit_sink.py` streaming audit logs to BigQuery.
- **Verification Command:** `pytest tests/integration/test_cross_system_saga.py -v`

### Phase 4: Production Hardening, Golden Evaluation & CI/CD (Weeks 10–12)
- **Deliverables:**
  1. 4-Tier Stratified Golden Evaluation Dataset (`eval/evalset.json`) containing 100+ golden test queries.
  2. Benchmark harness `eval/run_evals.py` executing automated LLM-as-a-judge scoring and threshold assertions.
  3. Production multi-stage `Dockerfile` and Cloud Run deployment configuration (min 5, max 200 instances).
  4. Cloud Monitoring dashboards and alerting policies for 5xx errors, latency anomalies, and DLQ events.
  5. Formal UAT sign-off with HR and IT business stakeholders.
- **Verification Command:** `python eval/run_evals.py --evalset eval/evalset.json --config eval/eval_config.json`

---

## 9. Golden Evaluation & Acceptance Criteria Matrix

| Category | Benchmark Metric | Acceptance Threshold | Evaluation Method |
|---|---|---|---|
| **Policy Accuracy** | Precision & Recall on Policy Q&A | $\ge 95\%$ Accuracy; $0\%$ Hallucination | Automated LLM-as-judge on Golden Dataset |
| **Transaction Integrity**| Correctness of HCM & ITSM mutations | $100\%$ Correctness; $0$ data corruption | Automated API assertions against Mock MCP |
| **Cross-System Saga** | Chaining actions across UC-2.x | $100\%$ Pass on all defined scenarios | End-to-end multi-hop simulation |
| **Adversarial Safety** | Prompt injection / jailbreak blocks | $100\%$ Detection; $< 1\%$ False Positives | Red Team Adversarial benchmark suite |
| **Domain Containment** | Rejection of non-HR / off-topic queries | $100\%$ Rejection with standard fallback | Boundary test suite |
| **Response Latency** | Time to start generating response | $< 10.0\text{s}$ average under load | Cloud Trace under 50 concurrent sessions |
| **Safety Overhead** | Latency of pre/post safety checks | $< 300\text{ms}$ overhead per turn | Custom middleware timing instrumentation |
| **Audit Coverage** | Logging of allowed and blocked actions | $100\%$ Logged with origin tags | BigQuery audit table row verification |
| **Resilience** | Graceful degradation on failure | $100\%$ Graceful; $0$ leaked stack traces | Downstream Chaos fault-injection tests |
