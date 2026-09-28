"""
CareerAI backend entry point.

Run with:
    uvicorn app.main:app --reload

This file should stay thin: it wires up the FastAPI app, middleware, and
route registration. Actual logic always lives in app/services/, never here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered career readiness, skill-gap analysis and personalized career development platform.",
    version="0.1.0",
)

# Allow the React frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Basic landing response so hitting the base URL isn't a 404."""
    return {
        "message": f"{settings.APP_NAME} API is running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    """
    Used by: deployment checks, Docker healthcheck (Phase 21), and you,
    right now, to confirm the server actually started correctly.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.ENV,
    }
