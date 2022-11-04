from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from pymongo import ASCENDING

client = AsyncIOMotorClient(settings.DATABASE_URL)

# try:
#     conn = client.server_info()
#     print(f'Connected to MongoDB {conn.get("version")}')

# except Exception:
#     print("Unable to connect to the MongoDB server.")

client.server_info()
db = client[settings.MONGO_INITDB_DATABASE]
user_collection = db.users
user_collection.create_index([("email", ASCENDING)], unique=True)
