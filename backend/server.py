from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List
import uuid
from datetime import datetime, timedelta

from models import (
    UserCreate, UserLogin, User, TokenResponse, UserRole,
    EventCreate, Event, RegistrationCreate, Registration,
    AttendanceMarkRequest, CertificateIssueRequest, Certificate,
    StudentDashboard, PaymentStatus
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_role
)
from utils import generate_qr_code, generate_certificate_pdf

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="JoinUp API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix=\"/api\")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= AUTH ROUTES =============
@api_router.post(\"/auth/register\", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({\"email\": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail=\"Email already registered\")
    
    # Create user
    user_dict = user_data.model_dump()
    user_dict[\"password\"] = get_password_hash(user_data.password)
    user_dict[\"id\"] = str(uuid.uuid4())
    user_dict[\"is_approved\"] = True if user_data.role != UserRole.ORGANIZER else True  # Auto-approve for MVP
    user_dict[\"created_at\"] = datetime.utcnow()
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token(data={\"sub\": user_dict[\"id\"], \"role\": user_dict[\"role\"]})
    
    # Remove password from response
    del user_dict[\"password\"]
    del user_dict[\"_id\"]
    
    return TokenResponse(access_token=access_token, user=User(**user_dict))

@api_router.post(\"/auth/login\", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({\"email\": credentials.email})
    if not user or not verify_password(credentials.password, user[\"password\"]):
        raise HTTPException(status_code=401, detail=\"Invalid credentials\")
    
    if not user.get(\"is_approved\", True):
        raise HTTPException(status_code=403, detail=\"Account not approved yet\")
    
    access_token = create_access_token(data={\"sub\": user[\"id\"], \"role\": user[\"role\"]})
    
    del user[\"password\"]
    del user[\"_id\"]
    
    return TokenResponse(access_token=access_token, user=User(**user))

@api_router.get(\"/auth/me\", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({\"id\": current_user[\"sub\"]})
    if not user:
        raise HTTPException(status_code=404, detail=\"User not found\")
    del user[\"password\"]
    del user[\"_id\"]
    return User(**user)

# ============= EVENT ROUTES =============
@api_router.post(\"/events\", response_model=Event)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(require_role([UserRole.ORGANIZER]))
):
    organizer = await db.users.find_one({\"id\": current_user[\"sub\"]})
    
    event_dict = event_data.model_dump()
    event_dict[\"id\"] = str(uuid.uuid4())
    event_dict[\"organizer_id\"] = current_user[\"sub\"]
    event_dict[\"organizer_name\"] = organizer[\"name\"]
    event_dict[\"current_registrations\"] = 0
    event_dict[\"created_at\"] = datetime.utcnow()
    
    await db.events.insert_one(event_dict)
    del event_dict[\"_id\"]
    
    return Event(**event_dict)

@api_router.get(\"/events\", response_model=List[Event])
async def get_events(
    search: str = None,
    college: str = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if search:
        query[\"$or\"] = [
            {\"title\": {\"$regex\": search, \"$options\": \"i\"}},
            {\"description\": {\"$regex\": search, \"$options\": \"i\"}}
        ]
    if college:
        query[\"college\"] = college
    
    events = await db.events.find(query).sort(\"date\", 1).to_list(1000)
    return [Event(**{**event, \"_id\": str(event[\"_id\"])}) for event in events]

@api_router.get(\"/events/{event_id}\", response_model=Event)
async def get_event(event_id: str, current_user: dict = Depends(get_current_user)):
    event = await db.events.find_one({\"id\": event_id})
    if not event:
        raise HTTPException(status_code=404, detail=\"Event not found\")
    del event[\"_id\"]
    return Event(**event)

@api_router.get(\"/events/organizer/my-events\", response_model=List[Event])
async def get_my_events(current_user: dict = Depends(require_role([UserRole.ORGANIZER]))):
    events = await db.events.find({\"organizer_id\": current_user[\"sub\"]}).sort(\"date\", -1).to_list(1000)
    return [Event(**{**event, \"_id\": str(event[\"_id\"])}) for event in events]

# ============= REGISTRATION ROUTES =============
@api_router.post(\"/registrations\", response_model=Registration)
async def register_for_event(
    reg_data: RegistrationCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    # Check if event exists
    event = await db.events.find_one({\"id\": reg_data.event_id})
    if not event:
        raise HTTPException(status_code=404, detail=\"Event not found\")
    
    # Check if already registered
    existing = await db.registrations.find_one({
        \"student_id\": current_user[\"sub\"],
        \"event_id\": reg_data.event_id
    })
    if existing:
        raise HTTPException(status_code=400, detail=\"Already registered for this event\")
    
    # Check max participants
    if event.get(\"max_participants\") and event[\"current_registrations\"] >= event[\"max_participants\"]:
        raise HTTPException(status_code=400, detail=\"Event is full\")
    
    # Get student info
    student = await db.users.find_one({\"id\": current_user[\"sub\"]})
    
    # Create registration
    reg_id = str(uuid.uuid4())
    qr_data = f\"joinup-{reg_id}\"
    
    reg_dict = {
        \"id\": reg_id,
        \"student_id\": current_user[\"sub\"],
        \"student_name\": student[\"name\"],
        \"event_id\": reg_data.event_id,
        \"event_title\": event[\"title\"],
        \"payment_status\": PaymentStatus.PAID,  # Mock payment
        \"qr_code_data\": qr_data,
        \"attendance_marked\": False,
        \"attendance_time\": None,
        \"certificate_issued\": False,
        \"created_at\": datetime.utcnow()
    }
    
    await db.registrations.insert_one(reg_dict)
    
    # Update event registration count
    await db.events.update_one(
        {\"id\": reg_data.event_id},
        {\"$inc\": {\"current_registrations\": 1}}
    )
    
    del reg_dict[\"_id\"]
    return Registration(**reg_dict)

@api_router.get(\"/registrations/my-registrations\", response_model=List[Registration])
async def get_my_registrations(current_user: dict = Depends(require_role([UserRole.STUDENT]))):
    registrations = await db.registrations.find({\"student_id\": current_user[\"sub\"]}).sort(\"created_at\", -1).to_list(1000)
    return [Registration(**{**reg, \"_id\": str(reg[\"_id\"])}) for reg in registrations]

@api_router.get(\"/registrations/event/{event_id}\", response_model=List[Registration])
async def get_event_registrations(
    event_id: str,
    current_user: dict = Depends(require_role([UserRole.ORGANIZER]))
):
    # Verify organizer owns this event
    event = await db.events.find_one({\"id\": event_id, \"organizer_id\": current_user[\"sub\"]})
    if not event:
        raise HTTPException(status_code=404, detail=\"Event not found or access denied\")
    
    registrations = await db.registrations.find({\"event_id\": event_id}).to_list(1000)
    return [Registration(**{**reg, \"_id\": str(reg[\"_id\"])}) for reg in registrations]

# ============= ATTENDANCE ROUTES =============
@api_router.post(\"/attendance/mark\")
async def mark_attendance(
    attendance_data: AttendanceMarkRequest,
    current_user: dict = Depends(require_role([UserRole.ORGANIZER]))
):
    registration = await db.registrations.find_one({\"qr_code_data\": attendance_data.qr_code_data})
    if not registration:
        raise HTTPException(status_code=404, detail=\"Invalid QR code\")
    
    # Verify organizer owns the event
    event = await db.events.find_one({\"id\": registration[\"event_id\"], \"organizer_id\": current_user[\"sub\"]})
    if not event:
        raise HTTPException(status_code=403, detail=\"You don't have permission to mark attendance for this event\")
    
    if registration[\"attendance_marked\"]:
        raise HTTPException(status_code=400, detail=\"Attendance already marked\")
    
    await db.registrations.update_one(
        {\"id\": registration[\"id\"]},
        {\"$set\": {\"attendance_marked\": True, \"attendance_time\": datetime.utcnow()}}
    )
    
    return {\"message\": \"Attendance marked successfully\", \"student_name\": registration[\"student_name\"]}

# ============= CERTIFICATE ROUTES =============
@api_router.post(\"/certificates/issue\", response_model=Certificate)
async def issue_certificate(
    cert_data: CertificateIssueRequest,
    current_user: dict = Depends(require_role([UserRole.ORGANIZER]))
):
    registration = await db.registrations.find_one({\"id\": cert_data.registration_id})
    if not registration:
        raise HTTPException(status_code=404, detail=\"Registration not found\")
    
    # Verify organizer owns the event
    event = await db.events.find_one({\"id\": registration[\"event_id\"], \"organizer_id\": current_user[\"sub\"]})
    if not event:
        raise HTTPException(status_code=403, detail=\"Access denied\")
    
    if not registration[\"attendance_marked\"]:
        raise HTTPException(status_code=400, detail=\"Cannot issue certificate - attendance not marked\")
    
    if registration[\"certificate_issued\"]:
        # Return existing certificate
        existing_cert = await db.certificates.find_one({\"registration_id\": cert_data.registration_id})
        if existing_cert:
            del existing_cert[\"_id\"]
            return Certificate(**existing_cert)
    
    # Generate certificate
    event_date = event[\"date\"].strftime(\"%B %d, %Y\")
    cert_pdf = generate_certificate_pdf(registration[\"student_name\"], event[\"title\"], event_date)
    
    cert_dict = {
        \"id\": str(uuid.uuid4()),
        \"registration_id\": cert_data.registration_id,
        \"student_id\": registration[\"student_id\"],
        \"student_name\": registration[\"student_name\"],
        \"event_id\": registration[\"event_id\"],
        \"event_title\": registration[\"event_title\"],
        \"issued_date\": datetime.utcnow(),
        \"certificate_data\": cert_pdf
    }
    
    await db.certificates.insert_one(cert_dict)
    await db.registrations.update_one(
        {\"id\": cert_data.registration_id},
        {\"$set\": {\"certificate_issued\": True}}
    )
    
    del cert_dict[\"_id\"]
    return Certificate(**cert_dict)

@api_router.get(\"/certificates/my-certificates\", response_model=List[Certificate])
async def get_my_certificates(current_user: dict = Depends(require_role([UserRole.STUDENT]))):
    certificates = await db.certificates.find({\"student_id\": current_user[\"sub\"]}).sort(\"issued_date\", -1).to_list(1000)
    return [Certificate(**{**cert, \"_id\": str(cert[\"_id\"])}) for cert in certificates]

# ============= DASHBOARD ROUTES =============
@api_router.get(\"/dashboard/student\", response_model=StudentDashboard)
async def get_student_dashboard(current_user: dict = Depends(require_role([UserRole.STUDENT]))):
    registrations = await db.registrations.find({\"student_id\": current_user[\"sub\"]}).to_list(1000)
    
    total_events = len(registrations)
    attended_events = sum(1 for reg in registrations if reg[\"attendance_marked\"])
    certificates_earned = sum(1 for reg in registrations if reg[\"certificate_issued\"])
    
    # Upcoming events (not attended yet and event date is in future)
    upcoming = 0
    for reg in registrations:
        if not reg[\"attendance_marked\"]:
            event = await db.events.find_one({\"id\": reg[\"event_id\"]})
            if event and event[\"date\"] > datetime.utcnow():
                upcoming += 1
    
    return StudentDashboard(
        total_events_registered=total_events,
        attended_events=attended_events,
        certificates_earned=certificates_earned,
        upcoming_events=upcoming
    )

# ============= ADMIN ROUTES =============
@api_router.get(\"/admin/users\", response_model=List[User])
async def get_all_users(current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    users = await db.users.find().to_list(1000)
    result = []
    for user in users:
        del user[\"password\"]
        del user[\"_id\"]
        result.append(User(**user))
    return result

@api_router.get(\"/admin/events\", response_model=List[Event])
async def get_all_events_admin(current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    events = await db.events.find().sort(\"created_at\", -1).to_list(1000)
    return [Event(**{**event, \"_id\": str(event[\"_id\"])}) for event in events]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[\"*\"],
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

@app.on_event(\"shutdown\")
async def shutdown_db_client():
    client.close()
