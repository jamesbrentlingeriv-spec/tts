import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import settings, voices, tts, audio
from app.config import BASE_DIR

app = FastAPI(
    title="SPRACH - AI Text-to-Speech Studio",
    description="High-speed AI Text-to-Speech PWA with Microsoft Neural TTS, Audiobook Studio, and Studio Voices",
    version="1.0.0"
)

# Enable CORS for local development and PWA caching
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(settings.router)
app.include_router(voices.router)
app.include_router(tts.router)
app.include_router(audio.router)

# Mount static files
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(static_dir / "index.html")

@app.get("/manifest.webmanifest")
def serve_manifest():
    return FileResponse(
        static_dir / "manifest.webmanifest",
        media_type="application/manifest+json"
    )

@app.get("/sw.js")
def serve_service_worker():
    return FileResponse(
        static_dir / "sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )
