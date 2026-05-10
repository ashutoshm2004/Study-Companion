import logging
from fastapi import APIRouter, HTTPException
from backend.models.schemas import QuizRequest, QuizResponse, QuizQuestion
from backend.services.rag_engine import generate_quiz
from backend.services.vector_store import document_exists

router = APIRouter(prefix="/quiz", tags=["Quiz"])
logger = logging.getLogger(__name__)

@router.post("", response_model=QuizResponse)
async def create_quiz(request: QuizRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found.")
    try:
        questions, topic, _ = generate_quiz(
            request.document_id, request.num_questions, request.difficulty.value, request.topic_filter)
        if not questions:
            raise HTTPException(500, "No questions generated. Try again.")
        result = []
        for q in questions:
            opts = q.get("options", [])
            idx  = max(0, min(int(q.get("correct_index", 0)), len(opts) - 1))
            result.append(QuizQuestion(question=q.get("question",""), options=opts, correct_index=idx,
                                       explanation=q.get("explanation",""), source_hint=q.get("source_hint","")))
        return QuizResponse(questions=result, topic=topic)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Quiz generation failed: {e}")
