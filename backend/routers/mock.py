import logging
from fastapi import APIRouter, HTTPException
from backend.models.schemas import MockQuestionRequest, MockQuestionsResponse, MockQuestion, EvaluateAnswerRequest, EvaluationResult
from backend.services.rag_engine import generate_mock_questions, evaluate_answer
from backend.services.vector_store import document_exists

router = APIRouter(prefix="/mock", tags=["Mock"])
logger = logging.getLogger(__name__)

@router.post("/questions", response_model=MockQuestionsResponse)
async def create_mock_questions(request: MockQuestionRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found.")
    try:
        questions, topic, _ = generate_mock_questions(request.document_id, request.num_questions, request.question_type)
        if not questions:
            raise HTTPException(500, "No questions generated. Try again.")
        qs = [MockQuestion(question=q.get("question",""), guidance=q.get("guidance",""), marks=int(q.get("marks",10))) for q in questions]
        return MockQuestionsResponse(questions=qs, topic=topic)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Mock questions failed: {e}")

@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_student_answer(request: EvaluateAnswerRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found.")
    if len(request.student_answer.strip()) < 20:
        raise HTTPException(400, "Answer too short (min 20 chars).")
    try:
        result, _ = evaluate_answer(request.document_id, request.question, request.student_answer, request.marks)
        score = int(result.get("score", 0))
        max_s = int(result.get("max_score", request.marks))
        return EvaluationResult(
            score=score, max_score=max_s,
            percentage=round(score / max_s * 100 if max_s else 0, 1),
            grade=result.get("grade","N/A"), strengths=result.get("strengths",[]),
            improvements=result.get("improvements",[]), model_answer=result.get("model_answer",""),
            feedback=result.get("feedback",""))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Evaluation failed: {e}")
