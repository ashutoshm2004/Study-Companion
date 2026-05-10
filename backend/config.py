import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vector_store")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
MAX_FILE_SIZE_MB   = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
CHUNK_SIZE         = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP      = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K_RETRIEVAL    = int(os.getenv("TOP_K_RETRIEVAL", "5"))
