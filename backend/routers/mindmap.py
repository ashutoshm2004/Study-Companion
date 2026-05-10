import logging
from fastapi import APIRouter, HTTPException
from models.schemas import MindMapRequest, MindMapResponse, MindMapNode, MindMapEdge
from services.rag_engine import generate_mind_map
from services.vector_store import document_exists

router = APIRouter(prefix="/mindmap", tags=["Mind Map"])
logger = logging.getLogger(__name__)

@router.post("", response_model=MindMapResponse)
async def create_mind_map(request: MindMapRequest):
    if not document_exists(request.document_id):
        raise HTTPException(404, "Document not found.")
    try:
        nodes, edges, title, _ = generate_mind_map(request.document_id)
        if not nodes:
            raise HTTPException(500, "Empty mind map returned. Try again.")
        mind_nodes = [MindMapNode(id=n.get("id", f"n{i}"), label=n.get("label",""), group=n.get("group","sub"), size=int(n.get("size",20))) for i, n in enumerate(nodes)]
        mind_edges = [MindMapEdge(source=e.get("source",""), target=e.get("target",""), label=e.get("label",""), weight=float(e.get("weight",1.0))) for e in edges if e.get("source") and e.get("target")]
        return MindMapResponse(nodes=mind_nodes, edges=mind_edges, title=title)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, f"Mind map failed: {e}")
