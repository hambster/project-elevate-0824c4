"""Saga multi-hop tools for Google ADK Agent."""
import asyncio
from app.clients.workweek_client import WorkWeekClient
from app.clients.service_client import ServiceImmediatelyClient
from app.saga.coordinator import SagaCoordinator

_coordinator = SagaCoordinator(WorkWeekClient(), ServiceImmediatelyClient())


def handle_equipment_procurement(employee_id: str = "WW-10928") -> str:
    """Orchestrate UC-2.1 cross-system Equipment Procurement (Policy check -> WorkWeek remote status verify -> ServiceImmediately monitor ticket).
    
    Args:
        employee_id: Authenticated employee ID.
    """
    res = asyncio.run(_coordinator.execute_equipment_procurement_saga(employee_id))
    return res.get("message", str(res))


def handle_medical_leave_workflow(
    employee_id: str = "WW-10928",
    start_date: str = "2026-09-01",
    end_date: str = "2026-09-05",
    days: float = 5.0,
) -> str:
    """Orchestrate UC-2.2 cross-system Medical Leave (Policy quote -> WorkWeek Sick Leave submit -> ServiceImmediately confidential HRSD case).
    
    Args:
        employee_id: Authenticated employee ID.
        start_date: Medical leave start date (YYYY-MM-DD).
        end_date: Medical leave end date (YYYY-MM-DD).
        days: Total working days requested.
    """
    res = asyncio.run(_coordinator.execute_medical_leave_saga(employee_id, start_date, end_date, days))
    return res.get("message", str(res))


def handle_relocation_workflow(
    employee_id: str = "WW-10928",
    new_address: str = "10 Downing Street, London SW1A 2AA, United Kingdom",
) -> str:
    """Orchestrate UC-2.3 cross-system London Relocation (Policy quote $5,000 -> WorkWeek address update -> ServiceImmediately Facilities Badge ticket).
    
    Args:
        employee_id: Authenticated employee ID.
        new_address: New London residential or office address.
    """
    res = asyncio.run(_coordinator.execute_relocation_saga(employee_id, new_address))
    return res.get("message", str(res))


def simulate_saga_failure_rollback(employee_id: str = "WW-10928") -> str:
    """Simulate a multi-hop saga where downstream ServiceImmediately ticket creation fails and triggers automated WorkWeek leave rollback.
    
    Args:
        employee_id: Authenticated employee ID.
    """
    res = asyncio.run(_coordinator.simulate_downstream_failure_saga(employee_id))
    return res.get("message", str(res))
