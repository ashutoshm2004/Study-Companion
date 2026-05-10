import logging
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse, SourceChunk
from backend.services.rag_engine import tutor_chat
from backend.services.vector_store import document_exists

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found. Upload it first.")
    if not request.message.strip():
        raise HTTPException(400, "Message cannot be empty.")
    try:
        history = [{"role": m.role, "content": m.content} for m in request.chat_history]
        response, chunks, tokens = tutor_chat(request.document_id, request.message, history)
        sources = [
            SourceChunk(text=c["text"][:300] + "..." if len(c["text"]) > 300 else c["text"],
                        page=c.get("page"), relevance_score=c.get("relevance_score", 0.0))
            for c in chunks
        ]
        return ChatResponse(response=response, sources=sources, tokens_used=tokens)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Chat failed: {e}")
