import logging
import re
from typing import Dict, Any, List, Tuple

from core.utils.exception_handler import AppException

logger = logging.getLogger(__name__)

# RFC-ish Email Regex
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# Standard Phone Regex (minimal)
PHONE_REGEX = r"^\+?[1-9]\d{1,14}$"

class ValidationEngine:


    @staticmethod
    def normalize_email(email: str) -> str:
        """Lowercases and trims email."""
        if not email:
            return email
        return email.strip().lower()

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        if not re.fullmatch(EMAIL_REGEX, email):
            return False, "Invalid email format (RFC-standard)."
        return True, ""


    @staticmethod
    def validate_password_complexity(password: str, email: str = "", name: str = "") -> List[Dict[str, Any]]:
        errors = []
        if len(password) < 8:
            errors.append({"code": "PASSWORD_TOO_SHORT", "message": "Password must be at least 8 characters long."})
        if not any(char.isupper() for char in password):
            errors.append({"code": "PASSWORD_NO_UPPERCASE", "message": "Password must contain at least one uppercase letter."})
        if not any(char.isdigit() for char in password):
            errors.append({"code": "PASSWORD_NO_DIGIT", "message": "Password must contain at least one digit."})

        return errors

    @staticmethod
    def raise_validation_errors(errors: List[Dict[str, Any]]):
        if not errors:
            return
        raise AppException(
            error_code="VALIDATION_FAILED",
            error_type="ValidationError",
            details=errors,
            status_code=400
        )
