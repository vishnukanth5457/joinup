#!/usr/bin/env python3
"""
Clean up test data and run fresh test
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "joinup")

async def cleanup():
    """Clean up test data"""
    print("Cleaning up test data...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Delete test users
    result = await db.users.delete_many({"email": {"$regex": ".*@example.com$"}})
    print(f"Deleted {result.deleted_count} test users")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup())
