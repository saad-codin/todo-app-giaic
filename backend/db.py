"""Database connection and session management."""

import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

# SQLite-specific settings (not needed for PostgreSQL)
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

# PostgreSQL with Neon requires SSL
pool_args = {}
if "neon" in DATABASE_URL or "postgresql" in DATABASE_URL:
    pool_args = {"pool_pre_ping": True}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args, **pool_args)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session for dependency injection."""
    with Session(engine) as session:
        yield session
