import re
import json
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document, User, Summary, Quiz, ExamPrep
from app.routers.auth import get_current_user
from app.services.vector_store import load_store
from app.services.retriever import retrieve, format_context
from app.services.prompt_builder import (
    build_summary_prompt,
    build_quiz_prompt,
    build_flashcard_prompt,
    build_exam_prep_prompt
)
from app.services.llm_engine import generate_response
from app.models.schemas import SummaryRequest, QuizRequest, FlashcardRequest, ExamPrepRequest

router = APIRouter(prefix="/features", tags=["Features"])


@router.post("/summarize")
async def summarize_document(
    request: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate or retrieve a cached document summary."""
    # Verify document ownership
    doc = db.query(Document).filter(Document.id == request.doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    # Check cache
    cached = db.query(Summary).filter(
        Summary.user_id == current_user.id,
        Summary.doc_id == request.doc_id,
        Summary.level == request.detail_level.value
    ).first()

    if cached:
        return {"id": cached.id, "summary": cached.content, "detail_level": request.detail_level}

    # Retrieve context chunks for a global view
    try:
        store = load_store(request.doc_id)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vector index not found")

    results = retrieve(store, "general overview summary main topics core terms definitions", top_k=6)
    context = format_context(results)

    prompt = build_summary_prompt(context, request.detail_level.value)
    summary = generate_response(prompt)

    # Save to cache database
    db_summary = Summary(
        user_id=current_user.id,
        doc_id=request.doc_id,
        level=request.detail_level.value,
        content=summary
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)

    return {"id": db_summary.id, "summary": summary, "detail_level": request.detail_level}


@router.post("/quiz")
async def generate_quiz(
    request: QuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate or retrieve a cached quiz based on document content."""
    doc = db.query(Document).filter(Document.id == request.doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    # Check cache
    cached = db.query(Quiz).filter(
        Quiz.user_id == current_user.id,
        Quiz.doc_id == request.doc_id,
        Quiz.num_questions == request.num_questions,
        Quiz.difficulty == request.difficulty,
        Quiz.question_type == request.question_type
    ).first()

    if cached:
        try:
            return json.loads(cached.content)
        except json.JSONDecodeError:
            return {"raw_quiz": cached.content, "id": cached.id}

    # Retrieve context chunks
    try:
        store = load_store(request.doc_id)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vector index not found")

    results = retrieve(store, "core concepts main definitions details and examples rules principles formulas", top_k=6)
    context = format_context(results)

    prompt = build_quiz_prompt(
        context,
        num_questions=request.num_questions,
        difficulty=request.difficulty,
        qtype=request.question_type
    )
    raw = generate_response(prompt)

    # Parse LLM JSON output
    parsed_quiz = None
    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            parsed_quiz = json.loads(json_match.group())
        else:
            parsed_quiz = json.loads(raw)
    except json.JSONDecodeError:
        # If JSON is corrupted, wrap raw string in a schema-like fallback or return it directly
        parsed_quiz = {"raw_quiz": raw, "parse_error": True}

    # Save to SQLite
    db_quiz = Quiz(
        user_id=current_user.id,
        doc_id=request.doc_id,
        num_questions=request.num_questions,
        difficulty=request.difficulty,
        question_type=request.question_type,
        content=json.dumps(parsed_quiz)
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)

    parsed_quiz["id"] = db_quiz.id
    return parsed_quiz


@router.post("/flashcards")
async def generate_flashcards(
    request: FlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate flashcards dynamically from key concepts in the document."""
    doc = db.query(Document).filter(Document.id == request.doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    try:
        store = load_store(request.doc_id)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vector index not found")

    # Fetch concepts and definitions
    results = retrieve(store, "definitions key terms theories glossary vocabulary summary formulas", top_k=5)
    context = format_context(results)

    prompt = build_flashcard_prompt(context)
    raw = generate_response(prompt)

    try:
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if json_match:
            cards = json.loads(json_match.group())
        else:
            cards = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback parsing
        cards = []
        for line in raw.split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':', 1)
                cards.append({
                    "front": parts[0].strip('•- "*'),
                    "back": parts[1].strip(' "*'),
                    "topic": "General"
                })
        if not cards:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to parse generated flashcards.")

    return cards


@router.post("/exam-prep")
async def generate_exam_prep(
    request: ExamPrepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate or retrieve cached exam revision materials."""
    doc = db.query(Document).filter(Document.id == request.doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    # Check cache
    cached = db.query(ExamPrep).filter(
        ExamPrep.user_id == current_user.id,
        ExamPrep.doc_id == request.doc_id,
        ExamPrep.prep_type == request.prep_type,
        ExamPrep.difficulty == request.difficulty
    ).first()

    if cached:
        return {"id": cached.id, "content": cached.content, "prep_type": request.prep_type, "difficulty": request.difficulty}

    try:
        store = load_store(request.doc_id)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vector index not found")

    # Retrieve context chunks
    results = retrieve(store, "important equations core theories high-yield topics questions exercises key points", top_k=10)
    context = format_context(results)

    prompt = build_exam_prep_prompt(context, request.prep_type, request.difficulty)
    content = generate_response(prompt)

    # Save to SQLite
    db_prep = ExamPrep(
        user_id=current_user.id,
        doc_id=request.doc_id,
        prep_type=request.prep_type,
        difficulty=request.difficulty,
        content=content
    )
    db.add(db_prep)
    db.commit()
    db.refresh(db_prep)

    return {"id": db_prep.id, "content": content, "prep_type": request.prep_type, "difficulty": request.difficulty}