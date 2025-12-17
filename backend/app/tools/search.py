"""Academic search tools."""

import arxiv
from duckduckgo_search import DDGS
from scholarly import scholarly


def search_arxiv_papers(query: str, max_results: int = 10) -> list[dict]:
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
                    "source": "arxiv",
                }
            )

        return results
    except (arxiv.ArxivError, ConnectionError, TimeoutError) as e:
        print(f"ArXiv search failed: {e}")
        return []


def search_web_academic(query: str, max_results: int = 5) -> list[dict]:
    """Search web for academic resources."""
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(query + " academic research", max_results=max_results)
            )
            return [
                {
                    "title": r["title"],
                    "url": r["href"],
                    "snippet": r["body"],
                    "source": "web",
                }
                for r in results
            ]
    except (ConnectionError, TimeoutError, KeyError) as e:
        print(f"Web search failed: {e}")
        return []


def search_scholarly_papers(query: str, max_results: int = 5) -> list[dict]:
    """Search Google Scholar for papers (limited due to API restrictions)."""
    try:
        search_query = scholarly.search_pubs(query)

        results = []
        for i, pub in enumerate(search_query):
            if i >= max_results:
                break

            results.append(
                {
                    "title": pub.get("bib", {}).get("title", "Unknown Title"),
                    "authors": pub.get("bib", {}).get("author", []),
                    "abstract": pub.get("bib", {}).get("abstract", ""),
                    "url": pub.get("pub_url", ""),
                    "year": pub.get("bib", {}).get("pub_year"),
                    "citations": pub.get("num_citations", 0),
                    "source": "scholarly",
                }
            )

        return results
    except (ImportError, ConnectionError, TimeoutError, StopIteration) as e:
        print(f"Scholarly search failed: {e}")
        return []


def comprehensive_search(query: str, max_results: int = 10) -> list[dict]:
    """Perform comprehensive search across multiple academic sources."""
    all_results = []

    arxiv_results = search_arxiv_papers(query, max_results // 2)
    all_results.extend(arxiv_results)

    scholar_results = search_scholarly_papers(query, max_results // 3)
    all_results.extend(scholar_results)

    web_results = search_web_academic(query, max_results // 3)
    all_results.extend(web_results)

    unique_results = []
    seen_titles = set()

    for result in all_results:
        title = result["title"].lower()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_results.append(result)

    return unique_results[:max_results]
