from typing import Optional
from pydantic import BaseModel, Field


class RequestAuthenticateModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class TokenModel(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)

class TokenData(BaseModel):
    username: Optional[str] = None