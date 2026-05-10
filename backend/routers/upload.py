import uuid, logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from backend.models.schemas import UploadResponse, DocumentsListResponse, DocumentInfo
from backend.services.parser import parse_document, chunk_pages
from backend.services.embedder import embed_texts
from backend.services.vector_store import store_chunks, list_documents, delete_document, document_exists
from backend.config import MAX_FILE_SIZE_MB, CHUNK_SIZE, CHUNK_OVERLAP

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = logging.getLogger(__name__)

ALLOWED_EXTS = {"pdf", "docx", "doc", "txt"}


@router.post("", response_model=UploadResponse)
async def upload_document(request: Request):
    """
    Accept multipart/form-data file upload.
    Manually parse the form so we are not dependent on FastAPI's UploadFile
    validation, which can give spurious 422s on some client versions.
    """
    try:
        form = await request.form()
    except Exception as e:
        raise HTTPException(400, f"Could not parse form data: {e}")

    if "file" not in form:
        raise HTTPException(422, "No 'file' field found in the request. Make sure you are sending multipart/form-data with field name 'file'.")

    upload = form["file"]

    # Depending on FastAPI/Starlette version, upload may be UploadFile or str
    if isinstance(upload, str):
        raise HTTPException(422, "File field is a string, not a file. Send as multipart/form-data.")

    filename = upload.filename or "unknown"
    content  = await upload.read()

    # Size check
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(413, f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB.")

    # Extension check
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"Unsupported file type '.{ext}'. Allowed: pdf, docx, txt.")

    if not content:
        raise HTTPException(422, "Uploaded file is empty.")

    try:
        logger.info(f"Processing: {filename} ({size_mb:.2f} MB)")
        pages  = parse_document(content, filename)
        chunks = chunk_pages(pages, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

        if not chunks:
            raise HTTPException(422, "No readable text found in document. If it's a scanned PDF, run OCR first.")

        logger.info(f"Embedding {len(chunks)} chunks...")
        embeddings = embed_texts([c["text"] for c in chunks])

        doc_id = str(uuid.uuid4())[:8]
        store_chunks(doc_id, chunks, embeddings, filename)
        logger.info(f"Stored doc {doc_id} — {len(chunks)} chunks")

        return UploadResponse(
            document_id=doc_id,
            filename=filename,
            num_chunks=len(chunks),
            message=f"'{filename}' processed into {len(chunks)} searchable chunks.",
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        logger.exception(f"Upload error: {e}")
        raise HTTPException(500, f"Processing failed: {e}")


@router.get("/documents", response_model=DocumentsListResponse)
async def get_documents():
    return DocumentsListResponse(documents=[DocumentInfo(**d) for d in list_documents()])


@router.delete("/documents/{document_id}")
async def remove_document(document_id: str):
    if not document_exists(document_id):
        raise HTTPException(404, "Document not found.")
    if not delete_document(document_id):
        raise HTTPException(500, "Delete failed.")
    return {"message": f"Document {document_id} deleted."}