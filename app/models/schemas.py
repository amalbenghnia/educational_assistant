from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime


# Auth Schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# RAG & Document Schemas
class SummaryLevel(str, Enum):
    brief = "brief"
    medium = "medium"
    detailed = "detailed"
    bullet_point = "bullet_point"
    exam_revision = "exam_revision"


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    num_pages: int
    num_chunks: int
    message: str


class QuestionRequest(BaseModel):
    doc_id: str  # specific doc_id or "all"
    question: str = Field(..., min_length=3, max_length=500)
    session_id: Optional[str] = "default"
    top_k: Optional[int] = Field(default=5, ge=1, le=15)


class AnswerResponse(BaseModel):
    answer: str
    sources: List[dict]
    session_id: str


class SummaryRequest(BaseModel):
    doc_id: str
    detail_level: SummaryLevel = SummaryLevel.medium


class QuizRequest(BaseModel):
    doc_id: str
    num_questions: int = Field(default=5, ge=2, le=15)
    difficulty: str = "intermediate"  # "beginner", "intermediate", "advanced"
    question_type: str = "mixed"  # "mcq", "true_false", "short_answer", "fill_blank", "mixed"


class FlashcardRequest(BaseModel):
    doc_id: str


class ExamPrepRequest(BaseModel):
    doc_id: str
    prep_type: str  # "practice_exam", "mock_test", "expected_questions", "important_topics", "revision_plan"
    difficulty: str = "intermediate"  # "beginner", "intermediate", "advanced"