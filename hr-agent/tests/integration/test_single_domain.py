"""Integration tests for single-domain tool actions (Policy RAG, WorkWeek, ITSM)."""
import pytest
from app.tools.policy_tools import search_hr_policies
from app.tools.workweek_tools import (
    get_pto_balances,
    submit_time_off_request,
    get_worker_profile,
)
from app.tools.service_tools import (
    get_ticket_info,
    create_support_incident,
    update_incident_status,
)


def test_policy_bereavement_qa():
    """UC-1.1: Verify bereavement leave Q&A with clickable citation."""
    res = search_hr_policies("What is the company bereavement leave policy?")
    assert res["matched"]
    assert "5" in res["content"]
    assert "immediate family" in res["content"]
    assert "POL-BEREAVEMENT-001" in res["citation"]
    assert "Section 4.2" in res["citation"]


def test_policy_headphones_qa():
    """UC-1.1: Verify noise-canceling headphones reimbursement limit ($150)."""
    res = search_hr_policies("Are employees allowed to expense noise-canceling headphones?")
    assert res["matched"]
    assert "150" in res["content"]
    assert "manager pre-approval" in res["content"]
    assert "POL-EXPENSE-005" in res["citation"]


def test_policy_abstention_pet_leave():
    """Verify strict policy abstention for uncovered pet birthday leave."""
    res = search_hr_policies("What is the policy for pet's birthday leave?")
    assert not res["matched"]
    assert "could not find an answer" in res["message"]


def test_workweek_pto_balance_tool():
    """UC-1.2: Check WorkWeek PTO balance tool."""
    output = get_pto_balances("WW-10928")
    assert "16" in output
    assert "Vacation" in output
    assert "40" in output
    assert "Sick" in output


def test_service_ticket_inquiry_tool():
    """UC-1.3: Check ServiceImmediately ticket inquiry tool."""
    output = get_ticket_info("INC123456")
    assert "INC123456" in output
    assert "In Progress" in output
    assert "VPN connection drops" in output
