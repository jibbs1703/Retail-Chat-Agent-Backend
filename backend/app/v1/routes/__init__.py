"""Retail Chat Agent Backend Routes Package."""

from .healthcheck import router as healthcheck_router

__all__ = ["healthcheck_router"]
