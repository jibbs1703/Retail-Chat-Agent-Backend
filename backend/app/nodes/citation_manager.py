"""Citation manager node for formatting references."""

from app.state.research_state import Citation, ResearchState


def format_citation_apa(paper: dict) -> str:
    """Format a paper citation in APA style."""
    authors = paper.get("authors", [])
    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} & {authors[1]}"
    else:
        author_str = f"{authors[0]} et al."

    year = paper.get("year", "n.d.")
    title = paper.get("title", "Untitled")

    return f"{author_str} ({year}). {title}."


def format_citation_mla(paper: dict) -> str:
    """Format a paper citation in MLA style."""
    authors = paper.get("authors", [])
    if not authors:
        author_str = "Unknown Author"
    else:
        author_str = authors[0]

    title = paper.get("title", "Untitled")
    year = paper.get("year", "")

    return f'{author_str}. "{title}." {year}.'


def format_citation_chicago(paper: dict) -> str:
    """Format a paper citation in Chicago style."""
    authors = paper.get("authors", [])
    if not authors:
        author_str = "Unknown Author"
    else:
        author_str = ", ".join(authors)

    title = paper.get("title", "Untitled")
    year = paper.get("year", "")

    return f'{author_str}. "{title}." {year}.'


def generate_citations(papers: list, style: str = "APA") -> list:
    """Generate formatted citations for all papers."""
    citations = []

    format_func = {
        "APA": format_citation_apa,
        "MLA": format_citation_mla,
        "Chicago": format_citation_chicago,
    }.get(style.upper(), format_citation_apa)

    for paper in papers:
        formatted = format_func(paper)
        citations.append(
            Citation(
                paper_id=paper.get("url", paper["title"]),
                style=style,
                formatted=formatted,
            )
        )

    return citations


def citation_manager_node(state: ResearchState) -> ResearchState:
    """Generate and format citations for the research paper."""
    if not state.get("search_results"):
        return {**state, "status": "error", "error": "No papers to cite"}

    # Default to APA style, could be made configurable
    citation_style = "APA"
    citations = generate_citations(state["search_results"], citation_style)

    return {
        **state,
        "citations": citations,
        "status": "complete",
        "current_node": "end",
    }
