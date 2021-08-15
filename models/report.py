from fastapi.encoders import jsonable_encoder
from starlette.responses import FileResponse

from helpers.error import EntryNotFound, EntryMalformed
from models.employer import EmployerModel
from helpers.time import Time
from helpers.log import Log
from pydantic import BaseModel, Field, ValidationError
from bson import ObjectId
from typing import Optional, List
from helpers.database import Database
from helpers.database import PyObjectId
from models.work import WorkModel
from models.event import EventModel
from helpers.pdf import PDFGenerator, PDFReport


class CreateReportModel(BaseModel):
    work_id: PyObjectId = Field(...)
    events_ids: list[PyObjectId] = Field(...)


class ReportModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: float = Field(Time.get_unix())

    work: WorkModel
    events: list[EventModel]
    employers: list[EmployerModel]

    async def get_loan(self, round_to=2):
        total = 0
        for event in self.events:
            if (event_loan := await event.get_loan()) is not None:
                Log().info(f"event: {event_loan}")
                total += event_loan
        Log().info(f"total: {total}")
        return round(total, round_to)

    async def generate_report(self):
        Log().info("This is log!")
        employers = ""
        for employer in self.employers:
            employers += f"- {employer.name} ({employer.email}) ({employer.id})\n"
            if (addr := employer.address) is not None:
                employers += f"  {addr}\n"
        events = ""
        for event in self.events:
            events += f"- {event.name} ({event.description}) | {await event.get_worked_for()} | On top: {event.loan_on_top} | {await event.get_loan()}\n"

        text = f"""
        Werkgever: {self.work.name} ({self.work.id})
        Uurloon: {self.work.hour_loan} euro / uur\n\n
        Werkgever(s):
        {employers}
        \n
        Events:
        {events}
        \n
        Summary:
        Totaal te betalen: {await self.get_loan()} euro.
        """

        PDFGenerator.generate(text.split("\n"), f"{self.id}.pdf")

        return FileResponse(f"{self.id}.pdf", media_type="application/pdf")

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


class ReportModelFactory(Database):
    def __init__(self):
        super().__init__()
        self.COLLECTION_NAME = "report"

    async def get_all(self) -> List[ReportModel]:
        """
        Gets all of the report object from the database
        :return List[ReportModel]: List of all the work models
        """
        db_resp = await self.find(self.COLLECTION_NAME, 1000)
        to_resp = []

        for i in db_resp:
            to_resp.append(ReportModel.parse_obj(i))

        return to_resp
        
    async def get_by_id(self, report_id: str) -> ReportModel:
        """
        Gets report model by its id
        :param report_id: id of the destination report model
        :raises EntryNotFound: If there is no report object with this id
        :return ReportModel: report model.
        """
        db_resp = await self.find_one(self.COLLECTION_NAME, {"_id": report_id})
        if db_resp is None:
            raise EntryNotFound("Can't find this report by id.")

        try:
            return ReportModel.parse_obj(db_resp)
        except ValidationError as e:
            raise EntryMalformed(e)

    async def create_from_model(self, model: ReportModel) -> ReportModel:
        """
        Creates a new report model and returns it
        :param model: a new model to be added into the database
        :raises EntryNotFound: When adding failed
        :return ReportModel: report model from get_by_id
        """
        model = jsonable_encoder(model)
        new_model = await self.insert_one(self.COLLECTION_NAME, model)
        return await self.get_by_id(new_model.inserted_id)
