from models.work import WorkModel
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
from helpers.error import Error
from routers.employer_router import COLLECTION_NAME as Employer_COLLECTION_NAME
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
async def read_report_by_id(report_id: str) -> str:
    resp = await Database().find_one(COLLECTION_NAME, {"_id": report_id})
    return resp if resp is not None else Error.generic_error(404, "Not found", 404)


@router.get("/{id}/txt", response_description="Generate pdf report.", dependencies=[Depends(get_current_active_user)])
async def read_report_pdf_by_id(report_id: str) -> str:
    resp = await Database().find_one(COLLECTION_NAME, {"_id": report_id})
    return (await ReportModel.parse_obj(resp).generate_report()) if resp is not None else Error.generic_error(404,
                                                                                                              "Not "
                                                                                                              "found",
                                                                                                              404)


@router.post("/", response_description="Add new report", response_model=ReportModel,
             dependencies=[Depends(get_current_active_user)])
async def create(model: CreateReportModel = Body(...)):
    work_obj = await Database().find_one(COLLECTION_NAME, {'_id': str(model.work_id)})
    if work_obj is None:
        return Error.generic_error(404, "Work not found!", 404)
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
