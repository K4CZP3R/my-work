from helpers.time import Time
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from helpers.database import PyObjectId


class WorkModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    created_at: float = Field(Time.get_unix())
    employers: list[PyObjectId] = Field([])
    hour_loan: float = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Werken voor Irek",
                "created_at": 1627333259.5807598,
                "employers": ["60ff3271972d0a9c14cc7f21"],
                "hour_loan": 13.64
            }
        }


class UpdateWorkModel(BaseModel):
    name: Optional[str]
    employers: Optional[list[PyObjectId]]
    hour_loan: Optional[float]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {"example": {"name": "Werken voor Irek", "employers": ["60ff3271972d0a9c14cc7f21"], "hour_loan": 13.86}}
        
