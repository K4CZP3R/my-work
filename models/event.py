from models.work import WorkModel
from helpers.time import Time
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from helpers.database import PyObjectId, Database

class EventModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    work: PyObjectId = Field(...)
    
    created_at: float = Field(Time.get_unix())
    
    from_time: float = Field(Time.get_unix())
    to_time: float = Field(Time.get_unix())

    based_on_hour_loan: bool = Field(...)
    loan_on_top: float = Field(...)

    name: str = Field(...)
    description: str = Field(...)

    async def get_worked_for(self):
        return Time.get_hours_between_ms(self.from_time, self.to_time)

    async def get_loan(self):
        resp = await Database().find_one("work", {"_id": self.work})
        if resp is None:
            return None
        resp: WorkModel
        return self.loan_on_top + ((await self.get_worked_for() * resp.hour_loan) if self.based_on_hour_loan else 0)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "work": "60ff3271972d0a9c14cc7f21",
                "created_at": 1627333259.5807598,
                "from_time": 0,
                "to_time": 60,
                "based_on_hour_loan": True,
                "loan_on_top": 30,
                "name": "Helping with x",
                "description": "Helped using x and y, for y i needed to pay from my own account."
            }
        }

class UpdateEventModel(BaseModel):
    work: Optional[PyObjectId]
    from_time: Optional[float]
    to_time: Optional[float]

    based_on_hour_loan: Optional[bool]
    loan_on_top: Optional[float]

    name: Optional[str]
    description: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "work": "60ff3271972d0a9c14cc7f21",
                "from_time": 0,
                "to_time": 60,
                "based_on_hour_loan": True,
                "loan_on_top": 30,
                "name": "Helping with x",
                "description": "Helped using x and y, for y i needed to pay from my own account."
            }
        }