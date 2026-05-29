"""
Database connection and session management.
Creates communication between FastAPI and SQLite database using SQLAlchemy.
Includes connection pooling and error handling.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import DATABASE_URL, DATABASE_ECHO
from app.logger import logger

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=DATABASE_ECHO,
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite."""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Session:
    """
    Dependency function to get database session.
    Used in FastAPI routes with Depends().
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.log_error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables."""
    try:
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info(" Database initialized successfully")
    except Exception as e:
        logger.log_error(f"Database initialization error: {str(e)}")
        raise


def get_db_stats():
    """Get database statistics and connection info."""
    try:
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return {
            "status": "connected",
            "tables": [table[0] for table in tables],
            "database_url": DATABASE_URL
        }
    except Exception as e:
        logger.log_error(f"Database stats error: {str(e)}")
        return {"status": "error", "message": str(e)}