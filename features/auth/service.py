import logging

from core.database import get_session
from core.utils.error_helpers import raise_app_exception, ServiceError
from core.utils.exception_handler import exception_handler
from core.utils.jwt_token import create_access_token
from core.utils.password_hashing import hash_password, verify_password
from core.utils.validation_engine import ValidationEngine
from features.auth.repository import UserRepository
from features.auth.schemas import LoginRequest, UserCreate, UserResponse, OAuthUserCreate
from core.utils.oauth2_google import GoogleOAuth2Handler, generate_oauth_state

logger = logging.getLogger(__name__)

class AuthService:
    @exception_handler
    async def sign_up(self, user_data: UserCreate) -> UserResponse:
        logger.debug("Registering new user: %s", user_data.email)
        
        email_normalized = ValidationEngine.normalize_email(user_data.email)
        
        # Email format validation
        is_valid_email, email_err = ValidationEngine.validate_email(email_normalized)
        if not is_valid_email:
            ValidationEngine.raise_validation_errors([{"code": "INVALID_EMAIL", "message": email_err}])
            
        with get_session() as session:
            user_repo = UserRepository(session)
            existing_user = await user_repo.get_user_by_email(email_normalized)
            if existing_user:
                raise_app_exception(ServiceError.DUPLICATE_EMAIL, f"Email '{email_normalized}' is already registered.")

            # Password complexity validations
            password_errors = ValidationEngine.validate_password_complexity(
                password=user_data.password,
                email=email_normalized,
                name=user_data.full_name
            )
            
            if password_errors:
                ValidationEngine.raise_validation_errors(password_errors)

            hashed_password = hash_password(user_data.password)
            
            # Map schema to dictionary for model creation
            user_dict = user_data.model_dump()
            user_dict["email"] = email_normalized
            user_dict["hashed_password"] = hashed_password
            user_dict.pop("password", None)
            
            new_user = await user_repo.create_user(user_dict)
            logger.info("User registered successfully: %s", new_user.id)
            return UserResponse.model_validate(new_user)

    @exception_handler
    async def login(self, login_data: LoginRequest) -> tuple[UserResponse, str]:
        logger.debug("User login attempt: %s", login_data.email)
        email_normalized = ValidationEngine.normalize_email(login_data.email)
        
        with get_session() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_user_by_email(email_normalized)
            if not user:
                raise_app_exception(ServiceError.UNAUTHORIZED, "Invalid email or password.")
                
            if not verify_password(login_data.password, user.hashed_password):
                raise_app_exception(ServiceError.UNAUTHORIZED, "Invalid email or password.")
                
            # Generate JWT token
            token_data = {"sub": user.email, "user_id": str(user.id)}
            access_token = create_access_token(data=token_data)
            
            logger.info("User logged in successfully: %s", user.id)
            return UserResponse.model_validate(user), access_token

    def get_google_auth_url(self) -> tuple[str, str]:
        """Generate Google OAuth authorization URL and return state for CSRF protection"""
        state = generate_oauth_state()
        auth_url = GoogleOAuth2Handler.get_google_auth_url(state)
        logger.debug("Generated Google auth URL with state: %s", state)
        return auth_url, state

    @exception_handler
    async def handle_google_oauth_callback(self, code: str) -> tuple[UserResponse, str]:
        """
        Handle Google OAuth callback and authenticate/create user

        Args:
            code: Authorization code from Google

        Returns:
            Tuple of (UserResponse, access_token)
        """
        logger.debug("Processing Google OAuth callback")

        # Exchange code for token
        token_data = await GoogleOAuth2Handler.exchange_code_for_token(code)
        if not token_data or "access_token" not in token_data:
            raise_app_exception(ServiceError.UNAUTHORIZED, "Failed to obtain access token from Google.")

        # Get user info from Google
        user_info = await GoogleOAuth2Handler.get_user_info(token_data["access_token"])
        if not user_info:
            raise_app_exception(ServiceError.UNAUTHORIZED, "Failed to retrieve user information from Google.")

        # Parse user info
        oauth_user_data = GoogleOAuth2Handler.parse_google_user_info(user_info)

        with get_session() as session:
            user_repo = UserRepository(session)

            # Check if user already exists with this OAuth provider
            existing_user = await user_repo.get_user_by_oauth(
                oauth_user_data["oauth_provider"],
                oauth_user_data["oauth_id"]
            )

            if existing_user:
                logger.info("User logged in with Google OAuth: %s", existing_user.id)
                # Generate JWT token
                token_data = {"sub": existing_user.email, "user_id": str(existing_user.id)}
                access_token = create_access_token(data=token_data)
                return UserResponse.model_validate(existing_user), access_token

            # Check if user exists with this email
            email_normalized = ValidationEngine.normalize_email(oauth_user_data["email"])
            existing_email_user = await user_repo.get_user_by_email(email_normalized)

            if existing_email_user:
                # Link OAuth to existing account
                existing_email_user.oauth_provider = oauth_user_data["oauth_provider"]
                existing_email_user.oauth_id = oauth_user_data["oauth_id"]
                existing_email_user.profile_picture_url = oauth_user_data.get("profile_picture_url")
                session.flush()
                logger.info("OAuth linked to existing user: %s", existing_email_user.id)

                # Generate JWT token
                token_data = {"sub": existing_email_user.email, "user_id": str(existing_email_user.id)}
                access_token = create_access_token(data=token_data)
                return UserResponse.model_validate(existing_email_user), access_token

            # Create new user from OAuth data
            oauth_user_data["email"] = email_normalized
            new_user = await user_repo.create_user(oauth_user_data)
            logger.info("New user created via Google OAuth: %s", new_user.id)

            # Generate JWT token
            token_data = {"sub": new_user.email, "user_id": str(new_user.id)}
            access_token = create_access_token(data=token_data)
            return UserResponse.model_validate(new_user), access_token
