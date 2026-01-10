from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# =====================================================
# DATABASE URL
# =====================================================
# WAJIB pakai service name "postgres"
# Contoh valid:
# postgresql+psycopg2://archive_user:password@postgres:5432/campus_archive_db

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Use SQLite for local development
    DATABASE_URL = "sqlite:///./campus_archive.db"

# =====================================================
# SQLALCHEMY ENGINE
# =====================================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True if not DATABASE_URL.startswith("sqlite") else False,   # Cek koneksi sebelum dipakai (not for SQLite)
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

# =====================================================
# SESSION FACTORY
# =====================================================
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# =====================================================
# DECLARATIVE BASE
# =====================================================
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

# =====================================================
# FASTAPI DEPENDENCY
# =====================================================
def get_db():
    """
    Dependency for FastAPI routes.
    Opens a DB session and closes it after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
