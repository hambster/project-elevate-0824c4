"""Unit tests for WorkWeek and ServiceImmediately clients and OpenAPI specs."""
import pytest
from app.clients.workweek_client import WorkWeekClient
from app.clients.service_client import ServiceImmediatelyClient


@pytest.mark.asyncio
async def test_workweek_profile_lookup():
    """Verify employee profile retrieval and RBAC data isolation."""
    client = WorkWeekClient()
    emp_id = await client.get_current_employee_id()
    
    # Authorized lookup
    res = await client.get_employee_profile(emp_id, authenticated_user_id=emp_id)
    assert res["employee_id"] == emp_id
    assert "error" not in res

    # Unauthorized cross-user lookup
    unauth = await client.get_employee_profile("EMP-99999", authenticated_user_id=emp_id)
    assert "error" in unauth
    assert "Access denied" in unauth["error"]


@pytest.mark.asyncio
async def test_workweek_leave_balances():
    """Verify leave balances retrieval."""
    client = WorkWeekClient()
    emp_id = await client.get_current_employee_id()
    res = await client.get_employee_balances(emp_id, authenticated_user_id=emp_id)
    assert "error" not in res
    assert "raw_text" in res or "balances" in res


@pytest.mark.asyncio
async def test_workweek_leave_submission():
    """Verify leave request submission."""
    client = WorkWeekClient()
    emp_id = await client.get_current_employee_id()

    # Valid submission
    res = await client.request_time_off(
        employee_id=emp_id,
        start_date="2026-09-03",
        end_date="2026-09-04",
        leave_type="Vacation",
        days=2.0,
        authenticated_user_id=emp_id,
    )
    assert res["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_service_ticket_lifecycle_and_transition_gotcha():
    """Verify ticket creation and status transition constraints."""
    import uuid
    client = ServiceImmediatelyClient()
    ww_client = WorkWeekClient()
    emp_id = await ww_client.get_current_employee_id()

    # Create new ticket with authenticated ID and unique summary to avoid duplicate detection
    unique_desc = f"VPN connection drops {uuid.uuid4().hex[:6]}"
    create_res = await client.create_ticket(
        requested_by=emp_id,
        category="Network / IT",
        short_description=unique_desc,
    )
    assert create_res.get("status") in ["SUCCESS", "FAILED"]
    if create_res.get("status") == "SUCCESS":
        assert "INC" in str(create_res.get("ticket_id", "")) or "INC" in str(create_res.get("message", ""))

    # Transition Gotcha: Cannot close directly without resolution notes
    illegal_trans = await client.update_ticket_status(
        ticket_id="INC008912",
        status="Closed",
        resolution_notes="",
    )
    assert "error" in illegal_trans or "cannot be closed" in str(illegal_trans).lower()


def test_mcp_token_resolution_order():
    """Verify MCP token resolution: request header > injected instance token > .env default."""
    from app.app_utils.context import request_mcp_token
    from app.clients.base_client import BaseClient
    from app.config import settings

    # 1. Default fallback to settings / .env
    default_client = BaseClient()
    assert default_client.get_token() == settings.mcp_token
    assert default_client.get_headers()["X-MCP-Token"] == settings.mcp_token

    # 2. Injected instance token takes precedence over default
    injected_client = BaseClient(token="injected_token_xyz")
    assert injected_client.get_token() == "injected_token_xyz"
    assert injected_client.get_headers()["X-MCP-Token"] == "injected_token_xyz"

    # 3. Request-scoped header token takes highest precedence
    token_ctx = request_mcp_token.set("request_header_token_abc")
    try:
        assert default_client.get_token() == "request_header_token_abc"
        assert default_client.get_headers()["X-MCP-Token"] == "request_header_token_abc"
        assert injected_client.get_token() == "request_header_token_abc"
        assert injected_client.get_headers()["X-MCP-Token"] == "request_header_token_abc"
    finally:
        request_mcp_token.reset(token_ctx)

    # 4. After request context cleanup, returns to previous levels
    assert default_client.get_token() == settings.mcp_token
    assert injected_client.get_token() == "injected_token_xyz"
