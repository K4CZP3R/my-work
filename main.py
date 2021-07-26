from fastapi import FastAPI

from routers import work_router
from helpers.database import Database
from routers import employer_router


Database()

app = FastAPI()


app.include_router(work_router.router)
app.include_router(employer_router.router)
