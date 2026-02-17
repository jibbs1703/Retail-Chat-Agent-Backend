"""Retail Chat Agent Backend Healthcheck Routes Module."""

from fastapi import APIRouter

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@router.get("/")
async def healthcheck():
    """Starter Healthcheck endpoint to verify that the server is running."""
    return {"status": "ok"}
