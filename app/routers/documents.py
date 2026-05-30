import shutil
from pathlib import Path
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document, User
from app.routers.auth import get_current_user
from app.services.pdf_parser import extract_pdf
from app.services.text_cleaner import clean_document
from app.services.chunker import chunk_document
from app.services.vector_store import build_and_save, load_store
from app.services.retriever import retrieve, retrieve_multi
from app.models.schemas import UploadResponse
from app.core.config import get_settings
from app.core.logger import get_logger

router = APIRouter(prefix="/documents", tags=["Documents"])
settings = get_settings()
logger = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RAG Pipeline execution: PDF -> parsing -> cleaning -> chunking -> vectorizing -> FAISS.
    Also logs the document metadata under the logged-in user session in SQLite.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "PDF file required")

    content = await file.read()
    size_bytes = len(content)
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > settings.max_pdf_size_mb:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File too large (max {settings.max_pdf_size_mb}MB)"
        )

    doc_id = str(uuid.uuid4())[:8]

    # Save PDF to disk
    settings.upload_dir.mkdir(exist_ok=True)
    pdf_path = settings.upload_dir / f"{doc_id}_{file.filename}"
    pdf_path.write_bytes(content)

    try:
        logger.info(f"Starting parsing pipeline for document {file.filename} (User ID: {current_user.id})")

        # Parse, clean, and chunk
        raw_doc = extract_pdf(pdf_path)
        clean_doc = clean_document(raw_doc)
        chunks = chunk_document(clean_doc)
        
        # Embed and index inside FAISS
        build_and_save(chunks, doc_id)

        # Log document metadata in database
        db_doc = Document(
            id=doc_id,
            user_id=current_user.id,
            filename=file.filename,
            file_path=str(pdf_path),
            file_size=size_bytes,
            num_pages=raw_doc.total_pages,
            num_chunks=len(chunks)
        )
        db.add(db_doc)
        db.commit()

        return UploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            num_pages=raw_doc.total_pages,
            num_chunks=len(chunks),
            message=f"Document successfully indexed: {len(chunks)} chunks created",
        )

    except Exception as e:
        pdf_path.unlink(missing_ok=True)
        # Clean up any partial vector stores
        shutil.rmtree(settings.vectorstore_dir / doc_id, ignore_errors=True)
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Processing error: {str(e)}")


@router.get("", response_model=List[dict])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents uploaded by the current user."""
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return [
        {
            "doc_id": doc.id,
            "filename": doc.filename,
            "file_size": doc.file_size,
            "num_pages": doc.num_pages,
            "num_chunks": doc.num_chunks,
            "upload_date": doc.upload_date.isoformat() if doc.upload_date else None
        }
        for doc in docs
    ]


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document, its source PDF file, and its FAISS vectorstore index."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    # Delete PDF file
    pdf_path = Path(doc.file_path)
    pdf_path.unlink(missing_ok=True)

    # Delete FAISS vectorstore
    shutil.rmtree(settings.vectorstore_dir / doc_id, ignore_errors=True)

    # Delete database record
    db.delete(doc)
    db.commit()

    return {"message": "Document and indexes successfully deleted"}


@router.get("/search", response_model=List[dict])
async def semantic_search(
    query: str,
    doc_id: str,  # specific doc_id or "all"
    top_k: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform semantic search across document chunks without generating answers.
    Useful for quick lookup and research.
    """
    if len(query.strip()) < 3:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Query must be at least 3 characters")

    # Fetch document stores
    if doc_id == "all":
        user_docs = db.query(Document).filter(Document.user_id == current_user.id).all()
        if not user_docs:
            return []
        stores = []
        for d in user_docs:
            try:
                stores.append(load_store(d.id))
            except FileNotFoundError:
                continue
        results = retrieve_multi(stores, query, top_k)
    else:
        doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
        try:
            store = load_store(doc.id)
        except FileNotFoundError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vector index not found")
        results = retrieve(store, query, top_k)

    return [
        {
            "text": chunk.text,
            "page": chunk.page_number,
            "filename": chunk.source_file,
            "score": round(score, 3)
        }
        for chunk, score in results
    ]