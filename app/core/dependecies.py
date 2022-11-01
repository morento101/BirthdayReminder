from core.settings import MONGODB_URL
import motor.motor_asyncio


def get_db():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client.birthday_reminder
        yield db
    finally:
        client.close()
