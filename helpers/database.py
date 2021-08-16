from typing import Any
from helpers.singleton import Singleton
import motor.motor_asyncio
import config
from bson import ObjectId
from typing import Generic
from typing import TypeVar


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Database(metaclass=Singleton):
    def __init__(self) -> None:
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_HOST)

        self.db = self.client[config.MONGO_DB]

    async def wipe_all(self):
        await self.client.drop_database(config.MONGO_DB)

    def find_one(self, db_name: str, filter: dict):
        return self.db[db_name].find_one(filter)

    def insert_one(self, db_name: str, to_insert: Any):
        return self.db[db_name].insert_one(to_insert)

    def find(self, db_name: str, amount: int):
        return self.db[db_name].find().to_list(amount)

    async def update(self, db_name: str, id: str, new_object: Any):
        new_object = {k: v for k, v in new_object.dict().items() if v is not None}

        if len(new_object) >= 1:
            update_result = await self.db[db_name].update_one(
                {"_id": id}, {"$set": new_object}
            )

            if update_result.modified_count == 1:
                if (
                        updated_obj := await self.find_one(db_name, {"_id": id})
                ) is not None:
                    return updated_obj

        if (existing_obj := await self.find_one(db_name, {"_id": id})) is not None:
            return existing_obj
        return None
