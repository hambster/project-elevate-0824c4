"""ServiceImmediately ITSM tools for Google ADK Agent."""
import asyncio
from typing import Optional
from app.clients.service_client import ServiceImmediatelyClient
from app.clients.workweek_client import WorkWeekClient
from app.guardrails.business_rules import validate_ticket_id_format

_service_client = ServiceImmediatelyClient()
_ww_client = WorkWeekClient()


def get_ticket_info(ticket_id: str) -> str:
    """Fetch status, category, priority, assignee, and timeline for an incident ticket in ServiceImmediately.
    
    Args:
        ticket_id: Ticket ID (e.g. INC0003310, INC123456).
    """
    employee_id = asyncio.run(_ww_client.get_current_employee_id())
    res = asyncio.run(_service_client.get_ticket_details(ticket_id, employee_id=employee_id))
    if "error" in res:
        return res["error"]
    if "raw_text" in res:
        return res["raw_text"]

    comments_str = ""
    if res.get("comments"):
        comments_str = "\nComments:\n" + "\n".join([f"- [{c.get('timestamp', '')}] {c.get('author_id', '')}: {c.get('content', '')}" for c in res["comments"]])

    return (
        f"Ticket {res.get('ticket_id')}:\n"
        f"Status: {res.get('status')}\n"
        f"Category: {res.get('category')}\n"
        f"Priority: {res.get('priority')}\n"
        f"Summary: {res.get('short_description')}\n"
        f"Assignee: {res.get('assigned_to', res.get('assignee', 'Unassigned'))}"
        f"{comments_str}"
    )


def list_employee_tickets(employee_id: str = "") -> str:
    """List all active and past ServiceImmediately support tickets for the employee.
    
    Args:
        employee_id: The employee ID (optional, defaults to current authenticated employee session).
    """
    if not employee_id:
        employee_id = asyncio.run(_ww_client.get_current_employee_id())

    res = asyncio.run(_service_client.list_tickets(employee_id))
    if isinstance(res, list):
        if not res:
            return f"No tickets found for employee {employee_id}."
        lines = [f"Tickets for employee {employee_id}:"]
        for t in res:
            lines.append(f"- #{t.get('ticket_id')}: {t.get('short_description')} (Status: {t.get('status')}, Priority: {t.get('priority')})")
        return "\n".join(lines)
    return str(res)


def create_support_incident(
    requested_by: str = "",
    category: str = "Network / IT",
    short_description: str = "",
    priority: str = "3 - Moderate",
    assignment_group: str = "Service Desk",
    detailed_description: str = "",
) -> str:
    """Open a new IT incident, network trouble ticket, or hardware procurement in ServiceImmediately.
    
    Args:
        requested_by: Authenticated employee ID (optional, defaults to current authenticated employee session).
        category: 'Hardware' | 'Software' | 'Access' | 'General_HRSD' | 'Network / IT' | 'Inquiry / Help'.
        short_description: Summary title of the request.
        priority: '1 - Critical' | '2 - High' | '3 - Moderate' | '4 - Low'.
        assignment_group: 'Service Desk' | 'IT Network Team' | 'Hardware Support' | 'Facilities'.
        detailed_description: Full details, error messages, or shipping instructions.
    """
    if not requested_by:
        requested_by = asyncio.run(_ww_client.get_current_employee_id())

    res = asyncio.run(
        _service_client.create_ticket(
            requested_by=requested_by,
            category=category,
            short_description=short_description,
            priority=priority,
            assignment_group=assignment_group,
            detailed_description=detailed_description or short_description,
        )
    )
    if "error" in res:
        return res["error"]
    return res.get("message", f"Created incident ticket {res.get('ticket_id')}: '{short_description}'.")


def add_comment_to_incident(ticket_id: str, author: str = "", comment: str = "") -> str:
    """Append an update comment to an active incident ticket timeline in ServiceImmediately.
    
    Args:
        ticket_id: Ticket ID (e.g. INC0003310, INC123456).
        author: Author identifier (optional, defaults to current authenticated employee session).
        comment: Note or update text.
    """
    if not author:
        author = asyncio.run(_ww_client.get_current_employee_id())

    res = asyncio.run(_service_client.add_ticket_comment(ticket_id, author, comment))
    if "error" in res:
        return res["error"]
    return res.get("message", f"Successfully added comment to ticket {ticket_id}.")


def update_incident_status(
    ticket_id: str,
    new_status: str,
    resolution_notes: str = "",
) -> str:
    """Transition incident status (e.g. In Progress -> Resolved -> Closed) in ServiceImmediately.
    
    Args:
        ticket_id: Ticket ID (e.g. INC0003310, INC008912).
        new_status: 'In Progress' | 'On Hold' | 'Resolved' | 'Closed'.
        resolution_notes: Required explanation when resolving or closing an incident.
    """
    res = asyncio.run(_service_client.update_ticket_status(ticket_id, new_status, resolution_notes))
    if "error" in res:
        return res["error"]
    return res.get("message", f"Ticket {ticket_id} updated to status '{new_status}'.")
