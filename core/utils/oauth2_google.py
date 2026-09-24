"""
Google OAuth 2.0 authentication utilities
"""
import logging
import json
from typing import Dict, Optional
import requests
from core.config.settings import settings

logger = logging.getLogger(__name__)

# Google OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleOAuth2Handler:
    """Handle Google OAuth 2.0 authentication flow"""

    @staticmethod
    def get_google_auth_url(state: str) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
        logger.debug(f"Generated Google auth URL for state: {state}")
        return auth_url

    @staticmethod
    async def exchange_code_for_token(code: str) -> Optional[Dict]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from Google

        Returns:
            Dict containing token data or None if failed
        """
        try:
            payload = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }

            response = requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=10)
            response.raise_for_status()

            token_data = response.json()
            logger.debug("Successfully exchanged code for token")
            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            return None

    @staticmethod
    async def get_user_info(access_token: str) -> Optional[Dict]:
        """
        Get user information from Google using access token

        Args:
            access_token: Google access token

        Returns:
            Dict containing user information or None if failed
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
            response.raise_for_status()

            user_info = response.json()
            logger.debug(f"Retrieved user info for: {user_info.get('email')}")
            return user_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving user info: {str(e)}")
            return None

    @staticmethod
    def parse_google_user_info(user_info: Dict) -> Dict:
        """
        Parse Google user info into application user data format

        Args:
            user_info: Dict containing Google user information

        Returns:
            Dict with standardized user data
        """
        return {
            "email": user_info.get("email"),
            "full_name": user_info.get("name", ""),
            "profile_picture_url": user_info.get("picture"),
            "oauth_provider": "google",
            "oauth_id": user_info.get("sub")
        }


def generate_oauth_state() -> str:
    """Generate a random state token for CSRF protection"""
    import secrets
    return secrets.token_urlsafe(32)


def verify_oauth_state(state: str, stored_state: str) -> bool:
    """Verify OAuth state token for CSRF protection"""
    return state == stored_state

