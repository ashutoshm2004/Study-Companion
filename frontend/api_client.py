"""HTTP client — all Streamlit pages call the FastAPI backend through here."""
import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 180.0

CONTENT_TYPES = {
    "pdf":  "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc":  "application/msword",
    "txt":  "text/plain",
}

def _c():
    return httpx.Client(base_url=BACKEND_URL, timeout=TIMEOUT)

def health() -> bool:
    try:
        with _c() as c:
            return c.get("/health").status_code == 200
    except Exception:
        return False

def upload_document(file_bytes: bytes, filename: str) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    ct = CONTENT_TYPES.get(ext, "application/octet-stream")

    with _c() as c:
        r = c.post(
            "/upload",
            files={"file": (filename, file_bytes, ct)}
        )

        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text)

        r.raise_for_status()
        return r.json()

def list_documents() -> list:
    with _c() as c:
        r = c.get("/upload/documents")
        r.raise_for_status()
        return r.json().get("documents", [])

def delete_document(doc_id: str) -> dict:
    with _c() as c:
        r = c.delete(f"/upload/documents/{doc_id}")
        r.raise_for_status()
        return r.json()

def chat(document_id: str, message: str, history: list) -> dict:
    with _c() as c:
        r = c.post("/chat", json={"document_id": document_id, "message": message, "chat_history": history})
        r.raise_for_status()
        return r.json()

def get_flashcards(document_id: str, num_cards: int, difficulty: str, topic: str = None) -> dict:
    payload = {"document_id": document_id, "num_cards": num_cards, "difficulty": difficulty}
    if topic:
        payload["topic_filter"] = topic
    with _c() as c:
        r = c.post("/flashcards", json=payload)
        r.raise_for_status()
        return r.json()

def get_quiz(document_id: str, num_questions: int, difficulty: str, topic: str = None) -> dict:
    payload = {"document_id": document_id, "num_questions": num_questions, "difficulty": difficulty}
    if topic:
        payload["topic_filter"] = topic
    with _c() as c:
        r = c.post("/quiz", json=payload)
        r.raise_for_status()
        return r.json()

def get_mindmap(document_id: str) -> dict:
    with _c() as c:
        r = c.post("/mindmap", json={"document_id": document_id})
        r.raise_for_status()
        return r.json()

def get_topics(document_id: str) -> dict:
    with _c() as c:
        r = c.post("/topics", json={"document_id": document_id})
        r.raise_for_status()
        return r.json()

def get_mock_questions(document_id: str, num: int, qtype: str) -> dict:
    with _c() as c:
        r = c.post("/mock/questions", json={"document_id": document_id, "num_questions": num, "question_type": qtype})
        r.raise_for_status()
        return r.json()

def evaluate_answer(document_id: str, question: str, answer: str, marks: int) -> dict:
    with _c() as c:
        r = c.post("/mock/evaluate", json={"document_id": document_id, "question": question, "student_answer": answer, "marks": marks})
        r.raise_for_status()
        return r.json()

def get_session_summary(document_id: str, history: list, quiz_scores: list = None) -> dict:
    with _c() as c:
        r = c.post("/session/summary", json={"document_id": document_id, "chat_history": history, "quiz_scores": quiz_scores or []})
        r.raise_for_status()
        return r.json()
