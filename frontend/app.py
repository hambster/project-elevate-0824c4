import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="HR Assistant Frontend Web Service",
    description="Standalone Web UI Presentation Service for Enterprise HR Agentic Solution (MVP 1)",
    version="1.0.0"
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Mount Static Files (CSS, JS)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serves the Single Page Application (Screen 1 Welcome & Screen 2 Q&A Workspace)."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Standalone Frontend Web Service running at http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
