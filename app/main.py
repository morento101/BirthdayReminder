from fastapi import FastAPI
from app.authentication.routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, initiate_database

app = FastAPI()

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


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(auth_router)


@app.get("/")
async def home():
    return {"data": "Home Page"}
