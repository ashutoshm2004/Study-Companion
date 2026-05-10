from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ── Upload ────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    num_chunks: int
    message: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    num_chunks: int
    uploaded_at: str


class DocumentsListResponse(BaseModel):
    documents: list[DocumentInfo]


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    document_id: str
    message: str
    chat_history: list[ChatMessage] = []


class SourceChunk(BaseModel):
    text: str
    page: Optional[int] = None
    relevance_score: float


class ChatResponse(BaseModel):
    response: str
    sources: list[SourceChunk]
    tokens_used: int


# ── Flashcards ────────────────────────────────────────────────────────────────

class DifficultyLevel(str, Enum):
    easy   = "easy"
    medium = "medium"
    hard   = "hard"


class FlashcardRequest(BaseModel):
    document_id: str
    num_cards: int = Field(default=10, ge=1, le=30)
    topic_filter: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.medium


class Flashcard(BaseModel):
    question: str
    answer: str
    difficulty: DifficultyLevel
    hint: Optional[str] = None


class FlashcardResponse(BaseModel):
    cards: list[Flashcard]
    topic_covered: str


# ── Quiz ──────────────────────────────────────────────────────────────────────

class QuizRequest(BaseModel):
    document_id: str
    num_questions: int = Field(default=5, ge=1, le=20)
    difficulty: DifficultyLevel = DifficultyLevel.medium
    topic_filter: Optional[str] = None


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str
    source_hint: str


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]
    topic: str


# ── Mind Map ──────────────────────────────────────────────────────────────────

class MindMapRequest(BaseModel):
    document_id: str


class MindMapNode(BaseModel):
    id: str
    label: str
    group: str
    size: int = 20


class MindMapEdge(BaseModel):
    source: str
    target: str
    label: str
    weight: float = 1.0


class MindMapResponse(BaseModel):
    nodes: list[MindMapNode]
    edges: list[MindMapEdge]
    title: str


# ── Topic Analysis ────────────────────────────────────────────────────────────

class TopicAnalysisRequest(BaseModel):
    document_id: str


class SubTopic(BaseModel):
    name: str
    summary: str


class Topic(BaseModel):
    name: str
    importance_score: float
    summary: str
    subtopics: list[SubTopic]
    key_terms: list[str]


class TopicAnalysisResponse(BaseModel):
    topics: list[Topic]
    document_summary: str
    total_topics: int


# ── Mock Questions ────────────────────────────────────────────────────────────

class MockQuestionRequest(BaseModel):
    document_id: str
    num_questions: int = Field(default=3, ge=1, le=10)
    question_type: str = "essay"


class MockQuestion(BaseModel):
    question: str
    guidance: str
    marks: int


class MockQuestionsResponse(BaseModel):
    questions: list[MockQuestion]
    topic: str


class EvaluateAnswerRequest(BaseModel):
    document_id: str
    question: str
    student_answer: str
    marks: int = 10


class EvaluationResult(BaseModel):
    model_config = {"protected_namespaces": ()}   # fixes pydantic model_ warning

    score: int
    max_score: int
    percentage: float
    grade: str
    strengths: list[str]
    improvements: list[str]
    model_answer: str
    feedback: str


# ── Session ───────────────────────────────────────────────────────────────────

class SessionSummaryRequest(BaseModel):
    document_id: str
    chat_history: list[ChatMessage]
    quiz_scores: list[dict] = []


class SessionSummaryResponse(BaseModel):
    summary: str
    topics_covered: list[str]
    weak_areas: list[str]
    strong_areas: list[str]
    recommended_next: list[str]
    overall_score: Optional[float] = None
