from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

from app.database.models import BirthdayModel, UserModel


class Settings(BaseSettings):
    SECRET_KEY: str

    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str
    CLIENT_ORIGIN: str

    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str

    MONGO_URL: str = "mongodb://admin:password@mongodb:27017/?authSource=admin"
    MONGO_INITDB_DATABASE: str

    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    class Config:
        env_file = '.env'


settings = Settings()


async def initiate_database(
    database=settings.MONGO_INITDB_DATABASE,
    mode="default"
):
    if mode == "default":
        client = AsyncIOMotorClient(settings.MONGO_URL)
    elif mode == "test":
        client = AsyncMongoMockClient()
    else:
        raise ValueError(f"Received invalid mode option: {mode}")

    await init_beanie(
        database=client[database],
        document_models=[UserModel, BirthdayModel]
    )

    return client
