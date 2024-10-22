# app.database.py
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_client():
    MONGO_URL = os.getenv("MONGO_URL")
    client = AsyncIOMotorClient(MONGO_URL)
    return client



# Get database
db = get_db_client().product_management

# Collections
products_collection = db.products



# Database helper functions
async def get_db():
    try:
        yield db
    finally:
        pass
