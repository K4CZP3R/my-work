from starlette.responses import JSONResponse

from helpers.error import EntryNotFound, EntryMalformed, Error
from models.event import UpdateEventModel, EventModel
from fastapi import APIRouter, Body, Depends
from models.response import ResponseErrorModel
from typing import List, Any
from helpers.database import Database
from fastapi.encoders import jsonable_encoder
from routers.authentication_router import get_current_active_user
from models.event import EventModelFactory

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"Error": {"message": "Not found."}}},
)

COLLECTION_NAME = "event"


@router.get("/", response_model=list[EventModel], dependencies=[Depends(get_current_active_user)])
async def read() -> List[EventModel]:
    return await EventModelFactory().get_all()


@router.get("/{event_id}", response_model=EventModel, dependencies=[Depends(get_current_active_user)])
async def read_event_by_id(event_id: str) -> Any:
    try:
        return await EventModelFactory().get_by_id(event_id)
    except EntryNotFound as e:
        return Error().generic_error(404, "Not found.", 404)
    except EntryMalformed as e:
        return Error().generic_error(500, "Malformed.", 500)


@router.post("/", response_description="Add new event", response_model=EventModel,
             dependencies=[Depends(get_current_active_user)])
async def create(model: EventModel = Body(...)):
    try:
        return await EventModelFactory().create_from_model(model)
    except EntryNotFound as e:
        return Error().generic_error(404, "Not found.", 404)
    except EntryMalformed as e:
        return Error().generic_error(500, "Malformed.", 500)


@router.put(
    "/{event_id}", response_description="Update employer", response_model=EventModel,
    dependencies=[Depends(get_current_active_user)]
)
async def update_event(event_id: str, update_model: UpdateEventModel = Body(...)):
    try:
        return await EventModelFactory().update_by_id_with_model(event_id, update_model)
    except EntryNotFound as e:
        return Error().generic_error(404, "Not found.", 404)
    except EntryMalformed as e:
        return Error().generic_error(500, "Malformed", 500)
