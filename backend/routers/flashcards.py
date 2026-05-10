import logging
from fastapi import APIRouter, HTTPException
from models.schemas import FlashcardRequest, FlashcardResponse, Flashcard, DifficultyLevel
from services.rag_engine import generate_flashcards
from services.vector_store import document_exists

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])
logger = logging.getLogger(__name__)

@router.post("", response_model=FlashcardResponse)
async def create_flashcards(request: FlashcardRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found.")
    try:
        cards, topic, _ = generate_flashcards(
            request.document_id, request.num_cards, request.topic_filter, request.difficulty.value)
        if not cards:
            raise HTTPException(500, "No flashcards generated. Try again.")
        result = []
        for c in cards:
            try:
                diff = DifficultyLevel(c.get("difficulty", request.difficulty.value))
            except ValueError:
                diff = request.difficulty
            result.append(Flashcard(question=c.get("question",""), answer=c.get("answer",""), difficulty=diff, hint=c.get("hint")))
        return FlashcardResponse(cards=result, topic_covered=topic)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Flashcard generation failed: {e}")
