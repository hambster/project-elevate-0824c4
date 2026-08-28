# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
import sys
from collections.abc import AsyncIterator
from typing import Optional

import nest_asyncio
nest_asyncio.apply()

from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from pydantic import BaseModel

HR_AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(HR_AGENT_DIR)
sys.path.insert(0, HR_AGENT_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "my-agent", "app"))
sys.path.insert(0, os.path.join(ROOT_DIR, "my-agent"))

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.context import request_mcp_token

try:
    from agent_engine import HRAgentEngine
except ModuleNotFoundError:
    from app.agent_engine import HRAgentEngine

engine = HRAgentEngine()

class ChatPayload(BaseModel):
    query: str
    employee_token: Optional[str] = ""

load_dotenv()
allow_origins = ["*"]


class MCPTokenMiddleware(BaseHTTPMiddleware):
    """Middleware to capture MCP auth token passed via custom request headers."""

    async def dispatch(self, request: Request, call_next):
        custom_token = (
            request.headers.get("x-mcp-token")
            or request.headers.get("x-custom-mcp-token")
            or request.headers.get("mcp-token")
        )
        token_ctx = request_mcp_token.set(custom_token) if custom_token else None
        try:
            response = await call_next(request)
            return response
        finally:
            if token_ctx is not None:
                request_mcp_token.reset(token_ctx)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=True,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MCPTokenMiddleware)
app.title = "hr-agent"
app.description = "API for interacting with the Agent hr-agent"


@app.get("/health")
async def health_check():
    return {"status": "HEALTHY", "service": "hr-agent-backend", "version": "1.0.0"}


@app.post("/api/auth/verify")
async def verify_token(
    payload: dict,
    x_mcp_token: Optional[str] = Header(None),
    x_custom_mcp_token: Optional[str] = Header(None),
    mcp_token: Optional[str] = Header(None)
):
    token = request_mcp_token.get() or x_mcp_token or x_custom_mcp_token or mcp_token or payload.get("token") or ""
    profile = engine.verify_token(token)
    if not profile:
        return JSONResponse(
            status_code=401,
            content={"status": "UNAUTHORIZED", "detail": f"Invalid or unrecognized identity token: '{token}'"}
        )
    return {"status": "SUCCESS", "profile": profile.dict()}


@app.post("/api/chat")
async def chat_endpoint(
    payload: ChatPayload,
    x_mcp_token: Optional[str] = Header(None),
    x_custom_mcp_token: Optional[str] = Header(None),
    mcp_token: Optional[str] = Header(None)
):
    token = request_mcp_token.get() or x_mcp_token or x_custom_mcp_token or mcp_token or payload.employee_token or ""
    profile = engine.verify_token(token)
    if not profile:
        return JSONResponse(
            status_code=401,
            content={
                "response_text": f"⚠️ **Authentication Failed:** Invalid or unauthorized identity token (`{token}`). Please provide a valid token via X-MCP-Token header.",
                "status": "UNAUTHORIZED",
                "intent": "AUTH_FAILURE",
                "sub_agent": "auth_gate"
            }
        )
    response = engine.process_message(payload.query, token)
    return JSONResponse(status_code=200, content=response.dict())


# Main execution
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.fast_api_app:app", host="0.0.0.0", port=port)
