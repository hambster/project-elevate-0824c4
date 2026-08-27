"""Unit tests for WorkWeek and ServiceImmediately clients and OpenAPI specs."""
import pytest
from app.clients.workweek_client import WorkWeekClient
from app.clients.service_client import ServiceImmediatelyClient


@pytest.mark.asyncio
async def test_workweek_profile_lookup():
    """Verify employee profile retrieval and RBAC data isolation."""
    client = WorkWeekClient()
    
    # Authorized lookup
    res = await client.get_employee_profile("WW-10928", authenticated_user_id="WW-10928")
    assert res["employee_id"] == "WW-10928"
    assert res["name"] == "Alex Rivera"
    assert res["remote_status"] == "APPROVED_REMOTE"

    # Unauthorized cross-user lookup
    unauth = await client.get_employee_profile("WW-88888", authenticated_user_id="WW-10928")
    assert "error" in unauth
    assert "Access denied" in unauth["error"]


@pytest.mark.asyncio
async def test_workweek_leave_balances():
    """Verify leave balances retrieval."""
    client = WorkWeekClient()
    res = await client.get_employee_balances("WW-10928", authenticated_user_id="WW-10928")
    assert "balances" in res
    bals = {b["leave_type"]: b["remaining_hours"] for b in res["balances"]}
    assert bals["Vacation"] == 16.0
    assert bals["Sick"] == 40.0


@pytest.mark.asyncio
async def test_workweek_leave_submission_and_overdraw_gotcha():
    """Verify leave request submission and balance overdraw rejection."""
    client = WorkWeekClient()

    # Valid submission (2 days = 16 hours <= 16 hours balance)
    res = await client.request_time_off(
        employee_id="WW-10928",
        start_date="2026-09-03",
        end_date="2026-09-04",
        leave_type="Vacation",
        days=2.0,
        authenticated_user_id="WW-10928",
    )
    assert res["status"] == "SUCCESS"
    assert "WW-LEAVE-" in res["request_id"]

    # Overdraw attempt (request 40 hours when remaining is 0)
    overdraw = await client.request_time_off(
        employee_id="WW-10928",
        start_date="2026-09-10",
        end_date="2026-09-15",
        leave_type="Vacation",
        days=5.0,
        authenticated_user_id="WW-10928",
    )
    assert "error" in overdraw
    assert "requested 40 hours" in overdraw["error"].lower()


@pytest.mark.asyncio
async def test_service_ticket_lifecycle_and_transition_gotcha():
    """Verify ticket creation and status transition constraints."""
    client = ServiceImmediatelyClient()

    # Query existing ticket
    t_res = await client.get_ticket_details("INC123456")
    assert t_res["ticket_id"] == "INC123456"
    assert t_res["status"] == "In Progress"

    # Create new ticket
    create_res = await client.create_ticket(
        requested_by="WW-10928",
        category="Network / IT",
        short_description="VPN connection drops",
    )
    assert create_res["status"] == "SUCCESS"
    assert "INC" in create_res["ticket_id"]

    # Transition Gotcha: Cannot close directly without resolution notes
    illegal_trans = await client.update_ticket_status(
        ticket_id="INC008912",
        status="Closed",
        resolution_notes="",
    )
    assert "error" in illegal_trans
    assert "cannot be closed directly without resolution notes" in illegal_trans["error"].lower()
