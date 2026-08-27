"""WorkWeek HCM tools for Google ADK Agent."""
import asyncio
from typing import Optional
from app.clients.workweek_client import WorkWeekClient
from app.guardrails.business_rules import validate_date_chronology, validate_phone_number

# Singleton client instance for tool execution
_ww_client = WorkWeekClient()


def get_worker_profile(employee_id: str = "") -> str:
    """Retrieve worker metadata, role, address, phone number, and remote status from WorkWeek HCM.
    
    Args:
        employee_id: The employee ID (optional, defaults to current authenticated employee session).
    """
    if not employee_id:
        employee_id = asyncio.run(_ww_client.get_current_employee_id())

    res = asyncio.run(_ww_client.get_employee_profile(employee_id))
    if "error" in res:
        return res["error"]
    if "raw_text" in res:
        return res["raw_text"]

    return (
        f"Employee: {res.get('name', 'Employee')} ({res['employee_id']})\n"
        f"Role: {res.get('role', 'Staff')} in {res.get('department', 'General')}\n"
        f"Address: {res.get('home_address', '')}\n"
        f"Phone: {res.get('phone_number', '')}\n"
        f"Remote Status: {res.get('remote_status', 'APPROVED_REMOTE')}"
    )


def update_worker_contact(
    employee_id: str = "",
    address: str = "",
    phone: str = "",
) -> str:
    """Update employee home address and/or phone number in WorkWeek HCM.
    
    Args:
        employee_id: The employee ID (optional, defaults to current authenticated employee session).
        address: New home street address (minimum 5 characters).
        phone: Standard international format phone number (e.g. +65 9123 4567 or +1 415-555-0199).
    """
    if not employee_id:
        employee_id = asyncio.run(_ww_client.get_current_employee_id())

    if phone:
        valid_phone, phone_msg = validate_phone_number(phone)
        if not valid_phone:
            return phone_msg

    res = asyncio.run(_ww_client.update_personal_info(employee_id, address=address or None, phone=phone or None))
    if "error" in res:
        return res["error"]
    return res.get("message", f"Successfully updated contact information for {employee_id}.")


def get_pto_balances(employee_id: str = "", leave_type: str = "") -> str:
    """Check remaining, accrued, and used PTO/Sick leave hours in WorkWeek HCM.
    
    Args:
        employee_id: The employee ID (optional, defaults to current authenticated employee session).
        leave_type: Optional leave filter ('Vacation' or 'Sick').
    """
    if not employee_id:
        employee_id = asyncio.run(_ww_client.get_current_employee_id())

    res = asyncio.run(_ww_client.get_employee_balances(employee_id, leave_type=leave_type or None))
    if "error" in res:
        return res["error"]
    if "raw_text" in res:
        return res["raw_text"]

    balances = res.get("balances", [])
    lines = [f"Leave balances for employee {employee_id}:"]
    for b in balances:
        lines.append(
            f"- {b['leave_type']}: {b['remaining_hours']:.0f} hours available "
            f"({b['accrued_hours']:.0f} accrued, {b['used_hours']:.0f} used)"
        )
    return "\n".join(lines)


def submit_time_off_request(
    employee_id: str = "",
    start_date: str = "",
    end_date: str = "",
    leave_type: str = "Vacation",
    days: float = 1.0,
    reason: str = "",
) -> str:
    """Submit a formal PTO or Sick Leave request in WorkWeek HCM.
    
    Args:
        employee_id: The employee ID (optional, defaults to current authenticated employee session).
        start_date: Start date formatted as YYYY-MM-DD.
        end_date: End date formatted as YYYY-MM-DD.
        leave_type: 'Vacation' | 'Sick' | 'Parental' | 'Unpaid'.
        days: Total working days requested (e.g. 2 days = 16 hours).
        reason: Optional explanation note.
    """
    if not employee_id:
        employee_id = asyncio.run(_ww_client.get_current_employee_id())

    valid_dates, date_msg = validate_date_chronology(start_date, end_date)
    if not valid_dates:
        return date_msg

    res = asyncio.run(
        _ww_client.request_time_off(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            days=days,
            reason=reason or None,
        )
    )
    if "error" in res:
        return res["error"]
    return res.get("message", f"Time-off request submitted successfully with ID {res.get('request_id')}.")


def cancel_time_off_request(employee_id: str = "", request_id: str = "", reason: str = "User requested cancellation") -> str:
    """Cancel a previously submitted time-off request in WorkWeek HCM and refund balances.
    
    Args:
        employee_id: The employee ID (optional, defaults to current authenticated employee session).
        request_id: Leave request identifier (e.g. 1 or WW-LEAVE-1001).
        reason: Reason for cancellation.
    """
    if not employee_id:
        employee_id = asyncio.run(_ww_client.get_current_employee_id())

    res = asyncio.run(_ww_client.cancel_leave_request(employee_id, request_id, reason))
    if "error" in res:
        return res["error"]
    return res.get("message", f"Leave request {request_id} has been cancelled.")
