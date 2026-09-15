from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    count: Optional[int] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 50
