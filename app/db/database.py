from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# check_same_thread=False is needed only for SQLite
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables in the database."""
    import app.db.models  # Import models to ensure they are registered
    Base.metadata.create_all(bind=engine)
    seed_user()

def seed_user():
    """Seed the database with the approved credentials."""
    import bcrypt
    from app.db.models import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "amalbenghnya@email.com").first()
        if not user:
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw("amal123".encode('utf-8'), salt).decode('utf-8')
            
            seeded_user = User(
                name="Amal Benghnya",
                email="amalbenghnya@email.com",
                password_hash=password_hash
            )
            db.add(seeded_user)
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()
