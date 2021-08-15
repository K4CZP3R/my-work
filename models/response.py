from typing import Any, Optional
from pydantic import BaseModel, Field


class ResponseErrorModel(BaseModel):
    message: str = Field(...)
    code: int = Field(...)


class ResponseModel(BaseModel):
    data: Any = Field(...)
    message: Optional[str] = Field(...)