"""Retail Chat Agent Backend Healthcheck Routes Module."""

from fastapi import APIRouter

router = APIRouter(tags=["Healthcheck"])


@router.get("/healthcheck")
async def healthcheck():
    """Starter Healthcheck endpoint to verify that the server is running."""
    return {"status": "ok"}
