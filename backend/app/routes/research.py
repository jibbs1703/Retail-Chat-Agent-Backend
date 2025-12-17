"""
Research API endpoints.
"""

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.graph import run_research_workflow
from app.state.models import ResearchRequest, ResearchStatus
from app.state.research_state import ResearchState

router = APIRouter()

job_store: dict[str, ResearchState] = {}


@router.post("/start", response_model=ResearchStatus)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research workflow."""
    job_id = str(uuid.uuid4())

    # Initialize state
    initial_state: ResearchState = {
        "topic": request.topic,
        "search_results": [],
        "analyzed_papers": [],
        "synthesis": None,
        "paper_sections": {},
        "citations": [],
        "status": "starting",
        "current_node": "literature_search",
        "error": None,
    }

    # Store initial state
    job_store[job_id] = initial_state

    # Run workflow in background
    background_tasks.add_task(run_workflow_background, job_id, initial_state)

    return ResearchStatus(
        job_id=job_id,
        status="starting",
        progress=0.0,
        current_stage="Initializing research workflow",
        message=f"Starting research on: {request.topic}",
    )


@router.get("/status/{job_id}", response_model=ResearchStatus)
async def get_research_status(job_id: str):
    """Get the status of a research job."""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    state = job_store[job_id]

    # Calculate progress based on status
    progress_map = {
        "starting": 0.0,
        "searching": 0.2,
        "analyzing": 0.4,
        "synthesizing": 0.6,
        "writing": 0.8,
        "citing": 0.9,
        "complete": 1.0,
        "error": 0.0,
    }

    progress = progress_map.get(state["status"], 0.0)

    return ResearchStatus(
        job_id=job_id,
        status=state["status"],
        progress=progress,
        current_stage=state["current_node"],
        message=state.get("error")
        if state.get("error")
        else f"Processing: {state['current_node']}",
    )


@router.post("/email/{job_id}")
async def send_research_email(job_id: str, email: str):
    """Send completed research via email."""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    state = job_store[job_id]
    if state["status"] != "complete":
        raise HTTPException(status_code=400, detail="Research not yet complete")

    # TODO: Implement email sending
    # This would integrate with the email service

    return {"message": f"Email sent to {email}"}


@router.get("/history")
async def get_research_history():
    """Get history of completed research jobs."""
    completed_jobs = [
        {
            "job_id": job_id,
            "topic": state["topic"],
            "status": state["status"],
            "completed_at": None,  # TODO: Add timestamps
        }
        for job_id, state in job_store.items()
        if state["status"] == "complete"
    ]
    return {"jobs": completed_jobs}


def run_workflow_background(job_id: str, initial_state: ResearchState):
    """Run the workflow in the background and update job status."""
    try:
        final_state = run_research_workflow(initial_state)
        job_store[job_id] = final_state
    except (RuntimeError, ValueError, KeyError) as e:
        # Update state with error
        error_state = initial_state.copy()
        error_state["status"] = "error"
        error_state["error"] = str(e)
        job_store[job_id] = error_state
