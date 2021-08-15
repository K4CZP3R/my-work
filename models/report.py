from starlette.responses import FileResponse
from models.employer import EmployerModel
from helpers.time import Time
from helpers.log import Log
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
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
                employer += f"  {addr}\n"
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
