import asyncio
from typing import Any, Dict, Optional
import httpx
from app.app_utils.context import request_mcp_token
from app.config import settings


class BaseClient:
    """Base client managing HTTP transport, X-MCP-Token headers, and fallback logic."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.base_url).rstrip("/")
        self.token = token
        self.timeout = timeout or settings.client_timeout_seconds
        self.max_retries = max_retries or settings.max_retries
        self.consecutive_timeouts = 0
        self.circuit_open = False

    def get_token(self) -> str:
        """Resolve effective token: Request Header Context -> Injected Token -> .env Config."""
        return request_mcp_token.get() or self.token or settings.mcp_token

    def get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Construct required authentication and metadata headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-MCP-Token": self.get_token(),
            "x-goog-authenticated-user-email": settings.default_user_email,
            "X-Origin-Entity": "AUTOMATION-AGENT",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    async def call_mcp_tool(self, mcp_url: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a FastMCP tool via JSON-RPC 2.0 over Streamable HTTP."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }
        req_headers = self.get_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(mcp_url, json=payload, headers=req_headers)
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data:
                    return data["result"]
                return data
            return {"error": f"MCP HTTP Error {resp.status_code}", "status_code": resp.status_code}

    async def execute_request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP request with exponential backoff retry and circuit breaking."""
        if self.circuit_open:
            raise RuntimeError(f"Circuit breaker OPEN for {self.base_url}. Service temporarily degraded.")

        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        req_headers = self.get_headers(headers)
        delays = [0.2, 0.5, 1.0]

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.request(
                        method=method,
                        url=url,
                        json=json_data,
                        params=params,
                        headers=req_headers,
                    )
                    if resp.status_code in [200, 201]:
                        self.consecutive_timeouts = 0
                        return resp.json() if resp.content else {"status": "SUCCESS"}
                    elif resp.status_code in [400, 401, 403, 404, 409, 422]:
                        # Non-transient error; return response json or raise
                        try:
                            return resp.json()
                        except Exception:
                            return {"error": resp.text, "status_code": resp.status_code}
                    elif resp.status_code in [429, 502, 503, 504]:
                        if attempt == self.max_retries - 1:
                            return {"error": f"Service unavailable (HTTP {resp.status_code})", "status_code": resp.status_code}
                        await asyncio.sleep(delays[min(attempt, len(delays) - 1)])
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                self.consecutive_timeouts += 1
                if attempt == self.max_retries - 1:
                    if self.consecutive_timeouts >= 3:
                        self.circuit_open = True
                    raise TimeoutError(f"Request to {url} timed out after {self.timeout}s across {self.max_retries} attempts: {e}")
                await asyncio.sleep(delays[min(attempt, len(delays) - 1)])

        return {"error": "Request failed after all retries"}
