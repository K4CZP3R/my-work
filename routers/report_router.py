from models.work import WorkModel
from starlette.responses import FileResponse
from models.event import EventModel
from starlette.responses import JSONResponse
from models.report import ReportModel, CreateReportModel
from models.employer import EmployerModel
from fastapi import APIRouter, Body, Depends
from models.response import ResponseErrorModel
from typing import List
from helpers.database import Database
from fastapi.encoders import jsonable_encoder
from helpers.log import Log
from helpers.pdf import PDFGenerator
from routers.authentication_router import get_current_active_user

router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"Error": {"message": "Not found."}}},
)

COLLECTION_NAME = "report"


@router.get("/", response_model=list[ReportModel], dependencies=[Depends(get_current_active_user)])
async def read() -> List[ReportModel]:
    return await Database().find(COLLECTION_NAME, 1000)


@router.get("/{id}", response_model=ReportModel, dependencies=[Depends(get_current_active_user)])
async def read_work_by_id(id: str) -> str:
    resp = await Database().find_one(COLLECTION_NAME, {"_id": id})
    if resp is None:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(
                ResponseErrorModel(message="Not found", code=0x1337)
            ),
        )
    return resp

@router.get("/{id}/txt", response_description="Generate txt report.", dependencies=[Depends(get_current_active_user)])
async def read_work_pdf_by_id(id: str) -> str:
    resp = await Database().find_one(COLLECTION_NAME, {"_id": id})
    if resp is None:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(
                ResponseErrorModel(message="Not found", code=0x1337)
            ),
        )
    
    report_obj = ReportModel.parse_obj(resp)

    section = []
    section.append(f"Werkgever: {report_obj.work.name} ({report_obj.work.id})")
    section.append(f"Uurloon: {report_obj.work.hour_loan} euro")
    section.append(f"Werkgever(s):")
    for werkgever in report_obj.employers:
        werkgever: EmployerModel
        section.append(f"- {werkgever.name} ({werkgever.email}) Adres: {werkgever.address} ({werkgever.id})")
    section.append("")
    section.append("")
    section.append(f"Events:")
    total_to_pay = 0.00
    for event in report_obj.events:
        event: EventModel
        worked_for_hours = round((event.to_time - event.from_time) / 60 / 60, 2)

        
        event_money = 0.00
        if event.based_on_hour_loan:    
            event_money = (worked_for_hours * report_obj.work.hour_loan)
        event_money += event.loan_on_top
        
        section.append(f"- {event.name} ({event.description}) | ({worked_for_hours} x {report_obj.work.hour_loan}) + {event.loan_on_top} = {event_money}")
        total_to_pay += event_money
    section.append("")
    section.append("")
    section.append("Summary:")
    section.append(f"Totaal te betalen: {total_to_pay} euro.")
    
    PDFGenerator.generate(section, "out.pdf")

    return FileResponse("out.pdf", media_type="application/pdf")

@router.post("/", response_description="Add new report", response_model=ReportModel, dependencies=[Depends(get_current_active_user)])
async def create(model: CreateReportModel= Body(...)):

    work_obj = await Database().find_one("work", {'_id': str(model.work_id)})
    if work_obj is None:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(
                ResponseErrorModel(message="Work not found!", code=0x1337)
            )
        )
    work_obj = WorkModel.parse_obj(work_obj)

    employer_objs: List[EmployerModel] = []
    for employer_id in work_obj.employers:
        Log().info(employer_id)
        employer_obj = await Database().find_one("employer", {"_id": str(employer_id)})
        if employer_obj is not None:
            employer_objs.append(EmployerModel.parse_obj(employer_obj))


    event_objs: List[EventModel] = []
    for event_id in model.events_ids:
        event_obj = await Database().find_one("event", {"_id": str(event_id)})
        if event_obj is not None:
            event_objs.append(EventModel.parse_obj(event_obj))
    
    model = ReportModel(work=work_obj, events=event_objs, employers=employer_objs)
    model = jsonable_encoder(model)
    
    new_model = await Database().insert_one(COLLECTION_NAME, model)
    created_model = await Database().find_one(
        COLLECTION_NAME, {"_id": new_model.inserted_id}
    )
    return created_model