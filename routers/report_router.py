from models.work import WorkModel
from models.event import EventModel
from models.report import ReportModel, CreateReportModel, ReportModelFactory
from models.work import WorkModelFactory
from models.employer import EmployerModelFactory
from models.employer import EmployerModel
from models.event import EventModelFactory
from fastapi import APIRouter, Body, Depends
from typing import List, Any
from helpers.log import Log
from helpers.error import Error, EntryNotFound, EntryMalformed
from routers.authentication_router import get_current_active_user

router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"Error": {"message": "Not found."}}},
)

COLLECTION_NAME = "report"


@router.get("/", response_model=list[ReportModel], dependencies=[Depends(get_current_active_user)])
async def read() -> List[ReportModel]:
    return await ReportModelFactory().get_all()


@router.get("/{report_id}", response_model=ReportModel, dependencies=[Depends(get_current_active_user)])
async def read_report_by_id(report_id: str) -> Any:
    try:
        return await ReportModelFactory().get_by_id(report_id)
    except EntryNotFound as e:
        return Error.generic_error(404, "Not found", 404)


@router.get("/{report_id}/pdf", response_description="Generate pdf report.",
            dependencies=[Depends(get_current_active_user)])
async def read_report_pdf_by_id(report_id: str) -> Any:
    try:
        report = await ReportModelFactory().get_by_id(report_id)
        return await report.generate_report()
    except EntryNotFound as e:
        return Error.generic_error(404, "Not found", 404)
    except EntryMalformed as e:
        return Error.generic_error(500, "Entry malformed", 500)


@router.post("/", response_description="Add new report", response_model=ReportModel,
             dependencies=[Depends(get_current_active_user)])
async def create(model: CreateReportModel = Body(...)):
    try:
        work = await WorkModelFactory().get_by_id(str(model.work_id))

        employed_objs: List[EmployerModel] = []
        for e_id in work.employers:
            try:
                employed_objs.append(await EmployerModelFactory().get_by_id(str(e_id)))
            except EntryNotFound as e:
                Log().error(e)
            except EntryMalformed as e:
                Log().error(e)

        event_objs: List[EventModel] = []
        for e_id in model.events_ids:
            try:
                event_objs.append(await EventModelFactory().get_by_id(str(e_id)))
            except EntryNotFound as e:
                Log().error(e)
            except EntryMalformed as e:
                Log().error(e)

        model = ReportModel(work=work, events=event_objs, employers=employed_objs)

        try:
            return await ReportModelFactory().create_from_model(model)
        except EntryNotFound as e:
            return Error().generic_error(404, "Something went wrong, and the report could not be created.", 404)
        except EntryMalformed as e:
            return Error().generic_error(500, "Something went wrong, and the generated report is invalid.", 500)
    except EntryNotFound as e:
        return Error().generic_error(404, "Work not found", 404)
    except EntryMalformed as e:
        return Error().generic_error(500, "Work is malformed", 500)
