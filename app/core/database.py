from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.core.logging import logger


# Create the engine — connection pool is configured here
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    # Recycle connections after 30 minutes to avoid stale connections
    pool_recycle=1800,
    echo=settings.debug,  # logs all SQL queries in debug mode
)

# Session factory — use this to create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.
    Automatically closes the session when the request is done.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Verify the database is reachable.
    Called at startup to fail fast if the DB is misconfigured.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False