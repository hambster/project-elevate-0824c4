"""Context variable management for request-scoped metadata (e.g. MCP tokens)."""
import contextvars
from typing import Optional

# Request-scoped MCP token context variable
request_mcp_token: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_mcp_token", default=None
)
