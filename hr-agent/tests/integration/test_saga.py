"""Integration tests for Cross-System Saga workflows and compensating rollbacks."""
import pytest
from app.tools.saga_tools import (
    handle_equipment_procurement,
    handle_medical_leave_workflow,
    handle_relocation_workflow,
    simulate_saga_failure_rollback,
)


def test_saga_equipment_procurement_uc21():
    """UC-2.1: Verify cross-system equipment procurement saga."""
    output = handle_equipment_procurement("WW-10928")
    assert "APPROVED_REMOTE" in output
    assert "27-inch" in output or "monitor" in output
    assert "INC" in output
    assert "POL-REMOTE-002" in output


def test_saga_medical_leave_uc22():
    """UC-2.2: Verify cross-system medical leave saga."""
    output = handle_medical_leave_workflow("WW-10928", "2026-09-01", "2026-09-05", 5.0)
    assert "WorkWeek" in output
    assert "ServiceImmediately" in output
    assert "Medical" in output or "Sick" in output
    assert "POL-MEDICAL-003" in output


def test_saga_relocation_uc23():
    """UC-2.3: Verify cross-system relocation saga."""
    output = handle_relocation_workflow("WW-10928", "10 Downing Street, London")
    assert "$5,000" in output
    assert "WorkWeek" in output
    assert "Facilities" in output
    assert "POL-RELOCATION-004" in output


def test_saga_downstream_failure_rollback():
    """NFR-4.3: Verify automated compensating rollback on downstream ITSM failure."""
    output = simulate_saga_failure_rollback("WW-10928")
    assert "WorkWeek" in output
    assert "notification setup encountered an issue" in output
    assert "HR Operations has been notified" in output
