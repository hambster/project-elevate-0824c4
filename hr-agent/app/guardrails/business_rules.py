"""Business rules and constraint validation for WorkWeek HCM and ServiceImmediately ITSM."""
import re
from datetime import datetime
from typing import Optional, Tuple

PHONE_REGEX = re.compile(r"^\+?[\d\s\-()]{7,20}$")
TICKET_ID_REGEX = re.compile(r"^INC\d{6}$")


def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """Validate phone number according to international E.164 pattern."""
    if not PHONE_REGEX.match(phone.strip()):
        return (
            False,
            "The phone number format provided is invalid. Please provide a standard international phone number (e.g. +65 9123 4567 or +1 415-555-0199).",
        )
    return True, ""


def validate_date_chronology(start_date: str, end_date: str) -> Tuple[bool, str]:
    """Validate that start date is on or before end date and both are valid dates."""
    try:
        s_dt = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        e_dt = datetime.strptime(end_date.strip(), "%Y-%m-%d")
    except ValueError:
        return False, "Dates must follow the YYYY-MM-DD format."

    if s_dt > e_dt:
        return False, "Start date cannot be after end date. Please provide valid dates for your time-off request."

    return True, ""


def validate_ticket_id_format(ticket_id: str) -> Tuple[bool, str]:
    """Validate ITSM ticket ID format (INC + 6 digits)."""
    if not TICKET_ID_REGEX.match(ticket_id.strip()):
        return False, f"Ticket ID '{ticket_id}' must follow the 'INC' followed by 6 digits format (e.g. INC123456)."
    return True, ""
