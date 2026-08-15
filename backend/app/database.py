from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    if not settings.MONGO_URI:
        print("❌ Error: MONGO_URI is missing in environment variables.")
        return
    
    db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)
    db_instance.db = db_instance.client[settings.DB_NAME]
    try:
        await db_instance.client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ MongoDB Atlas Connection Error: {e}")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        print("🔌 MongoDB Atlas connection closed.")

def get_database():
    return db_instance.db