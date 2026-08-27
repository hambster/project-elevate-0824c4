"""Employee data models."""
from typing import Optional
from pydantic import BaseModel, Field


class EmployeeProfile(BaseModel):
    """Employee personal and employment metadata."""
    employee_id: str
    name: str
    email: str
    role: str
    department: Optional[str] = "Engineering"
    manager_id: Optional[str] = "WW-00100"
    home_address: Optional[str] = ""
    phone_number: Optional[str] = ""
    location: Optional[str] = "US - Mountain View"
    remote_status: Optional[str] = "APPROVED_REMOTE"


class ProfileUpdateRequest(BaseModel):
    """Payload to update editable employee contact details."""
    address: Optional[str] = Field(None, min_length=5, description="New home address")
    phone: Optional[str] = Field(None, description="Standard international phone number")
