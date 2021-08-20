from fastapi.middleware.cors import CORSMiddleware
from logging.config import dictConfig

from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

import config
from helpers.database import Database
from my_log_conf import log_config
from routers import employer_router
from routers import event_router
from routers import report_router
from routers import work_router
from routers import authentication_router
from fastapi import FastAPI
from helpers.log import Log
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

origins = ["http://127.0.0.1:4200", "http://localhost:4200"]

db = Database()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def on_startup():
    dictConfig(log_config)
    Log().info("My-Work startup!")


@app.get("/wipe/{key}")
@limiter.limit("60/minute")
async def wipe_db(key: str, request: Request):
    if config.SECRET_KEY == key:
        await db.wipe_all()
        return {"status": "ok"}
    return {"status": "notok"}


app.include_router(work_router.router)
app.include_router(employer_router.router)
app.include_router(event_router.router)
app.include_router(report_router.router)
app.include_router(authentication_router.router)
