from fastapi.encoders import jsonable_encoder

from helpers.error import EntryNotFound, EntryMalformed
from models.work import WorkModel
from helpers.time import Time
from pydantic import BaseModel, Field, ValidationError
from bson import ObjectId
from typing import Optional, List
from helpers.database import PyObjectId, Database
from helpers.log import Log


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
        resp = await Database().find_one("work", {"_id": str(self.work)})
        if resp is None:
            Log().error(f"There is no work with id {self.work}")
            return None
        resp = WorkModel.parse_obj(resp)
        hour_loan = await self.get_worked_for() * resp.hour_loan
        loan_total = self.loan_on_top + (
            (await self.get_worked_for() * resp.hour_loan) if self.based_on_hour_loan else 0)
        return loan_total

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


class EventModelFactory(Database):
    def __init__(self):
        super().__init__()
        self.COLLECTION_NAME = "event"

    async def get_all(self) -> List[EventModel]:
        """
        Gets all of the event object from the database
        :return List[EventModel]: List of all the event models
        """
        db_resp = await self.find(self.COLLECTION_NAME, 1000)
        to_resp = []

        for i in db_resp:
            to_resp.append(EventModel.parse_obj(i))

        return to_resp

    async def get_by_id(self, event_id: str) -> EventModel:
        """
        Gets event model by its id
        :param event_id: id of the destination event model
        :raises EntryNotFound: If there is no event object with this id
        :return EventModel: event model.
        """
        db_resp = await self.find_one(self.COLLECTION_NAME, {"_id": event_id})
        if db_resp is None:
            raise EntryNotFound("Can't find this report by id.")

        try:
            return EventModel.parse_obj(db_resp)
        except ValidationError as e:
            raise EntryMalformed(e)

    async def create_from_model(self, model: EventModel) -> EventModel:
        """
        Creates a new event model and returns it
        :param model: a new model to be added into the database
        :raises EntryNotFound: When adding failed
        :return EventModel: event model from get_by_id
        """
        model = jsonable_encoder(model)
        new_model = await self.insert_one(self.COLLECTION_NAME, model)
        return await self.get_by_id(new_model.inserted_id)

    async def update_by_id_with_model(self, event_id: str, update_model: UpdateEventModel) -> EventModel:
        """
        Updates a existing event model and then returns it?
        :param event_id: Id of event to update
        :param update_model: New content for the event
        :return: Updated event object
        """
        db_resp = await self.update(self.COLLECTION_NAME, event_id, update_model)
        if db_resp is None:
            raise EntryNotFound("Can't find this event by id")
        return db_resp
