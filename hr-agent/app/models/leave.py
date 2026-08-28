"""Leave and time-off models."""
from typing import Optional
from pydantic import BaseModel, Field


class LeaveBalance(BaseModel):
    """Leave balance details for an employee."""
    leave_type: str  # 'Vacation' | 'Sick' | 'Personal'
    accrued_hours: float
    used_hours: float
    remaining_hours: float


class TimeOffRequest(BaseModel):
    """Payload to submit a leave request."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    leave_type: str = Field("Vacation", description="Leave type: Vacation, Sick, Parental, Unpaid")
    days: float = Field(..., gt=0, description="Total requested working days")
    reason: Optional[str] = None


class LeaveRequestUpdateRequest(BaseModel):
    """Payload to update an existing leave request."""
    start_date: str
    end_date: str
    leave_type: str
    days: float


class LeaveRequest(BaseModel):
    """A registered leave request."""
    request_id: str
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    days: float
    status: str = "SUBMITTED"  # 'SUBMITTED' | 'APPROVED' | 'CANCELLED'
    cancellation_reason: Optional[str] = None
