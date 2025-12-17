"""API route definitions for FastAPI."""

from fastapi import APIRouter

from app.routes.health import router as health_router
from app.routes.papers import router as papers_router
from app.routes.research import router as research_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(research_router, prefix="/research", tags=["research"])
api_router.include_router(papers_router, prefix="/papers", tags=["papers"])
