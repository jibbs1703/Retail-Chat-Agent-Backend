"""Literature search node for the research workflow."""

import arxiv
from duckduckgo_search import DDGS
from langchain_core.tools import tool

from app.state.research_state import Paper, ResearchState


@tool
def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    """Search arXiv for research papers."""
    try:
        search = arxiv.Search(
            query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for result in search.results():
            results.append(
                {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "url": result.pdf_url,
                    "year": result.published.year if result.published else None,
                    "citations": None,
                }
            )
        return results
    except (ConnectionError, TimeoutError) as e:
        print(f"ArXiv search failed: {e}")
        return []


@tool
def search_duckduckgo(query: str) -> list[dict]:
    """Search DuckDuckGo for academic resources."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            return [
                {"title": r["title"], "url": r["href"], "snippet": r["body"]}
                for r in results
            ]
    except (ConnectionError, TimeoutError, KeyError) as e:
        print(f"DuckDuckGo search failed: {e}")
        return []


def literature_search_node(state: ResearchState) -> ResearchState:
    """Execute literature search for the research topic."""
    search_query = f"{state['topic']} research papers academic literature"

    # Search multiple sources
    arxiv_results = search_arxiv(search_query, max_results=5)

    papers = []
    for result in arxiv_results:
        papers.append(
            Paper(
                title=result["title"],
                authors=result["authors"],
                abstract=result["abstract"],
                url=result["url"],
                year=result["year"],
                citations=result["citations"],
            )
        )

    # Update state
    return {
        **state,
        "search_results": papers,
        "status": "analyzing",
        "current_node": "paper_analysis",
    }
