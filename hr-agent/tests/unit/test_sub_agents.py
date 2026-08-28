"""Unit tests for Hierarchical Sub-Agents topology and tool mappings."""
from app.sub_agents.policy_agent import policy_agent
from app.sub_agents.enterprise_service_agent import enterprise_service_agent
from app.agent import root_agent


def test_policy_agent_topology():
    """Verify PolicyAgent configuration and specialized tools."""
    assert policy_agent.name == "policy_agent"
    tool_names = [getattr(t, "__name__", str(t)) for t in policy_agent.tools]
    assert "list_concepts" in tool_names
    assert "read_concept" in tool_names
    assert "search_hr_policies" in tool_names
    # Verify it does NOT contain SaaS write/mutation tools
    assert "submit_time_off_request" not in tool_names
    assert "create_support_incident" not in tool_names


def test_enterprise_service_agent_topology():
    """Verify EnterpriseServiceAgent configuration and SaaS tools."""
    assert enterprise_service_agent.name == "enterprise_service_agent"
    tool_names = [getattr(t, "__name__", str(t)) for t in enterprise_service_agent.tools]
    # WorkWeek tools
    assert "get_worker_profile" in tool_names
    assert "get_pto_balances" in tool_names
    assert "submit_time_off_request" in tool_names
    # ServiceImmediately tools
    assert "get_ticket_info" in tool_names
    assert "create_support_incident" in tool_names
    # Saga tools
    assert "handle_equipment_procurement" in tool_names
    assert "handle_medical_leave_workflow" in tool_names
    assert "handle_relocation_workflow" in tool_names
    assert "simulate_saga_failure_rollback" in tool_names
    # Verify it does NOT contain policy retrieval tools
    assert "list_concepts" not in tool_names


def test_root_supervisor_hierarchy():
    """Verify Root Supervisor orchestrator references the specialized sub-agents."""
    assert root_agent.name == "root_agent"
    sub_agent_names = [sa.name for sa in root_agent.sub_agents]
    assert "policy_agent" in sub_agent_names
    assert "enterprise_service_agent" in sub_agent_names
