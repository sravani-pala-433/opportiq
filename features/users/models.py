from sqlalchemy import Column, UUID, String, Boolean, DateTime
import uuid
from core import logging
from core.database import Base

logging.configure_logging()
logger = logging.get_logger(__name__)

logger.info("Initializing database")

