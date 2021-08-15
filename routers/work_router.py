from models.work import UpdateWorkModel, WorkModel, WorkModelFactory
from fastapi import APIRouter, Body, Depends
from typing import List
from typing import Any
from routers.authentication_router import get_current_active_user
from helpers.error import Error, EntryNotFound

from helpers.log import Log

router = APIRouter(
    prefix="/work", tags=["work"], responses={404: {"Error": {"message": "Not found."}}, }
)

COLLECTION_NAME = "work"


@router.get("/", response_model=list[WorkModel], dependencies=[Depends(get_current_active_user)])
async def read() -> List[WorkModel]:
    return await WorkModelFactory().get_all()


@router.get("/{work_id}", response_model=WorkModel, dependencies=[Depends(get_current_active_user)])
async def read_work_by_id(work_id: str) -> Any:
    try:
        return await WorkModelFactory().get_by_id(work_id)
    except EntryNotFound as e:
        Log().error(str(e))
        return Error.generic_error(404, "Entry not found!", 404)


@router.post("/", response_description="Add new employer", response_model=WorkModel,
             dependencies=[Depends(get_current_active_user)])
async def create(model: WorkModel = Body(...)):
    try:
        return await WorkModelFactory().create_from_model(model)
    except EntryNotFound as e:
        Log.error(str(e))
        return Error.generic_error(404, "Entry creating failed!", 404)


@router.put("/{work_id}", response_description="Update employer", response_model=WorkModel,
            dependencies=[Depends(get_current_active_user)])
async def update_work(work_id: str, update_model: UpdateWorkModel = Body(...)):
    try:
        return await WorkModelFactory().update_by_id_with_model(work_id, update_model)
    except EntryNotFound as e:
        Log().error(str(e))
        return Error.generic_error(404, "Not found", 404)
