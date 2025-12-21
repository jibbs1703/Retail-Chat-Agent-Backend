"""Paper analysis node for the research workflow."""

from langchain_ollama import ChatOllama

from app.core.config import get_settings
from app.state.research_state import Analysis, ResearchState

settings = get_settings()


def analyze_paper_content(paper: dict) -> Analysis:
    """Analyze a single paper's content."""
    llm = ChatOllama(model=settings.OLLAMA_MODEL, temperature=0.1)

    prompt = f"""
    Analyze this research paper and provide:
    1. A concise summary (2-3 sentences)
    2. Key findings (bullet points)
    3. Methodology used
    4. Limitations (if mentioned or apparent)

    Paper Title: {paper["title"]}
    Abstract: {paper["abstract"]}

    Provide your analysis in a structured format.
    """

    response = llm.invoke(prompt)

    content = response.content
    lines = content.split("\n")

    summary = ""
    key_findings = []
    methodology = ""
    limitations = []

    current_section = None
    for line in lines:
        line = line.strip()
        if line.lower().startswith("summary"):
            current_section = "summary"
        elif line.lower().startswith("key findings") or line.lower().startswith(
            "findings"
        ):
            current_section = "findings"
        elif line.lower().startswith("methodology"):
            current_section = "methodology"
        elif line.lower().startswith("limitations"):
            current_section = "limitations"
        elif line and current_section:
            if current_section == "summary":
                summary += line + " "
            elif current_section == "findings" and line.startswith("-"):
                key_findings.append(line[1:].strip())
            elif current_section == "methodology":
                methodology += line + " "
            elif current_section == "limitations" and line.startswith("-"):
                limitations.append(line[1:].strip())

    return Analysis(
        paper_id=paper.get("url", paper["title"]),
        summary=summary.strip(),
        key_findings=key_findings,
        methodology=methodology.strip(),
        limitations=limitations,
    )


def paper_analysis_node(state: ResearchState) -> ResearchState:
    """Analyze the collected research papers."""
    if not state.get("search_results"):
        return {**state, "status": "error", "error": "No papers found to analyze"}

    analyzed_papers = []
    for paper in state["search_results"][:5]:
        try:
            analysis = analyze_paper_content(paper)
            analyzed_papers.append(analysis)
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            print(f"Failed to analyze paper {paper['title']}: {e}")
            continue

    return {
        **state,
        "analyzed_papers": analyzed_papers,
        "status": "synthesizing",
        "current_node": "data_synthesis",
    }
