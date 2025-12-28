#!/usr/bin/env python3
"""
MongoDB Index Creation Script
Creates all necessary indexes for optimal query performance
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


async def create_indexes():
    """Create all database indexes"""
    print(f"Connecting to MongoDB at {mongo_url}...")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Connected to MongoDB successfully")
        
        # USERS Collection Indexes
        print("\nCreating indexes for 'users' collection...")
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
        await db.users.create_index("role")
        await db.users.create_index("college")
        await db.users.create_index("created_at")
        print("✓ Users indexes created")
        
        # EVENTS Collection Indexes
        print("\nCreating indexes for 'events' collection...")
        await db.events.create_index("id", unique=True)
        await db.events.create_index("organizer_id")
        await db.events.create_index("date")
        await db.events.create_index("college")
        await db.events.create_index("category")
        await db.events.create_index("average_rating")
        await db.events.create_index("created_at")
        # Compound index for search
        await db.events.create_index([("title", "text"), ("description", "text")])
        print("✓ Events indexes created")
        
        # REGISTRATIONS Collection Indexes
        print("\nCreating indexes for 'registrations' collection...")
        await db.registrations.create_index("id", unique=True)
        await db.registrations.create_index("student_id")
        await db.registrations.create_index("event_id")
        await db.registrations.create_index("qr_code_data", unique=True)
        await db.registrations.create_index("attendance_marked")
        await db.registrations.create_index("created_at")
        # Compound unique index to prevent duplicate registrations
        await db.registrations.create_index(
            [("student_id", 1), ("event_id", 1)],
            unique=True
        )
        print("✓ Registrations indexes created")
        
        # CERTIFICATES Collection Indexes
        print("\nCreating indexes for 'certificates' collection...")
        await db.certificates.create_index("id", unique=True)
        await db.certificates.create_index("registration_id", unique=True)
        await db.certificates.create_index("student_id")
        await db.certificates.create_index("event_id")
        await db.certificates.create_index("issued_date")
        print("✓ Certificates indexes created")
        
        # RATINGS Collection Indexes
        print("\nCreating indexes for 'ratings' collection...")
        await db.ratings.create_index("id", unique=True)
        await db.ratings.create_index("event_id")
        await db.ratings.create_index("student_id")
        await db.ratings.create_index("rating")
        await db.ratings.create_index("created_at")
        # Compound unique index to prevent duplicate ratings
        await db.ratings.create_index(
            [("student_id", 1), ("event_id", 1)],
            unique=True
        )
        print("✓ Ratings indexes created")
        
        print("\n" + "="*50)
        print("✓ All indexes created successfully!")
        print("="*50)
        
        # List all indexes
        print("\nCreated indexes:")
        for collection_name in ['users', 'events', 'registrations', 'certificates', 'ratings']:
            indexes = await db[collection_name].list_indexes().to_list(None)
            print(f"\n{collection_name}:")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx.get('key', {})}")
        
    except Exception as e:
        print(f"\n✗ Error creating indexes: {e}")
        raise
    finally:
        client.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    print("="*50)
    print("MongoDB Index Creation for JoinUp")
    print("="*50)
    asyncio.run(create_indexes())
