from pydantic import BaseModel
from typing import Generic, Optional, TypeVar

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None