from datetime import datetime, timezone
from sqlalchemy import Column, UUID, String, Boolean, DateTime
import uuid
from core import logging
from core.database import Base

logging.configure_logging()
logger = logging.get_logger(__name__)

logger.info("Initializing database")

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,index= True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # nullable for OAuth users
    full_name = Column(String, nullable=False)
    bio = Column(String,nullable=True)
    user_type = Column(String, default='user')
    experience_level = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    is_open_to_refer = Column(Boolean, default=False)
    onboarding_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', etc.
    oauth_id = Column(String, nullable=True, index=True)  # Provider's user ID
    profile_picture_url = Column(String, nullable=True)  # URL for profile picture

