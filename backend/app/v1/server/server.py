"""Retail Chat Agent Backend Server Module."""

from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..agents import get_retail_agent
from ..core.configuration import get_settings
from ..core.utilities import warm_up_clip
from ..routes import chat_router, healthcheck_router, sessions_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the agent and Redis connection on startup; close on shutdown."""
    warm_up_clip()
    app.state.agent = get_retail_agent()
    app.state.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    yield
    app.state.redis.close()


app = FastAPI(
    title=settings.application_name,
    description=settings.application_description,
    version=settings.application_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.application_api_prefix
app.include_router(healthcheck_router, prefix=prefix)
app.include_router(chat_router, prefix=prefix)
app.include_router(sessions_router, prefix=prefix)
