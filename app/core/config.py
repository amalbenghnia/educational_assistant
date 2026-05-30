from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3"
    llm_temperature: float = 0.2
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 150
    retriever_top_k: int = 5
    upload_dir: Path = Path("uploads")
    vectorstore_dir: Path = Path("vectorstore")
    max_pdf_size_mb: int = 20
    secret_key: str = "supersecretkey_change_me_in_production"
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite:///./educational_assistant.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
