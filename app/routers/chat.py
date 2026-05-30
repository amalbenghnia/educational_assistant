import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ChatMessage, Document, User
from app.routers.auth import get_current_user
from app.services.vector_store import load_store
from app.services.retriever import retrieve, retrieve_multi, format_context
from app.services.prompt_builder import SYSTEM_PROMPT, build_qa_prompt
from app.services.llm_engine import generate_response, generate_stream
from app.models.schemas import QuestionRequest, AnswerResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


def format_history_db(db: Session, user_id: int, session_id: str, max_turns: int = 5) -> str:
    """Format the last N turns of the chat history from the DB for inclusion in the RAG prompt."""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id,
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp.asc()).all()

    # limit to last N turns (1 turn = 1 user + 1 assistant message)
    limit = max_turns * 2
    recent_messages = messages[-limit:] if len(messages) > limit else messages

    lines = []
    for msg in recent_messages:
        role_label = "Student" if msg.role == "user" else "Assistant"
        lines.append(f"{role_label}: {msg.content}")

    return "\n".join(lines)


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Primary RAG Q&A endpoint: processes questions, loads context, includes 
    conversational memory, queries Llama 3, and saves history.
    """
    # Fetch document stores
    if request.doc_id == "all":
        user_docs = db.query(Document).filter(Document.user_id == current_user.id).all()
        if not user_docs:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No documents uploaded yet.")
        stores = []
        for d in user_docs:
            try:
                stores.append(load_store(d.id))
            except FileNotFoundError:
                continue
        if not stores:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No vector indexes found.")
        results = retrieve_multi(stores, request.question, request.top_k)
    else:
        doc = db.query(Document).filter(Document.id == request.doc_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Document {request.doc_id} not found")
        try:
            store = load_store(doc.id)
        except FileNotFoundError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Vector index for {doc.filename} not found")
        results = retrieve(store, request.question, request.top_k)

    context = format_context(results)

    # Retrieve conversation history from DB
    history = format_history_db(db, current_user.id, request.session_id)

    # Build prompt with history
    if history:
        enriched_question = (
            f"CONVERSATION HISTORY:\n{history}\n\n"
            f"NEW STUDENT QUESTION: {request.question}"
        )
    else:
        enriched_question = request.question

    prompt = build_qa_prompt(enriched_question, context)
    answer = generate_response(prompt, SYSTEM_PROMPT)

    # Serialize sources
    sources = [
        {
            "file": chunk.source_file,
            "page": chunk.page_number,
            "score": round(score, 3),
            "preview": chunk.text[:150] + "...",
        }
        for chunk, score in results
    ]

    # Save conversation log to SQLite
    user_msg = ChatMessage(
        user_id=current_user.id,
        session_id=request.session_id,
        role="user",
        content=request.question
    )
    assistant_msg = ChatMessage(
        user_id=current_user.id,
        session_id=request.session_id,
        role="assistant",
        content=answer,
        sources=json.dumps(sources)
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()

    return AnswerResponse(
        answer=answer,
        sources=sources,
        session_id=request.session_id,
    )


@router.post("/ask/stream")
async def ask_question_stream(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streaming Q&A: yields answers token by token.
    Note: Currently skips database logging as it serves simple text streaming.
    """
    if request.doc_id == "all":
        user_docs = db.query(Document).filter(Document.user_id == current_user.id).all()
        stores = []
        for d in user_docs:
            try:
                stores.append(load_store(d.id))
            except FileNotFoundError:
                continue
        results = retrieve_multi(stores, request.question, request.top_k)
    else:
        doc = db.query(Document).filter(Document.id == request.doc_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
        store = load_store(doc.id)
        results = retrieve(store, request.question, request.top_k)

    context = format_context(results)
    prompt = build_qa_prompt(request.question, context)

    return StreamingResponse(
        generate_stream(prompt, SYSTEM_PROMPT),
        media_type="text/plain",
    )


@router.get("/history/{session_id}", response_model=List[dict])
async def get_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve message logs for a specific session."""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp.asc()).all()

    return [
        {
            "role": msg.role,
            "content": msg.content,
            "sources": json.loads(msg.sources) if msg.sources else [],
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]


@router.post("/clear/{session_id}")
async def clear_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all message history for a given session."""
    db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.session_id == session_id
    ).delete()
    db.commit()
    return {"message": "Chat history cleared successfully"}