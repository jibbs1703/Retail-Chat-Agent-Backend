"""Retail Chat Agent Backend Server Module."""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..core.configuration import get_settings
from ..routes import healthcheck_router

settings = get_settings()


router = APIRouter()
settings = get_settings()


app = FastAPI(
    title=settings.application_name,
    description=settings.application_description,
    version=settings.application_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck_router, prefix=settings.application_api_prefix)
