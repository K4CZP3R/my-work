from models.work import UpdateWorkModel, WorkModel
from fastapi import APIRouter, Body, Depends
from models.response import ResponseErrorModel
from typing import List
from helpers.database import Database
from typing import Any
from routers.authentication_router import get_current_active_user
from helpers.error import Error
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/work", tags=["work"], responses={404: {"Error": {"message": "Not found."}}, }
)

COLLECTION_NAME = "work"


@router.get("/", response_model=list[WorkModel], dependencies=[Depends(get_current_active_user)])
async def read() -> List[str]:
    return await Database().find(COLLECTION_NAME, 1000)


@router.get("/{work_id}", response_model=WorkModel, dependencies=[Depends(get_current_active_user)])
async def read_work_by_id(work_id: str) -> Any:
    resp = await Database().find_one(COLLECTION_NAME, {"_id": work_id})
    return resp if resp is not None else Error.generic_error(404, "Not found", 404)


@router.post("/", response_description="Add new employer", response_model=WorkModel,
             dependencies=[Depends(get_current_active_user)])
async def create(model: WorkModel = Body(...)):
    model = jsonable_encoder(model)
    new_model = await Database().insert_one(COLLECTION_NAME, model)
    created_model = await Database().find_one(
        COLLECTION_NAME, {"_id": new_model.inserted_id}
    )
    return created_model


@router.put("/{work_id}", response_description="Update employer", response_model=WorkModel,
            dependencies=[Depends(get_current_active_user)])
async def update_work(work_id: str, update_model: UpdateWorkModel = Body(...)):
    resp = await Database().update(COLLECTION_NAME, work_id, update_model)
    return resp if resp is not None else Error.generic_error(404, "Not found", 404)
