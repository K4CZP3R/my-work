from starlette.responses import JSONResponse
from models.event import UpdateEventModel, EventModel
from fastapi import APIRouter, Body, Depends
from models.response import ResponseErrorModel
from typing import List
from helpers.database import Database
from fastapi.encoders import jsonable_encoder
from routers.authentication_router import get_current_active_user

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"Error": {"message": "Not found."}}},
)

COLLECTION_NAME = "event"


@router.get("/", response_model=list[EventModel], dependencies=[Depends(get_current_active_user)])
async def read() -> List[EventModel]:
    return await Database().find(COLLECTION_NAME, 1000)


@router.get("/{id}", response_model=EventModel, dependencies=[Depends(get_current_active_user)])
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


@router.post("/", response_description="Add new event", response_model=EventModel, dependencies=[Depends(get_current_active_user)])
async def create(model: EventModel = Body(...)):
    model = jsonable_encoder(model)
    new_model = await Database().insert_one(COLLECTION_NAME, model)
    created_model = await Database().find_one(
        COLLECTION_NAME, {"_id": new_model.inserted_id}
    )
    return created_model


@router.put(
    "/{id}", response_description="Update employer", response_model=EventModel, dependencies=[Depends(get_current_active_user)]
)
async def update_work(id: str, update_model: UpdateEventModel = Body(...)):
    resp = await Database().update(COLLECTION_NAME, id, update_model)

    if resp is None:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(
                ResponseErrorModel(message="Not found.", code=404)
            ),
        )
    return resp
