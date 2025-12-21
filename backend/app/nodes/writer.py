"""Writer node for generating research paper content."""

from langchain_ollama import ChatOllama

from app.core.config import get_settings
from app.state.research_state import ResearchState

settings = get_settings()


def generate_paper_sections(topic: str, synthesis: dict, analyses: list) -> dict:
    """Generate structured research paper sections."""
    llm = ChatOllama(model=settings.OLLAMA_MODEL, temperature=0.1)

    sections = {}

    abstract_prompt = f"""
    Write a compelling abstract for a research paper on: {topic}

    Key insights: {", ".join(synthesis.get("insights", []))}
    Research gaps: {", ".join(synthesis.get("research_gaps", []))}

    The abstract should be 150-250 words, engaging, and highlight the significance.
    """

    sections["abstract"] = llm.invoke(abstract_prompt).content

    intro_prompt = f"""
    Write an introduction section for a research paper on: {topic}

    Include:
    1. Background and context
    2. Research problem/ question
    3. Significance of the study
    4. Brief overview of methodology

    Key insights from literature: {", ".join(synthesis.get("insights", []))}
    """

    sections["introduction"] = llm.invoke(intro_prompt).content

    lit_review_prompt = f"""
        Write a literature review section synthesizing {len(analyses)} research \
    papers on: {topic}
    
        Key findings from papers:
        {chr(10).join([f"- {analysis['summary']}" for analysis in analyses[:3]])}
    
        Common patterns: {", ".join(synthesis.get("patterns", []))}
        Research gaps: {", ".join(synthesis.get("research_gaps", []))}
        """

    sections["literature_review"] = llm.invoke(lit_review_prompt).content

    discussion_prompt = f"""
    Write a discussion section for the research paper on: {topic}

    Address:
    1. Interpretation of findings
    2. Implications for the field
    3. Addressing the research gaps
    4. Future research directions

    Key insights: {", ".join(synthesis.get("insights", []))}
    """

    sections["discussion"] = llm.invoke(discussion_prompt).content

    conclusion_prompt = f"""
    Write a conclusion section summarizing the research on: {topic}

    Include:
    1. Summary of key findings
    2. Contributions to the field
    3. Final thoughts

    Keep it concise and impactful.
    """

    sections["conclusion"] = llm.invoke(conclusion_prompt).content

    return sections


def writer_node(state: ResearchState) -> ResearchState:
    """Generate the research paper content."""
    if not state.get("synthesis") or not state.get("analyzed_papers"):
        return {
            **state,
            "status": "error",
            "error": "Missing synthesis or analyzed papers for writing",
        }

    paper_sections = generate_paper_sections(
        state["topic"], state["synthesis"], state["analyzed_papers"]
    )

    return {
        **state,
        "paper_sections": paper_sections,
        "status": "citing",
        "current_node": "citation_manager",
    }
