"""Research Paper Agent Server Module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from app.routes.health import router as health_router

# Create FastAPI app
app = FastAPI(
    title="Research Paper Agent API",
    description="AI-powered research assistant for academic literature review",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Research Paper Agent API", "version": "1.0.0", "docs": "/docs"}
