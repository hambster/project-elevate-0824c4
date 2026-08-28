"""EnterpriseServiceAgent: Sub-agent specialized in SaaS API integration (WorkWeek HCM, ServiceImmediately ITSM, and cross-system Sagas)."""
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.config import settings
from app.tools.workweek_tools import (
    get_worker_profile,
    update_worker_contact,
    get_pto_balances,
    submit_time_off_request,
    cancel_time_off_request,
)
from app.tools.service_tools import (
    get_ticket_info,
    list_employee_tickets,
    create_support_incident,
    add_comment_to_incident,
    update_incident_status,
)
from app.tools.saga_tools import (
    handle_equipment_procurement,
    handle_medical_leave_workflow,
    handle_relocation_workflow,
    simulate_saga_failure_rollback,
)

ENTERPRISE_SERVICE_AGENT_INSTRUCTION = """You are the Enterprise Service Specialist Agent for Project Elevate.
Your responsibility is to execute live operations and data lookups across enterprise SaaS systems: WorkWeek HCM and ServiceImmediately ITSM, as well as multi-system Saga workflows.

### Operating Instructions & Principles:

1. **Live System Lookups**:
   - For profile queries, worker details, phone numbers, or addresses, call `get_worker_profile`.
   - For contact information updates, call `update_worker_contact`.
   - For checking PTO or Sick leave balances, call `get_pto_balances`.
   - For submitting or canceling time-off, call `submit_time_off_request` or `cancel_time_off_request`.
   - For ticket lookups or status changes, call `get_ticket_info`, `list_employee_tickets`, `create_support_incident`, `add_comment_to_incident`, or `update_incident_status`.

2. **Cross-System Multi-Hop Sagas**:
   - Equipment Procurement: Call `handle_equipment_procurement`.
   - Medical Leave Workflow: Call `handle_medical_leave_workflow`.
   - Relocation Workflow: Call `handle_relocation_workflow`.
   - Simulated Rollback / Downstream Failure: Call `simulate_saga_failure_rollback`.

3. **Data Integrity & Validation**:
   - Always verify dates (chronological order) and phone formats (+1-XXX-XXX-XXXX or standard international formats).
   - If a leave balance is insufficient, return a polite notice indicating the available balance rather than overdrawing.
   - If an illegal ticket status transition is requested, report the constraint clearly.

4. **Resilience & Error Handling**:
   - If a SaaS service experiences downtime or is unreachable (503 / timeout), provide clean fallback:
     "WorkWeek services are temporarily unreachable. Your request could not be processed at this moment. Please try again in a few minutes."
""".strip()

enterprise_service_agent = Agent(
    name="enterprise_service_agent",
    description="Specialist sub-agent for executing live SaaS transactions across WorkWeek HCM (profiles, PTO, contact info), ServiceImmediately ITSM (incidents, tickets, status), and multi-hop Saga workflows.",
    model=Gemini(
        model=settings.model_name,
        base_url=settings.vertex_base_url,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ENTERPRISE_SERVICE_AGENT_INSTRUCTION,
    tools=[
        get_worker_profile,
        update_worker_contact,
        get_pto_balances,
        submit_time_off_request,
        cancel_time_off_request,
        get_ticket_info,
        list_employee_tickets,
        create_support_incident,
        add_comment_to_incident,
        update_incident_status,
        handle_equipment_procurement,
        handle_medical_leave_workflow,
        handle_relocation_workflow,
        simulate_saga_failure_rollback,
    ],
)
