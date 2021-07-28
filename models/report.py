from models.employer import EmployerModel
from helpers.time_helpers import TimeHelpers
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from helpers.database import PyObjectId
from models.work import WorkModel
from models.event import EventModel

class CreateReportModel(BaseModel):
    work_id: PyObjectId = Field(...)
    events_ids: list[PyObjectId] = Field(...)

class ReportModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: float = Field(TimeHelpers.get_unix())

    work: WorkModel
    events: list[EventModel]
    employers: list[EmployerModel]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "created_at": 0.0,
                "work": "<WorkModel>",
                "events": ["<EventModel>", "<EventModel>"]
            }
        }
