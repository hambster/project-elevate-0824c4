"""ITSM and ticket tracking models."""
from typing import Optional, List
from pydantic import BaseModel, Field


class TicketComment(BaseModel):
    """Comment on a ticket."""
    comment_id: str
    author_id: str
    author_type: str = "AUTOMATION"
    timestamp: str
    content: str


class TicketCreateRequest(BaseModel):
    """Payload to create an incident ticket."""
    requested_by: str = Field(..., description="Employee ID of the requester")
    category: str = Field(..., description="Category: Hardware, Software, Access, General_HRSD, Network / IT")
    short_description: str = Field(..., description="Short summary of the issue")
    priority: str = Field("3 - Moderate", description="1 - Critical, 2 - High, 3 - Moderate, 4 - Low")
    assignment_group: str = Field("Service Desk", description="Target assignment group")
    detailed_description: Optional[str] = None


class TicketStatusUpdateRequest(BaseModel):
    """Payload to update the lifecycle state of a ticket."""
    status: str = Field(..., description="Target status: New, In Progress, Resolved, Closed, On Hold")
    resolution_notes: Optional[str] = Field("", description="Resolution notes (required if Resolving or Closing)")
    updated_by: Optional[str] = Field("System", description="Identifier of the user or system making the update")


class CommentCreateRequest(BaseModel):
    """Payload to append a comment to an incident."""
    author: str = Field(..., description="Author ID / Name")
    comment_text: str = Field(..., description="Content of the comment")


class IncidentTicket(BaseModel):
    """Full incident ticket representation."""
    ticket_id: str
    caller_id: str
    short_description: str
    detailed_description: Optional[str] = ""
    category: str
    priority: str
    status: str = "New"  # 'New' | 'In Progress' | 'Resolved' | 'Closed' | 'On Hold'
    assignment_group: str = "Service Desk"
    assignee: Optional[str] = "Unassigned"
    resolution_notes: Optional[str] = None
    created_at: str
    updated_at: str
    comments: List[TicketComment] = []
