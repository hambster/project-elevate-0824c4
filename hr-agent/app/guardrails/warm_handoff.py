"""Human Warm-Handoff protocol for automated escalation."""
from typing import Any, Dict
from app.clients.service_client import ServiceImmediatelyClient


async def trigger_warm_handoff(
    service_client: ServiceImmediatelyClient,
    employee_id: str,
    reason: str,
    category: str = "AI Service Escalation",
) -> Dict[str, Any]:
    """Create an escalation incident and return a warm-handoff card payload."""
    short_desc = f"AI Service Escalation for {employee_id}: {reason[:60]}"
    res = await service_client.create_ticket(
        requested_by=employee_id,
        category=category,
        short_description=short_desc,
        priority="2 - High",
        assignment_group="HR Direct Support",
        detailed_description=f"Automated Human Handoff triggered.\nReason: {reason}",
    )
    ticket_id = res.get("ticket_id", "INC999999")
    return {
        "status": "ESCALATED",
        "ticket_id": ticket_id,
        "message": f"An AI Service Escalation support ticket has been created (#{ticket_id}) and dispatched to HR/IT operations. A human representative will reach out to assist you shortly.",
        "redirect_url": f"https://support.example.com/tickets/{ticket_id}",
    }
