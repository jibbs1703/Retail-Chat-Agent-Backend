"""Pydantic models for the research paper agent."""

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    """Request model for starting research."""

    topic: str
    citation_style: str = "APA"
    email: str | None = None


class ResearchStatus(BaseModel):
    """Status response for research job."""

    job_id: str
    status: str
    progress: float
    current_stage: str
    message: str | None = None


class EmailConfig(BaseModel):
    """Email configuration."""

    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    email_from: str


class PaperSearchRequest(BaseModel):
    """Request for semantic paper search."""

    query: str
    limit: int = 10
