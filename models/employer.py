from fastapi.encoders import jsonable_encoder

from helpers.error import EntryNotFound, EntryMalformed
from helpers.time import Time
from pydantic import BaseModel, Field, ValidationError
from bson import ObjectId
from typing import Optional, List
from helpers.database import PyObjectId, Database


class EmployerModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: str = Field(...)
    address: Optional[str]
    created_at: float = Field(Time.get_unix())

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Irek",
                "email": "email@e.com",
                "address": "Straat 23, 5344EG Oss",
                "created_at": 1627333259.5807598,
            }
        }


class UpdateEmployerModel(BaseModel):
    name: Optional[str]
    address: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Irek",
                "email": "email@e.com",
                "address": "Straat 23, 5344EG Oss",
                "created_at": 1627333259.5807598,
            }
        }


class EmployerModelFactory(Database):
    def __init__(self):
        super().__init__()
        self.COLLECTION_NAME = "employer"

    async def get_all(self) -> List[EmployerModel]:
        """
        Gets all of the employer object from the database
        :return List[EmployerModel]: List of all the employer models
        """
        db_resp = await self.find(self.COLLECTION_NAME, 1000)
        to_resp = []

        for i in db_resp:
            to_resp.append(EmployerModel.parse_obj(i))

        return to_resp

    async def get_by_id(self, employer_id: str) -> EmployerModel:
        """
        Gets employer model by its id
        :param employer_id: id of the destination employer model
        :raises EntryNotFound: If there is no employer object with this id
        :return EmployerModel: employer model.
        """
        db_resp = await self.find_one(self.COLLECTION_NAME, {"_id": employer_id})
        if db_resp is None:
            raise EntryNotFound("Can't find this report by id.")

        try:
            return EmployerModel.parse_obj(db_resp)
        except ValidationError as e:
            raise EntryMalformed(e)

    async def create_from_model(self, model: EmployerModel) -> EmployerModel:
        """
        Creates a new employer model and returns it
        :param model: a new model to be added into the database
        :raises EntryNotFound: When adding failed
        :return EmployerModel: employer model from get_by_id
        """
        model = jsonable_encoder(model)
        new_model = await self.insert_one(self.COLLECTION_NAME, model)
        return await self.get_by_id(new_model.inserted_id)

    async def update_by_id_with_model(self, employer_id: str, update_model: UpdateEmployerModel) -> EmployerModel:
        """
        Updates a existing event model and then returns it?
        :param employer_id: Id of event to update
        :param update_model: New content for the event
        :return: Updated event object
        """
        db_resp = await self.update(self.COLLECTION_NAME, employer_id, update_model)
        if db_resp is None:
            raise EntryNotFound("Can't find this employer by id")
        return db_resp
