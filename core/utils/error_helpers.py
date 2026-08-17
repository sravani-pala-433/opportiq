from dataclasses import dataclass
from enum import Enum
from fastapi import status


@dataclass
class AppError:
    name: str
    error_type: str
    details: str
    status_code: int

class ServiceError(Enum):
    CYCLE_DETECTED = AppError(
        name = "CYCLE_DETECTED",
        error_type = "ValidationError",
        details = "Adding this relationship would create a cycle in the family tree.",
        status_code = status.HTTP_400_BAD_REQUEST
    )
    DUPLICATE_EMAIL = AppError(
        name = "DUPLICATE_EMAIL",
        error_type = "ValidationError",
        details = "A user with this email already exists.",
        status_code = status.HTTP_400_BAD_REQUEST
    )
    UNAUTHORIZED = AppError(
        name = "UNAUTHORIZED",
        error_type = "AuthenticationError",
        details = "Invalid credentials or unauthorized access.",
        status_code = status.HTTP_401_UNAUTHORIZED
    )
    INVALID_INPUT = AppError(
        name = "INVALID_INPUT",
        error_type = "ValidationError",
        details = "Invalid input provided.",
        status_code = status.HTTP_400_BAD_REQUEST
    )
    USER_NOT_FOUND = AppError(
        name = "USER_NOT_FOUND",
        error_type = "NotFoundError",
        details = "User not found.",
        status_code = status.HTTP_404_NOT_FOUND
    )
    PERSON_NOT_FOUND = AppError(
        name = "PERSON_NOT_FOUND",
        error_type = "NotFoundError",
        details = "Person not found.",
        status_code = status.HTTP_404_NOT_FOUND
    )
    CLIENT_CREATION_FAILED = AppError(
        name = "CLIENT_CREATION_FAILED",
        error_type = "InternalError",
        details = "Failed to create client.",
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    INTERNAL_ERROR = AppError(
        name = "INTERNAL_ERROR",
        error_type = "InternalError",
        details = "An internal server error occurred.",
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    FILE_NOT_FOUND = AppError(
        name = "FILE_NOT_FOUND",
        error_type = "NotFoundError",
        details = "File not found.",
        status_code = status.HTTP_404_NOT_FOUND
    )
    FORBIDDEN = AppError(
        name = "FORBIDDEN",
        error_type = "PermissionError",
        details = "Access forbidden.",
        status_code = status.HTTP_403_FORBIDDEN
    )

def raise_app_exception(app_error: ServiceError, additional_details: str) :
    from core.utils.exception_handler import AppException
    details = app_error.value.details
    if additional_details:
        details = f"{details} {additional_details}"
    raise AppException(
        error_code=app_error.value.name,
        error_type=app_error.value.error_type,
        details=details,
        status_code=app_error.value.status_code
    )
