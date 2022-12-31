from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.authentication.routes import router as auth_router
from app.birthdays.routes import router as birthdays_router
from app.core.config import initiate_database, settings
from app.core.utils import custom_openapi
from app.tasks.worker import celery, create_task

app = FastAPI()

app.include_router(auth_router)
app.include_router(birthdays_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.openapi = custom_openapi(app)

app.celery = celery


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def setup_database():
    client = await initiate_database()
    app.mongodb_client = client
    create_task.delay()


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
