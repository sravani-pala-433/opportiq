from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    bio: Optional[str] = None
    user_type: Optional[str] = 'user'
    experience_level: Optional[str] = None
    availability: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    is_open_to_refer: Optional[bool] = False

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    bio: Optional[str] = None
    user_type: str
    experience_level: Optional[str] = None
    availability: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    is_open_to_refer: bool
    onboarding_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# OAuth Schemas
class GoogleAuthRequest(BaseModel):
    """Request for Google OAuth authentication"""
    code: str
    state: str


class OAuthUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    oauth_provider: str
    oauth_id: str
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    user_type: Optional[str] = 'user'


class AuthTokenResponse(BaseModel):
    """Response containing auth token and user info"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class GoogleAuthUrlResponse(BaseModel):
    """Response containing Google OAuth authorization URL"""
    auth_url: str
    state: str


