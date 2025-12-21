"""Validation functions for workflow edges."""

from app.core.config import get_settings
from app.state.research_state import ResearchState

settings = get_settings()


def validate_search_results(state: ResearchState) -> bool:
    """Validate that search returned sufficient results."""
    results = state.get("search_results", [])
    return len(results) >= settings.MIN_RESULTS


def validate_analyses(state: ResearchState) -> bool:
    """Validate that papers were properly analyzed."""
    analyses = state.get("analyzed_papers", [])
    return len(analyses) > 0 and all(analysis.get("summary") for analysis in analyses)


def validate_synthesis(state: ResearchState) -> bool:
    """Validate that synthesis was successful."""
    synthesis = state.get("synthesis")
    return synthesis is not None and len(synthesis.get("insights", [])) > 0


def validate_paper_sections(state: ResearchState) -> bool:
    """Validate that paper sections were generated."""
    sections = state.get("paper_sections", {})
    required_sections = [
        "abstract",
        "introduction",
        "literature_review",
        "discussion",
        "conclusion",
    ]
    return all(section in sections for section in required_sections)


def validate_citations(state: ResearchState) -> bool:
    """Validate that citations were generated."""
    citations = state.get("citations", [])
    return len(citations) >= settings.MIN_CITATIONS
