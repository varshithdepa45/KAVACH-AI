"""KAVACH AI - FastAPI application entrypoint.

Run:
    python -m uvicorn app.main:app --reload --port 8000   (from the backend/ dir)
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .api.routes import router
from .database import db
from .security.middleware import AuditAndAirgapMiddleware, write_audit
from .services.seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: prepare dirs, DB and seed data.
    config.ensure_dirs()
    db.init_db()
    seed_all()
    write_audit("system.startup",
                detail=f"{config.APP_NAME} {config.VERSION} started in "
                       f"{config.KAVACH_MODE} mode.")
    yield
    write_audit("system.shutdown", detail="Application shutting down.")


app = FastAPI(
    title=f"{config.APP_NAME} - {config.APP_TAGLINE}",
    version=config.VERSION,
    description="Sovereign On-Premise Agentic AI Workbench (offline prototype).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    # Local-only appliance: accept the frontend on any localhost port so the UI
    # works regardless of which dev port Next.js picks.
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Kavach-Mode", "X-Kavach-Network"],
)
app.add_middleware(AuditAndAirgapMiddleware)

app.include_router(router)


@app.get("/")
def root():
    return {
        "app": config.APP_NAME,
        "tagline": config.APP_TAGLINE,
        "version": config.VERSION,
        "mode": config.KAVACH_MODE,
        "docs": "/docs",
        "health": "/api/health",
    }
