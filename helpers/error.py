from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from models.response import ResponseErrorModel


class EntryNotFound(Exception):
    pass


class Error:
    @staticmethod
    def generic_error(http_error_code: int, message: str, app_error_code: int) -> JSONResponse:
        return JSONResponse(
            status_code=http_error_code,
            content=jsonable_encoder(
                ResponseErrorModel(message=message, code=app_error_code)
            ),
        )
