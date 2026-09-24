import uuid
import logging
from typing import Type, List
from sqlalchemy.orm import Session

from core.logging import get_logger
from features.auth.models import User
from core.utils.data_masking import encrypt_data, decrypt_data

logger = get_logger(__name__)

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create_user(self, user_data: dict) -> User:
        logger.debug("Creating user with data in repository")
        new_user = User(**user_data)
        self.session.add(new_user)
        self.session.flush()
        logger.info(f"User created with ID: {new_user.id}")
        return new_user

    async def get_user_by_email(self, email: str) -> type[User] | None:
        return self.session.query(User).filter(User.email == email).first()

    async def get_user_by_id(self, user_id: uuid.UUID) -> type[User] | None:
        return self.session.query(User).filter(User.id == user_id).first()

    async def get_user_by_oauth(self, oauth_provider: str, oauth_id: str) -> type[User] | None:
        """Get user by OAuth provider and provider ID"""
        return self.session.query(User).filter(
            User.oauth_provider == oauth_provider,
            User.oauth_id == oauth_id
        ).first()


