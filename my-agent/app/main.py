import os
import sys
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ensure app module path is resolved cleanly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.agent_engine import HRAgentEngine
except ModuleNotFoundError:
    from agent_engine import HRAgentEngine

app = FastAPI(
    title="HR Agentic Solution Backend Service",
    description="Decoupled Agent Orchestration Backend Service (LangGraph, Policy RAG, WorkWeek & ServiceImmediately MCPs)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = HRAgentEngine()

class ChatPayload(BaseModel):
    query: str
    employee_token: Optional[str] = "WW-10928"

@app.get("/health")
async def health_check():
    return {"status": "HEALTHY", "service": "backend-agent-orchestrator", "version": "1.0.0"}

@app.post("/api/auth/verify")
async def verify_token(payload: dict):
    token = payload.get("token", "WW-10928")
    profile = engine.verify_token(token)
    return {"status": "SUCCESS", "profile": profile.dict()}

@app.post("/api/chat")
async def chat_endpoint(payload: ChatPayload, x_employee_token: Optional[str] = Header(None)):
    """
    Decoupled Backend Agent API Endpoint:
    Receives user query and employee delegation token, executes Model Armor scanner, DLP masking,
    intent routing, policy search, WorkWeek/ServiceImmediately MCP tool execution, and returns structured AgentResponse.
    """
    token = x_employee_token or payload.employee_token or "WW-10928"
    response = engine.process_message(payload.query, token)
    return JSONResponse(status_code=200, content=response.dict())

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Decoupled Backend Agent Service running at http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
