"""Research state management for LangGraph workflow."""

from typing import TypedDict


class Paper(TypedDict):
    """Represents a research paper."""

    title: str
    authors: list[str]
    abstract: str
    url: str
    year: int | None
    citations: int | None


class Analysis(TypedDict):
    """Represents analysis of a paper."""

    paper_id: str
    summary: str
    key_findings: list[str]
    methodology: str
    limitations: list[str]


class Synthesis(TypedDict):
    """Represents data synthesis results."""

    insights: list[str]
    patterns: list[str]
    research_gaps: list[str]
    trends: dict[str, any]


class Citation(TypedDict):
    """Represents a formatted citation."""

    paper_id: str
    style: str
    formatted: str


class ResearchState(TypedDict):
    """Main state for the research workflow."""

    topic: str
    search_results: list[Paper]
    analyzed_papers: list[Analysis]
    synthesis: Synthesis | None
    paper_sections: dict[str, str]
    citations: list[Citation]
    status: str
    current_node: str
    error: str | None
