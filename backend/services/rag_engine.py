"""RAG engine — every feature goes through retrieve → prompt → Groq."""
import logging
from backend.services.embedder import embed_query
from backend.services.vector_store import retrieve_chunks, retrieve_all_chunks
from backend.services.llm_client import chat, chat_json, build_context
from backend.config import TOP_K_RETRIEVAL

logger = logging.getLogger(__name__)

# ── Tutor Chat ────────────────────────────────────────────────────────────────

TUTOR_SYS = """You are a patient, encouraging study tutor helping a student understand their course material.
- Explain clearly using analogies and real-world examples
- Break complex ideas into simple steps  
- Be warm and supportive
- Base answers ONLY on the provided document excerpts
- If the answer is not in the document, say so honestly
- End conceptual answers with one follow-up question to check understanding"""

def tutor_chat(document_id, message, chat_history):
    chunks = retrieve_chunks(document_id, embed_query(message), top_k=TOP_K_RETRIEVAL)
    context = build_context(chunks)
    msgs = [{"role": m["role"], "content": m["content"]} for m in chat_history[-6:]]
    msgs.append({"role": "user", "content": f"{context}\n\nStudent question: {message}"})
    response, tokens = chat(TUTOR_SYS, msgs, max_tokens=1024)
    return response, chunks, tokens

# ── Flashcards ────────────────────────────────────────────────────────────────

def generate_flashcards(document_id, num_cards=10, topic_filter=None, difficulty="medium"):
    query = topic_filter or "key concepts definitions important terms"
    chunks = retrieve_chunks(document_id, embed_query(query), top_k=5)
    context = build_context(chunks)
    diff_desc = {"easy": "simple recall of definitions", "medium": "mix of recall and comprehension", "hard": "application and analysis"}
    system = f"""You are an educator making {difficulty} difficulty flashcards ({diff_desc.get(difficulty, '')}).
Create exactly {num_cards} flashcards from the excerpts.
Return ONLY this JSON:
{{"topic_covered": "topic name", "cards": [{{"question": "...", "answer": "...", "difficulty": "{difficulty}", "hint": "..."}}]}}"""
    result, tokens = chat_json(system, [{"role": "user", "content": f"{context}\n\nGenerate {num_cards} flashcards."}], max_tokens=2048)
    return result.get("cards", []), result.get("topic_covered", "Course Material"), tokens

# ── Quiz ──────────────────────────────────────────────────────────────────────

def generate_quiz(document_id, num_questions=5, difficulty="medium", topic_filter=None):
    query = topic_filter or "key concepts main ideas important facts"
    chunks = retrieve_chunks(document_id, embed_query(query), top_k=5)
    context = build_context(chunks)
    system = f"""You are an exam question writer. Create {num_questions} {difficulty} MCQ questions from the excerpts.
Return ONLY this JSON:
{{"topic": "topic name", "questions": [{{"question": "...", "options": ["A","B","C","D"], "correct_index": 0, "explanation": "...", "source_hint": "..."}}]}}
correct_index is 0-based. Make wrong options plausible."""
    result, tokens = chat_json(system, [{"role": "user", "content": f"{context}\n\nCreate {num_questions} {difficulty} MCQ questions."}], max_tokens=2048)
    return result.get("questions", []), result.get("topic", "Course Material"), tokens

# ── Mind Map ──────────────────────────────────────────────────────────────────

def generate_mind_map(document_id):
    chunks = retrieve_all_chunks(document_id, max_chunks=15)
    context = build_context(chunks)
    system = """Extract a concept knowledge graph from the document.
Return ONLY this JSON:
{"title": "doc title", "nodes": [{"id": "n1", "label": "Short Label", "group": "main", "size": 40}], "edges": [{"source": "n1", "target": "n2", "label": "relates to", "weight": 1.0}]}
Groups: main (size 40, 5-8 nodes), sub (size 25, 8-15 nodes). Labels max 4 words. Every node needs an edge."""
    result, tokens = chat_json(system, [{"role": "user", "content": f"{context}\n\nExtract the concept graph."}], max_tokens=2048)
    return result.get("nodes", []), result.get("edges", []), result.get("title", "Concept Map"), tokens

# ── Topic Analysis ────────────────────────────────────────────────────────────

def analyze_topics(document_id):
    chunks = retrieve_all_chunks(document_id, max_chunks=20)
    context = build_context(chunks)
    system = """Analyse the document and extract structured topics.
Return ONLY this JSON:
{"document_summary": "2-3 sentence overview", "topics": [{"name": "...", "importance_score": 0.9, "summary": "2-3 sentences", "subtopics": [{"name": "...", "summary": "..."}], "key_terms": ["term1"]}]}
importance_score: 1.0=most central, 0.3=minor. Order by importance. Aim for 4-7 topics."""
    result, tokens = chat_json(system, [{"role": "user", "content": f"{context}\n\nAnalyse topics."}], max_tokens=2048)
    return result.get("topics", []), result.get("document_summary", ""), tokens

# ── Mock Questions ────────────────────────────────────────────────────────────

def generate_mock_questions(document_id, num_questions=3, question_type="essay"):
    chunks = retrieve_chunks(document_id, embed_query("important concepts theories applications"), top_k=5)
    context = build_context(chunks)
    type_desc = {"essay": "open-ended 300-500 word answers", "short_answer": "focused 100-200 word answers", "case_study": "scenario-based applying concepts"}
    system = f"""Create {num_questions} {question_type} exam questions ({type_desc.get(question_type, '')}) from the document.
Return ONLY this JSON:
{{"topic": "topic name", "questions": [{{"question": "...", "guidance": "key points a good answer must include", "marks": 10}}]}}"""
    result, tokens = chat_json(system, [{"role": "user", "content": f"{context}\n\nCreate {num_questions} {question_type} questions."}], max_tokens=1500)
    return result.get("questions", []), result.get("topic", "Course Material"), tokens

def evaluate_answer(document_id, question, student_answer, marks=10):
    chunks = retrieve_chunks(document_id, embed_query(question), top_k=4)
    context = build_context(chunks)
    system = f"""You are a fair examiner grading a student answer out of {marks} marks.
Criteria: accuracy, completeness, clarity, depth.
Return ONLY this JSON:
{{"score": 7, "max_score": {marks}, "percentage": 70.0, "grade": "B", "strengths": ["..."], "improvements": ["..."], "model_answer": "ideal 150-200 word answer", "feedback": "encouraging feedback paragraph"}}
Grade scale: A=90-100, B=80-89, C=70-79, D=60-69, F=below 60"""
    result, tokens = chat_json(system, [{"role": "user", "content": f"{context}\n\nQuestion: {question}\n\nStudent Answer:\n{student_answer}\n\nGrade this answer."}], max_tokens=1500)
    return result, tokens

# ── Session Summary ───────────────────────────────────────────────────────────

def generate_session_summary(document_id, chat_history, quiz_scores=None):
    history_text = "\n".join(f"{m['role'].upper()}: {m['content'][:200]}" for m in chat_history[-10:])
    score_text = f"\nQuiz: {quiz_scores}" if quiz_scores else ""
    system = """You are a study coach reviewing a student's session.
Return ONLY this JSON:
{"summary": "2-3 sentence overview", "topics_covered": ["..."], "strong_areas": ["..."], "weak_areas": ["..."], "recommended_next": ["..."], "overall_score": null}"""
    result, tokens = chat_json(system, [{"role": "user", "content": f"Transcript:\n{history_text}{score_text}\n\nGenerate summary."}], max_tokens=1024)
    return result, tokens
