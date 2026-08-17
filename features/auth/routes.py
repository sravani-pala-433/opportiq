import logging

from fastapi import APIRouter, Depends, status, Response

from core.utils.response_helpers import success_response
from features.auth.schemas import (
    LoginRequest,
    UserCreate,
    GoogleAuthRequest,
    GoogleAuthUrlResponse,
    AuthTokenResponse
)
from features.auth.service import AuthService

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@auth_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
)
async def signup(user_data: UserCreate, auth_service: AuthService = Depends()):
    logger.debug("Signing up user: %s", user_data.email)
    user_response = await auth_service.sign_up(user_data)
    return success_response(
        data=user_response.model_dump(),
        message="User registered successfully.",
        status_code=201
    )

@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
async def login(response: Response, login_data: LoginRequest, auth_service: AuthService = Depends()):
    logger.debug("Logging in user: %s", login_data.email)
    user_response, access_token = await auth_service.login(login_data)
    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24  # 1 day in seconds
    )
    return success_response(
        data=user_response.model_dump(),
        message="Login successful.",
        status_code=200
    )

@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def logout(response: Response):
    logger.debug("Logging out user")
    # Clear the HTTP-only cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return success_response(
        data=None,
        message="Logout successful.",
        status_code=200
    )


# Google OAuth 2.0 Routes
@auth_router.get(
    "/google/auth-url",
    status_code=status.HTTP_200_OK,
    response_model=GoogleAuthUrlResponse
)
async def get_google_auth_url(auth_service: AuthService = Depends()):
    """
    Get Google OAuth authorization URL

    Returns the URL to redirect the user to for Google authentication
    """
    logger.debug("Retrieving Google auth URL")
    auth_url, state = auth_service.get_google_auth_url()
    # In production, you should store this state in Redis or session
    # For now, returning it to client who should include it in callback
    return GoogleAuthUrlResponse(auth_url=auth_url, state=state)


@auth_router.post(
    "/google/callback",
    status_code=status.HTTP_200_OK,
    response_model=AuthTokenResponse
)
async def google_oauth_callback(
    response: Response,
    auth_request: GoogleAuthRequest,
    auth_service: AuthService = Depends()
):
    """
    Handle Google OAuth callback

    Exchange authorization code for user authentication
    """
    logger.debug("Processing Google OAuth callback")
    user_response, access_token = await auth_service.handle_google_oauth_callback(auth_request.code)

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24  # 1 day in seconds
    )

    return AuthTokenResponse(
        access_token=access_token,
        user=user_response
    )

