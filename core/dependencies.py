from fastapi import Request, Depends
from core.utils.error_helpers import raise_app_exception, ServiceError
from core.utils.jwt_token import decode_access_token
from core.database import get_session
from features.auth.repository import UserRepository
from features.auth.models import User

async def get_current_user(request: Request) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise_app_exception(ServiceError.UNAUTHORIZED, "Missing authentication token.")
    
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise_app_exception(ServiceError.UNAUTHORIZED, "Invalid or expired token.")
        
    email = payload.get("sub")
    with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_user_by_email(email)
        if not user:
            raise_app_exception(ServiceError.UNAUTHORIZED, "User not found.")
        return user
