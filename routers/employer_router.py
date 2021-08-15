from starlette.responses import JSONResponse

from helpers.error import EntryNotFound, EntryMalformed, Error
from models.employer import UpdateEmployerModel, EmployerModel, EmployerModelFactory
from fastapi import APIRouter, Body, Depends
from models.response import ResponseErrorModel
from typing import List, Any
from helpers.database import Database
from fastapi.encoders import jsonable_encoder
from routers.authentication_router import get_current_active_user

router = APIRouter(
    prefix="/employer",
    tags=["employer"],
    responses={404: {"Error": {"message": "Not found."}}},
)

COLLECTION_NAME = "employer"


@router.get("/", dependencies=[Depends(get_current_active_user)])
async def read() -> List[EmployerModel]:
    return await EmployerModelFactory().get_all()


@router.get("/{employer_id}", response_model=EmployerModel, dependencies=[Depends(get_current_active_user)])
async def read_employer_by_id(employer_id: str) -> Any:
    try:
        return await EmployerModelFactory().get_by_id(employer_id)
    except EntryNotFound as e:
        return Error().generic_error(404, "Not found.", 404)
    except EntryMalformed as e:
        return Error().generic_error(500, "Malformed", 500)


@router.post("/", response_description="Add new employer", response_model=EmployerModel,
             dependencies=[Depends(get_current_active_user)])
async def create(model: EmployerModel = Body(...)):
    try:
        return await EmployerModelFactory().create_from_model(model)
    except EntryNotFound as e:
        return Error().generic_error(404, "Not found.", 404)
    except EntryMalformed as e:
        return Error().generic_error(500, "Malformed", 500)


@router.put(
    "/{employer_id}", response_description="Update employer", response_model=EmployerModel,
    dependencies=[Depends(get_current_active_user)]
)
async def update_work(employer_id: str, update_model: UpdateEmployerModel = Body(...)):
    try:
        return await EmployerModelFactory().update_by_id_with_model(employer_id, update_model)
    except EntryNotFound as e:
        return Error().generic_error(404, "Not found.", 404)
    except EntryMalformed as e:
        return Error().generic_error(500, "Malformed", 500)
