#!/usr/bin/env python3
"""
Database Clear Script
WARNING: This will delete all data from the database!
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'joinup')


async def clear_database():
    """Clear all collections in the database"""
    print(f"Connecting to MongoDB at {mongo_url}...")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Connected to MongoDB successfully\n")
        
        collections = ['users', 'events', 'registrations', 'certificates', 'ratings']
        
        print("Clearing collections...")
        for collection in collections:
            result = await db[collection].delete_many({})
            print(f"  - {collection}: {result.deleted_count} documents deleted")
        
        print("\n✓ Database cleared successfully!")
        
    except Exception as e:
        print(f"\n✗ Error clearing database: {e}")
        raise
    finally:
        client.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    print("="*50)
    print("WARNING: Database Clear Operation")
    print("="*50)
    print("\nThis will DELETE ALL DATA from the database!")
    print(f"Database: {db_name}")
    print(f"MongoDB URL: {mongo_url}")
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        response2 = input("Type 'DELETE' to confirm: ")
        if response2 == 'DELETE':
            asyncio.run(clear_database())
        else:
            print("Operation cancelled.")
    else:
        print("Operation cancelled.")
