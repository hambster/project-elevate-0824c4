import os
import json
import urllib.request
import urllib.error
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HR Assistant Frontend Web Service",
    description="Standalone Web UI Presentation Service for Enterprise HR Agentic Solution (MVP 1)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# Mount Static Directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/styles.css")
async def get_css():
    return FileResponse(os.path.join(STATIC_DIR, "styles.css"), media_type="text/css", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/app.js")
async def get_js():
    return FileResponse(os.path.join(STATIC_DIR, "app.js"), media_type="application/javascript", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serves the Single Page Application (Screen 1 Welcome & Screen 2 Q&A Workspace)."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

def proxy_to_backend(path: str, request: Request, body_bytes: bytes):
    url = f"{BACKEND_URL}{path}"
    headers = {}
    for key, val in request.headers.items():
        if key.lower() not in ("host", "content-length"):
            headers[key] = val

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=request.method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            try:
                content = json.loads(data.decode("utf-8"))
                return JSONResponse(status_code=resp.status, content=content)
            except Exception:
                return HTMLResponse(status_code=resp.status, content=data.decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            content = json.loads(err_body)
        except Exception:
            content = {"detail": err_body}
        return JSONResponse(status_code=e.code, content=content)
    except Exception as ex:
        return JSONResponse(status_code=502, content={"detail": f"Backend proxy error: {str(ex)}"})

@app.post("/run_sse")
async def run_sse_proxy(request: Request):
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")}
    body = await request.body()
    req = urllib.request.Request(f"{BACKEND_URL}/run_sse", data=body, headers=headers, method="POST")
    try:
        def stream_generator():
            with urllib.request.urlopen(req, timeout=120) as resp:
                for line in resp:
                    yield line

        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            content = json.loads(err_body)
        except Exception:
            content = {"detail": err_body}
        return JSONResponse(status_code=e.code, content=content)
    except Exception as ex:
        return JSONResponse(status_code=502, content={"detail": f"Backend proxy error: {str(ex)}"})

@app.api_route("/apps/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def apps_proxy(path: str, request: Request):
    body = await request.body()
    return proxy_to_backend(f"/apps/{path}", request, body)

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def api_proxy(path: str, request: Request):
    body = await request.body()
    return proxy_to_backend(f"/api/{path}", request, body)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Standalone Frontend Web Service running at http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
