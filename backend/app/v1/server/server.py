"""Retail Chat Agent Backend Server Module."""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.v1.routes import healthcheck_router

router = APIRouter()


app = FastAPI(
    title="Retail Chat Agent Backend API",
    description=(
        "API for the Retail Chat Agent Backend, providing endpoints for chat "
        "search and embedding models management."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck_router)
