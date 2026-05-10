import logging
from fastapi import APIRouter, HTTPException
from models.schemas import TopicAnalysisRequest, TopicAnalysisResponse, Topic, SubTopic
from services.rag_engine import analyze_topics
from services.vector_store import document_exists

router = APIRouter(prefix="/topics", tags=["Topics"])
logger = logging.getLogger(__name__)

@router.post("", response_model=TopicAnalysisResponse)
async def topic_analysis(request: TopicAnalysisRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found.")
    try:
        topics, summary, _ = analyze_topics(request.document_id)
        structured = []
        for t in topics:
            subtopics = [SubTopic(name=s.get("name",""), summary=s.get("summary","")) for s in t.get("subtopics",[])]
            structured.append(Topic(name=t.get("name",""), importance_score=float(t.get("importance_score",0.5)),
                                    summary=t.get("summary",""), subtopics=subtopics, key_terms=t.get("key_terms",[])))
        return TopicAnalysisResponse(topics=structured, document_summary=summary, total_topics=len(structured))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Topic analysis failed: {e}")
