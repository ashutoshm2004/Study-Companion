"""AI Study Companion — FastAPI backend (Groq + sentence-transformers, 100% free)"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, chat, flashcards, quiz, mindmap, topics, mock, session

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI(title="AI Study Companion", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

for router in [upload.router, chat.router, flashcards.router, quiz.router,
               mindmap.router, topics.router, mock.router, session.router]:
    app.include_router(router)

@app.get("/health")
def health():
    from config import GROQ_MODEL
    return {"status": "ok", "model": GROQ_MODEL}

@app.get("/")
def root():
    return {"message": "AI Study Companion API v2", "docs": "/docs"}
