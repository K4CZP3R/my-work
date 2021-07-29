from fastapi.middleware.cors import CORSMiddleware
from logging.config import dictConfig
from helpers.database import Database
from my_log_conf import log_config
from routers import employer_router
from routers import event_router
from routers import report_router
from routers import work_router
from routers import authentication_router
from fastapi import FastAPI
from helpers.log import Log

origins = ["http://127.0.0.1:4200"]

db = Database()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def on_startup():
    dictConfig(log_config)
    Log().info("My-Work startup!")


app.include_router(work_router.router)
app.include_router(employer_router.router)
app.include_router(event_router.router)
app.include_router(report_router.router)
app.include_router(authentication_router.router)
