from core.settings import MONGODB_URL
import motor.motor_asyncio


def get_client():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        yield client
    finally:
        client.close()
