"""
Database configuration and session management
Handles SQLAlchemy setup and database connections
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL configuration
# For development, use SQLite; for production, use PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ecommerce.db"  # Default SQLite for development
)

# Handle PostgreSQL URL format for Render/Heroku
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy engine configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query logging
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL query logging
    )

# Session configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI routes
    Provides database session with automatic cleanup
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_db_info():
    """
    Get database connection information for health checks
    """
    try:
        with engine.connect() as connection:
            if DATABASE_URL.startswith("sqlite"):
                result = connection.execute("SELECT 1").fetchone()
                return {"type": "SQLite", "status": "connected"}
            else:
                result = connection.execute("SELECT version()").fetchone()
                return {"type": "PostgreSQL", "status": "connected", "version": str(result[0])}
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return {"type": "Unknown", "status": "disconnected", "error": str(e)}
