"""Routing logic for the research workflow edges."""

from app.state.research_state import ResearchState


def route_after_search(state: ResearchState) -> str:
    """Route after literature search."""
    if state.get("error"):
        return "error_handler"
    if len(state.get("search_results", [])) == 0:
        return "expand_search"
    return "paper_analysis"


def route_after_analysis(state: ResearchState) -> str:
    """Route after paper analysis."""
    if state.get("error"):
        return "error_handler"
    if len(state.get("analyzed_papers", [])) == 0:
        return "retry_analysis"
    return "data_synthesis"


def route_after_synthesis(state: ResearchState) -> str:
    """Route after data synthesis."""
    if state.get("error"):
        return "error_handler"
    return "writer"


def route_after_writing(state: ResearchState) -> str:
    """Route after writing."""
    if state.get("error"):
        return "error_handler"
    return "citation_manager"


def route_after_citation(state: ResearchState) -> str:
    """Route after citation management."""
    if state.get("error"):
        return "error_handler"
    return "document_generation"
