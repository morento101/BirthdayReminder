from pydantic import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from app.database.models import User


class Settings(BaseSettings):
    FASTAPI_HOST: str
    FASTAPI_PORT: int

    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str

    CLIENT_ORIGIN: str

    class Config:
        env_file = '.env'


settings = Settings()


async def initiate_database(
    database=settings.MONGO_INITDB_DATABASE,
    mode="default"
):
    if mode == "default":
        client = AsyncIOMotorClient(settings.DATABASE_URL)
    elif mode == "test":
        client = AsyncMongoMockClient()
    else:
        raise ValueError(f"Received invalid mode option: {mode}")

    await init_beanie(
        database=client[database], 
        document_models=[User]
    )

    return client