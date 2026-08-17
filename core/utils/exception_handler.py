import asyncio
import logging
from functools import wraps
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from passlib.exc import UnknownHashError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from core.utils.error_helpers import raise_app_exception, ServiceError

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, error_code: str, error_type: str, details: Any, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.error_code = error_code
        self.error_type = error_type
        self.details = details
        self.status_code = status_code

    def to_response(self):
        # If details is a list of structured errors, return them directly
        if isinstance(self.details, list):
            return {
                "error_code": self.error_code,
                "error_type": self.error_type,
                "errors": self.details,
                "status_code": self.status_code
            }

        # Fallback for single error
        return {
            "error_code": self.error_code,
            "error_type": self.error_type,
            "details": self.details,
            "status_code": self.status_code
        }


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response()
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.status_code,
            "error_type": "HTTPException",
            "details": str(exc.detail)
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "error_type": "UnhandledException",
            "details": str(exc)
        }
    )



def exception_handler(func):
    """Generalized exception handling for service functions using ServiceError and raise_app_exception."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.error("Integrity Error: %s", str(e))
            error_message = str(e)
            if "duplicate key value violates unique constraint" in error_message.lower():
                if "email" in error_message.lower():
                    raise_app_exception(ServiceError.DUPLICATE_EMAIL)
            raise_app_exception(ServiceError.INTERNAL_ERROR, "Duplicate or invalid data while accessing database.")
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy Error: %s", str(e))
            raise_app_exception(ServiceError.INTERNAL_ERROR, "An error occurred while accessing the database.")
        except UnknownHashError:
            logger.warning("Hashing algorithm mismatch.")
            raise_app_exception(ServiceError.UNAUTHORIZED, "Invalid credentials or password hashing failed.")
        except ValueError as e:
            logger.error("Value Error: %s", str(e))
            raise_app_exception(ServiceError.INVALID_INPUT, str(e))
        except TypeError as e:
            logger.error("Type Error: %s", str(e))
            raise_app_exception(ServiceError.INVALID_INPUT, str(e))
        except ImportError as e:
            logger.error("Import Error: %s", str(e))
            raise_app_exception(ServiceError.INTERNAL_ERROR, str(e))
        except TimeoutError as e:
            logger.error("Timeout Error: %s", str(e))
            raise_app_exception(ServiceError.INTERNAL_ERROR, str(e))
        except ConnectionError as e:
            logger.error("Connection Error: %s", str(e))
            raise_app_exception(ServiceError.INTERNAL_ERROR, str(e))
        except asyncio.CancelledError as e:
            logger.warning("Async Task Cancelled: %s", str(e))
            raise_app_exception(ServiceError.INTERNAL_ERROR, str(e))
        except AttributeError as e:
            logger.error("Attribute Error: %s", str(e))
            raise_app_exception(ServiceError.INVALID_INPUT, str(e))
        except KeyError as e:
            logger.error("Key Error: %s", str(e))
            raise_app_exception(ServiceError.INVALID_INPUT, str(e))
        except IndexError as e:
            logger.error("Index Error: %s", str(e))
            raise_app_exception(ServiceError.INVALID_INPUT, str(e))
        except FileNotFoundError as e:
            logger.error("File Not Found Error: %s", str(e))
            raise_app_exception(ServiceError.FILE_NOT_FOUND, str(e))
        except PermissionError as e:
            logger.error("Permission Error: %s", str(e))
            raise_app_exception(ServiceError.FORBIDDEN, str(e))
        except IsADirectoryError as e:
            logger.error("Is A Directory Error: %s", str(e))
            raise_app_exception(ServiceError.INVALID_INPUT, str(e))
        except OSError as e:
            logger.error("OS Error: %s", str(e))
            raise_app_exception(ServiceError.INTERNAL_ERROR, str(e))
        except AppException as ae:
            raise ae
        except Exception as e:
            logger.exception("Unexpected error during operation: %s", str(e))
            raise_app_exception(ServiceError.INTERNAL_ERROR, str(e))

    return wrapper
