from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import documents, chat, features, auth, export
from app.core.config import get_settings
from app.db.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the SQLite tables and seed default user credentials
    init_db()
    
    # Ensure working directories exist
    settings.upload_dir.mkdir(exist_ok=True)
    settings.vectorstore_dir.mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="AI-Powered Educational Assistant",
    description="An intelligent RAG-based study assistant platforms powered by Llama 3.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(features.router)
app.include_router(export.router)


@app.get("/")
async def root():
    return {
        "name": "AI-Powered Educational Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "profile": "GET /auth/me"
            },
            "documents": {
                "upload": "POST /documents/upload",
                "list": "GET /documents",
                "delete": "DELETE /documents/{doc_id}",
                "search": "GET /documents/search"
            },
            "chat": {
                "ask": "POST /chat/ask",
                "history": "GET /chat/history/{session_id}",
                "clear": "POST /chat/clear/{session_id}"
            },
            "features": {
                "summarize": "POST /features/summarize",
                "quiz": "POST /features/quiz",
                "flashcards": "POST /features/flashcards",
                "exam-prep": "POST /features/exam-prep"
            },
            "export": "GET /export/{feature_type}/{item_id}"
        },
    }