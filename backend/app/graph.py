"""
LangGraph workflow orchestration for research paper generation.
"""

from langgraph.graph import END, StateGraph

from app.edges.routing import (
    route_after_analysis,
    route_after_citation,
    route_after_search,
    route_after_synthesis,
    route_after_writing,
)
from app.nodes.citation_manager import citation_manager_node
from app.nodes.data_synthesis import data_synthesis_node
from app.nodes.literature_search import literature_search_node
from app.nodes.paper_analysis import paper_analysis_node
from app.nodes.writer import writer_node
from app.state.research_state import ResearchState


def create_research_graph():
    """Create the LangGraph workflow for research paper generation."""

    workflow = StateGraph(ResearchState)

    workflow.add_node("literature_search", literature_search_node)
    workflow.add_node("paper_analysis", paper_analysis_node)
    workflow.add_node("data_synthesis", data_synthesis_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("citation_manager", citation_manager_node)

    workflow.add_conditional_edges(
        "literature_search",
        route_after_search,
        {
            "paper_analysis": "paper_analysis",
            "expand_search": "literature_search",
            "error_handler": END,
        },
    )

    workflow.add_conditional_edges(
        "paper_analysis",
        route_after_analysis,
        {
            "data_synthesis": "data_synthesis",
            "retry_analysis": "paper_analysis",
            "error_handler": END,
        },
    )

    workflow.add_conditional_edges(
        "data_synthesis",
        route_after_synthesis,
        {"writer": "writer", "error_handler": END},
    )

    workflow.add_conditional_edges(
        "writer",
        route_after_writing,
        {"citation_manager": "citation_manager", "error_handler": END},
    )

    workflow.add_conditional_edges(
        "citation_manager",
        route_after_citation,
        {
            "document_generation": END,
            "error_handler": END,
        },
    )

    workflow.set_entry_point("literature_search")

    return workflow.compile()


research_graph = create_research_graph()


def run_research_workflow(initial_state: ResearchState):
    """Run the research workflow with the given initial state."""
    return research_graph.invoke(initial_state)
