"""
Paper search API endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.state.models import PaperSearchRequest
from app.tools.database import search_papers_semantic

router = APIRouter()


@router.post("/search")
async def search_papers(request: PaperSearchRequest):
    """Perform semantic search for papers."""
    try:
        results = await search_papers_semantic(request.query, request.limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}") from e


@router.get("/paper/{paper_id}")
async def get_paper_details(paper_id: str):
    """Get detailed information about a specific paper."""
    # TODO: Implement paper detail retrieval from Qdrant
    return {"paper_id": paper_id, "message": "Not implemented yet"}
