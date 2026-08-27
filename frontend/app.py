import os
import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Decoupled HR Assistant Frontend Service",
    description="Frontend UI Web Service for HR Agentic Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_AGENT_URL = os.getenv("BACKEND_AGENT_URL", "http://localhost:8000/api/chat")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Mount Static Files (CSS, JS)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serves the Single Page Application (Screen 1 Auth & Screen 2 Assistant)."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/chat")
async def proxy_chat(request: Request):
    """
    Decoupled API Proxy:
    Forwards the user query & employee delegation token header/payload to the backend agent service.
    """
    try:
        body = await request.json()
        headers = dict(request.headers)
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                BACKEND_AGENT_URL,
                json=body,
                headers={
                    "X-Employee-Token": headers.get("x-employee-token", body.get("employee_token", "WW-10928")),
                    "Content-Type": "application/json"
                }
            )
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        # Fallback response when backend service is offline
        return JSONResponse(
            status_code=200,
            content={
                "response_text": (
                    f"⚠️ **Frontend Proxy Notice:** Decoupled Backend Agent at `{BACKEND_AGENT_URL}` is currently offline.\n\n"
                    f"Please start the backend agent service in `my-agent/` (running on port `8000`)."
                ),
                "intent": "PROXY_FALLBACK",
                "sub_agent": "frontend_proxy",
                "status": "BACKEND_OFFLINE"
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Decoupled Frontend Service running at http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
