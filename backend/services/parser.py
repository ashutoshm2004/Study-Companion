"""Parse PDF / DOCX / TXT → list of {text, page} dicts."""
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_document(file_bytes: bytes, filename: str) -> list[dict]:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _parse_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return _parse_docx(file_bytes)
    elif ext == ".txt":
        return _parse_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF, DOCX, or TXT.")


def _parse_pdf(file_bytes: bytes) -> list[dict]:
    import fitz  # PyMuPDF
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for i in range(len(doc)):
        text = doc[i].get_text("text").strip()
        if text:
            pages.append({"text": text, "page": i + 1})
    doc.close()
    if not pages:
        raise ValueError(
            "No text found in PDF. It may be a scanned image — "
            "please use an OCR tool first."
        )
    return pages


def _parse_docx(file_bytes: bytes) -> list[dict]:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    if not text:
        raise ValueError("No text found in DOCX file.")
    return [{"text": text, "page": 1}]


def _parse_txt(file_bytes: bytes) -> list[dict]:
    try:
        text = file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1").strip()
    if not text:
        raise ValueError("TXT file is empty.")
    return [{"text": text, "page": 1}]


def chunk_pages(pages: list[dict], chunk_size: int = 800, overlap: int = 100) -> list[dict]:
    chunks, idx = [], 0
    for page in pages:
        words = page["text"].split()
        start = 0
        while start < len(words):
            chunk_text = " ".join(words[start : start + chunk_size])
            if len(chunk_text.strip()) > 50:
                chunks.append({"text": chunk_text, "page": page["page"], "chunk_index": idx})
                idx += 1
            start += chunk_size - overlap
    return chunks
