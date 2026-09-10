import logging
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )
except Exception as exc:
    logger.warning(f"Primary DATABASE_URL initialization note: {exc}")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Verify database schema, purge outdated instances if schema mismatch exists, and initialize tables cleanly."""
    try:
        inspector = inspect(engine)
        if inspector.has_table("complaints"):
            columns = [col["name"] for col in inspector.get_columns("complaints")]
            if "complaint_source" not in columns or len(columns) < 20:
                logger.warning("Outdated 'complaints' schema detected (missing columns). Dropping and re-creating database tables...")
                Base.metadata.drop_all(bind=engine)

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified and initialized successfully.")
    except Exception as err:
        logger.error(f"Error during init_db: {err}")
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            pass


def get_db():
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
