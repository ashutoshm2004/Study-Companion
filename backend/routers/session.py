import logging
from fastapi import APIRouter, HTTPException
from backend.models.schemas import SessionSummaryRequest, SessionSummaryResponse
from backend.services.rag_engine import generate_session_summary
from backend.services.vector_store import document_exists

router = APIRouter(prefix="/session", tags=["Session"])
logger = logging.getLogger(__name__)

@router.post("/summary", response_model=SessionSummaryResponse)
async def session_summary(request: SessionSummaryRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found.")
    if len(request.chat_history) < 2:
        raise HTTPException(400, "Need at least 2 messages to summarise.")
    try:
        history = [{"role": m.role, "content": m.content} for m in request.chat_history]
        result, _ = generate_session_summary(request.document_id, history, request.quiz_scores)
        return SessionSummaryResponse(
            summary=result.get("summary",""), topics_covered=result.get("topics_covered",[]),
            weak_areas=result.get("weak_areas",[]), strong_areas=result.get("strong_areas",[]),
            recommended_next=result.get("recommended_next",[]), overall_score=result.get("overall_score"))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Summary failed: {e}")
