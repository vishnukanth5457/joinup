import asyncio
import uuid
from datetime import datetime
import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# ✅ Load .env file (important if script is in /database)
load_dotenv(dotenv_path="/.env")

# ✅ Correct environment variable names
MONGO_URL = os.getenv("mongodb://localhost:27017")
DB_NAME = os.getenv("joinup")

# ✅ Safety checks (VERY IMPORTANT)
if not MONGO_URL:
    raise RuntimeError("❌ MONGO_URL not found in .env")
if not DB_NAME:
    raise RuntimeError("❌ DB_NAME not found in .env")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

async def seed_data():
    # ---------------- USERS ----------------
    users = [
        {
            "id": str(uuid.uuid4()),
            "email": "student1@test.com",
            "password": "hashed_password",
            "name": "Student One",
            "role": "student",
            "college": "MIT",
            "department": "CSE",
            "year": 3,
            "is_approved": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "organizer@test.com",
            "password": "hashed_password",
            "name": "Tech Club MIT",
            "role": "organizer",
            "college": "MIT",
            "organization_name": "Tech Club",
            "is_approved": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "admin@test.com",
            "password": "hashed_password",
            "name": "Admin User",
            "role": "admin",
            "is_approved": True,
            "created_at": datetime.utcnow()
        }
    ]

    await db.users.insert_many(users)
    print("✅ Users inserted")

    student_id = users[0]["id"]
    organizer_id = users[1]["id"]

    # ---------------- EVENTS ----------------
    event_id = str(uuid.uuid4())
    event = {
        "id": event_id,
        "title": "Tech Fest 2025",
        "description": "Annual technology festival",
        "date": datetime.utcnow(),
        "venue": "Main Auditorium",
        "fee": 500,
        "college": "MIT",
        "category": "Technology",
        "max_participants": 200,
        "organizer_id": organizer_id,
        "organizer_name": "Tech Club MIT",
        "current_registrations": 1,
        "average_rating": 0,
        "total_ratings": 0,
        "created_at": datetime.utcnow()
    }

    await db.events.insert_one(event)
    print("✅ Event inserted")

    # ---------------- REGISTRATIONS ----------------
    registration_id = str(uuid.uuid4())
    registration = {
        "id": registration_id,
        "student_id": student_id,
        "student_name": "Student One",
        "event_id": event_id,
        "event_title": "Tech Fest 2025",
        "payment_status": "paid",
        "qr_code_data": f"joinup-{uuid.uuid4()}",
        "attendance_marked": False,
        "certificate_issued": False,
        "created_at": datetime.utcnow()
    }

    await db.registrations.insert_one(registration)
    print("✅ Registration inserted")

    # ---------------- CERTIFICATES ----------------
    certificate = {
        "id": str(uuid.uuid4()),
        "registration_id": registration_id,
        "student_id": student_id,
        "student_name": "Student One",
        "event_id": event_id,
        "event_title": "Tech Fest 2025",
        "issued_date": datetime.utcnow(),
        "certificate_data": "BASE64_PDF_DATA"
    }

    await db.certificates.insert_one(certificate)
    print("✅ Certificate inserted")

    # ---------------- RATINGS ----------------
    rating = {
        "id": str(uuid.uuid4()),
        "event_id": event_id,
        "student_id": student_id,
        "student_name": "Student One",
        "rating": 5,
        "feedback": "Excellent event!",
        "created_at": datetime.utcnow()
    }

    await db.ratings.insert_one(rating)
    print("✅ Rating inserted")

    print("\n🎉 Dummy data seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
