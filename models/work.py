from helpers.time import Time
from pydantic import BaseModel, Field, ValidationError
from bson import ObjectId
from typing import Optional, List
from helpers.database import PyObjectId, Database
from helpers.error import EntryNotFound, EntryMalformed
from fastapi.encoders import jsonable_encoder


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
        schema_extra = {
            "example": {"name": "Werken voor Irek", "employers": ["60ff3271972d0a9c14cc7f21"], "hour_loan": 13.86}}


class WorkModelFactory(Database):
    def __init__(self):
        super().__init__()
        self.COLLECTION_NAME = "work"

    async def get_all(self) -> List[WorkModel]:
        """
        Gets all of the work object from the database
        :return List[WorkModel]: List of all the work models
        """
        db_resp = await self.find(self.COLLECTION_NAME, 1000)
        to_resp = []

        for i in db_resp:
            to_resp.append(WorkModel.parse_obj(i))

        return to_resp

    async def get_by_id(self, work_id: str) -> WorkModel:
        """
        Gets work model by its id
        :param work_id: id of the destination work model
        :raises EntryNotFound: If there is no work object with this id
        :return WorkModel: work model.
        """
        db_resp = await self.find_one(self.COLLECTION_NAME, {"_id": work_id})
        if db_resp is None:
            raise EntryNotFound("Can't find this work by id.")

        try:
            return WorkModel.parse_obj(db_resp)
        except ValidationError as e:
            raise EntryMalformed(e)

    async def create_from_model(self, model: WorkModel) -> WorkModel:
        """
        Creates a new work model and returns it
        :param model: a new model to be added into the database
        :raises EntryNotFound: When adding failed
        :return WorkModel: work model from get_by_id
        """
        model = jsonable_encoder(model)
        new_model = await self.insert_one(self.COLLECTION_NAME, model)
        return await self.get_by_id(new_model.inserted_id)

    async def update_by_id_with_model(self, work_id: str, update_model: UpdateWorkModel) -> WorkModel:
        """
        Updates a existing work model and then returns it?
        :param work_id: Id of work to update
        :param update_model: New content for the work
        :return: Updated work object
        """
        db_resp = await self.update(self.COLLECTION_NAME, work_id, update_model)
        if db_resp is None:
            raise EntryNotFound("Can't find this work by id")
        return db_resp
