import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# =========================
# Environment Configuration
# =========================
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "joinup")

# =========================
# Database Initialization
# =========================
async def init_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("🔗 Connected to MongoDB")

    # =========================
    # USERS COLLECTION
    # =========================
    users = db.users
    await users.create_index("email", unique=True)
    await users.create_index("id", unique=True)
    await users.create_index("role")
    await users.create_index("college")

    print("✅ users collection indexes created")

    # =========================
    # EVENTS COLLECTION
    # =========================
    events = db.events
    await events.create_index("id", unique=True)
    await events.create_index("organizer_id")
    await events.create_index("date")
    await events.create_index("college")
    await events.create_index("category")
    await events.create_index("average_rating")

    print("✅ events collection indexes created")

    # =========================
    # REGISTRATIONS COLLECTION
    # =========================
    registrations = db.registrations
    await registrations.create_index("id", unique=True)
    await registrations.create_index("student_id")
    await registrations.create_index("event_id")
    await registrations.create_index("qr_code_data", unique=True)
    await registrations.create_index(
        [("student_id", 1), ("event_id", 1)],
        unique=True
    )

    print("✅ registrations collection indexes created")

    # =========================
    # CERTIFICATES COLLECTION
    # =========================
    certificates = db.certificates
    await certificates.create_index("id", unique=True)
    await certificates.create_index("registration_id", unique=True)
    await certificates.create_index("student_id")
    await certificates.create_index("event_id")

    print("✅ certificates collection indexes created")

    # =========================
    # RATINGS COLLECTION
    # =========================
    ratings = db.ratings
    await ratings.create_index("id", unique=True)
    await ratings.create_index("event_id")
    await ratings.create_index("student_id")
    await ratings.create_index(
        [("student_id", 1), ("event_id", 1)],
        unique=True
    )

    print("✅ ratings collection indexes created")

    print("\n🎉 MongoDB initialization completed successfully!")

# =========================
# Script Entry Point
# =========================
if __name__ == "__main__":
    asyncio.run(init_database())
