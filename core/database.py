import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.logging import get_logger
from core.config.settings import settings
from sqlalchemy.ext.declarative import declarative_base

logger = get_logger(__name__)


DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

