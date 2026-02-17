"""Retail Chat Agent Backend Routes Package."""

from backend.app.v1.routes.healthcheck import router as healthcheck_router

__all__ = ["healthcheck_router"]