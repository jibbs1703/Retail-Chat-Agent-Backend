"""Data synthesis node for the research workflow."""

from langchain_ollama import ChatOllama

from app.core.config import get_settings
from app.state.research_state import ResearchState, Synthesis

settings = get_settings()


def synthesize_data(analyses: list) -> Synthesis:
    """Synthesize insights from multiple paper analyses."""
    llm = ChatOllama(model=settings.OLLAMA_MODEL, temperature=0.1)

    # Compile all analyses into a single text
    analysis_text = "\n\n".join(
        [
            f"Paper: {analysis['paper_id']}\n"
            f"Summary: {analysis['summary']}\n"
            f"Key Findings: {'; '.join(analysis['key_findings'])}\n"
            f"Methodology: {analysis['methodology']}\n"
            f"Limitations: {'; '.join(analysis['limitations'])}"
            for analysis in analyses
        ]
    )

    prompt = f"""
    Synthesize the following research paper analyses into coherent insights:

    {analysis_text}

    Provide:
    1. Key insights (3-5 main findings across all papers)
    2. Common patterns or themes
    3. Research gaps identified
    4. Trends in the field

    Structure your response clearly.
    """

    response = llm.invoke(prompt)
    content = response.content

    # Simple parsing (in a real implementation, use better parsing)
    lines = content.split("\n")
    insights = []
    patterns = []
    gaps = []
    trends = {}

    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "insight" in line.lower() or "finding" in line.lower():
            current_section = "insights"
        elif "pattern" in line.lower() or "theme" in line.lower():
            current_section = "patterns"
        elif "gap" in line.lower():
            current_section = "gaps"
        elif "trend" in line.lower():
            current_section = "trends"
        elif line.startswith("-") or line.startswith("•"):
            item = line[1:].strip()
            if current_section == "insights":
                insights.append(item)
            elif current_section == "patterns":
                patterns.append(item)
            elif current_section == "gaps":
                gaps.append(item)

    return Synthesis(
        insights=insights, patterns=patterns, research_gaps=gaps, trends=trends
    )


def data_synthesis_node(state: ResearchState) -> ResearchState:
    """Synthesize data from analyzed papers."""
    if not state.get("analyzed_papers"):
        return {**state, "status": "error", "error": "No analyzed papers to synthesize"}

    synthesis = synthesize_data(state["analyzed_papers"])

    return {
        **state,
        "synthesis": synthesis,
        "status": "writing",
        "current_node": "writer",
    }
