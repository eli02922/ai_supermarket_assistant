from sqlalchemy.orm import Session
from src.db.base import SessionLocal, engine, Base


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database"""
    Base.metadata.create_all(bind=engine)