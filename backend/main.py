"""FastAPI application entry point."""

import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import newsletter, settings, history
from backend.database.db_manager import init_db
from backend.config.settings import settings as app_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

app = FastAPI(
    title="HAL Newsletter API",
    version="1.0.0",
    description="Backend API for the HAL AI Tools Weekly Newsletter Generator",
)

# CORS — allow Vite dev server, local React build, and Vercel domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — mounted with both /api prefix and root prefix for seamless Vercel/Render compatibility
app.include_router(newsletter.router, prefix="/api/newsletter")
app.include_router(settings.router, prefix="/api/settings")
app.include_router(history.router, prefix="/api/history")

app.include_router(newsletter.router, prefix="/newsletter")
app.include_router(settings.router, prefix="/settings")
app.include_router(history.router, prefix="/history")


@app.on_event("startup")
async def startup():
    """Initialise database on first run."""
    await init_db()
    # Ensure output directory exists
    Path(app_settings.newsletter_output_dir).mkdir(parents=True, exist_ok=True)
    Path("generated_newsletters/logs").mkdir(parents=True, exist_ok=True)


@app.get("/")
@app.get("/health")
async def health():
    return {"status": "ok", "app": "HAL Newsletter API"}


# Serve generated PDFs/HTML at /generated/<filename>
_output_dir = Path(app_settings.newsletter_output_dir)
_output_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/generated",
    StaticFiles(directory=str(_output_dir)),
    name="generated",
)
