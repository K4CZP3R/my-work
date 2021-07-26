from helpers.time_helpers import TimeHelpers
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from helpers.database import PyObjectId


class WorkModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    created_at: float = Field(TimeHelpers.get_unix())

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Werken voor Irek",
                "created_at": 1627333259.5807598,
            }
        }


class UpdateWorkModel(BaseModel):
    name: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {"example": {"name": "Werken voor Irek"}}
