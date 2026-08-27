"""Policy search and grounding models."""
from typing import Optional, List
from pydantic import BaseModel


class PolicyCitation(BaseModel):
    """Citation link for a policy reference."""
    policy_id: str
    section: str
    title: str
    url: str


class PolicySearchResult(BaseModel):
    """Result returned by policy retrieval engine."""
    matched: bool
    policy_id: Optional[str] = None
    title: Optional[str] = None
    section: Optional[str] = None
    content: Optional[str] = None
    citation: Optional[PolicyCitation] = None
    source_url: Optional[str] = None
