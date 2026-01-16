from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
import os
from dotenv import load_dotenv
import logging
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "joinup")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Initialize MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Initialize FastAPI app
app = FastAPI(title="JoinUp API", version="1.0.0")

# Add CORS middleware FIRST (before routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ===== MODELS =====
class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    college: str
    role: str = "student"
    department: Optional[str] = None
    year: Optional[int] = None
    organization_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    college: str
    role: str
    department: Optional[str] = None
    year: Optional[int] = None
    organization_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ===== UTILITY FUNCTIONS =====
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(data: dict, expires_days: int = ACCESS_TOKEN_EXPIRE_DAYS):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: Optional[dict] = Depends(lambda: None)):
    """Get current user from token - placeholder for now"""
    # This is used as an optional dependency for routes that don't require auth
    return credentials

def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ===== AUTH ROUTES =====
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        logger.info(f"Registration attempt for: {user_data.email}")
        
        # Validate input
        if not user_data.email or not user_data.password or not user_data.name:
            raise HTTPException(status_code=400, detail="Email, password, and name are required")
        
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email.lower()})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user_data.password)
        
        user_dict = {
            "id": user_id,
            "email": user_data.email.lower(),
            "password": hashed_password,
            "name": user_data.name,
            "college": user_data.college,
            "role": user_data.role or "student",
            "department": user_data.department,
            "year": user_data.year,
            "organization_name": user_data.organization_name,
            "created_at": datetime.now(timezone.utc),
            "is_approved": True,
        }
        
        await db.users.insert_one(user_dict)
        logger.info(f"User registered: {user_data.email}")
        
        # Create token
        access_token = create_access_token({"sub": user_id, "role": user_data.role or "student"})
        
        # Return user without password
        user_response = UserResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            college=user_data.college,
            role=user_data.role or "student",
            department=user_data.department,
            year=user_data.year,
            organization_name=user_data.organization_name,
        )
        
        return TokenResponse(access_token=access_token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    try:
        logger.info(f"Login attempt for: {credentials.email}")
        
        if not credentials.email or not credentials.password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        # Find user
        user = await db.users.find_one({"email": credentials.email.lower()})
        if not user:
            logger.warning(f"User not found: {credentials.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(credentials.password, user["password"]):
            logger.warning(f"Invalid password for: {credentials.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create token
        access_token = create_access_token({"sub": user["id"], "role": user["role"]})
        logger.info(f"User logged in: {credentials.email}")
        
        # Return user without password
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            college=user["college"],
            role=user["role"],
            department=user.get("department"),
            year=user.get("year"),
            organization_name=user.get("organization_name"),
        )
        
        return TokenResponse(access_token=access_token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to ping MongoDB using client.admin
        await client.admin.command('ping')
        return {"status": "healthy", "service": "JoinUp API", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {"status": "unhealthy", "service": "JoinUp API", "database": "disconnected"}

# ===== TEST ROUTE =====
@app.get("/api/test")
async def test_route():
    """Test route to verify API is working"""
    return {"message": "API is working", "timestamp": datetime.now(timezone.utc).isoformat()}

# ===== EVENTS ROUTES =====
@app.get("/api/events")
async def get_events(search: str = None, current_user: dict = None):
    """Get all events with optional search"""
    try:
        query = {}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        events = await db.events.find(query).to_list(100)
        return [
            {
                "id": event.get("id", str(event.get("_id"))),
                "title": event.get("title", ""),
                "description": event.get("description", ""),
                "date": event.get("date", ""),
                "venue": event.get("venue", ""),
                "fee": event.get("fee", 0),
                "college": event.get("college", ""),
                "category": event.get("category", ""),
                "organizer_name": event.get("organizer_name", ""),
                "current_registrations": event.get("current_registrations", 0),
                "max_participants": event.get("max_participants"),
            }
            for event in events
        ]
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        return []

@app.get("/api/dashboard/student")
async def get_student_dashboard(current_user: dict = None):
    """Get student dashboard stats"""
    try:
        # For now, return dummy stats - backend can track these later
        return {
            "total_events_registered": 0,
            "attended_events": 0,
            "certificates_earned": 0,
            "upcoming_events": 0,
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        return {
            "total_events_registered": 0,
            "attended_events": 0,
            "certificates_earned": 0,
            "upcoming_events": 0,
        }

@app.get("/api/dashboard/organizer")
async def get_organizer_dashboard(current_user: dict = None):
    """Get organizer dashboard stats"""
    try:
        return {
            "total_events_created": 0,
            "total_registrations": 0,
            "total_attendees": 0,
            "pending_certificates": 0,
        }
    except Exception as e:
        logger.error(f"Error fetching organizer dashboard: {str(e)}")
        return {
            "total_events_created": 0,
            "total_registrations": 0,
            "total_attendees": 0,
            "pending_certificates": 0,
        }

@app.get("/api/events/organizer/my-events")
async def get_organizer_events(current_user: dict = None):
    """Get events created by organizer"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        organizer_id = current_user.get("sub")
        events = await db.events.find({"organizer_id": organizer_id}).to_list(None)
        
        return [
            {
                "id": event.get("id"),
                "title": event.get("title"),
                "description": event.get("description"),
                "date": event.get("date"),
                "venue": event.get("venue"),
                "current_registrations": event.get("current_registrations", 0),
                "max_participants": event.get("max_participants"),
            }
            for event in events
        ]
    except Exception as e:
        logger.error(f"Error fetching organizer events: {str(e)}")
        return []

@app.post("/api/events")
async def create_event(event_data: dict):
    """Create new event"""
    try:
        event_dict = {
            "id": str(uuid.uuid4()),
            "title": event_data.get("title", ""),
            "description": event_data.get("description", ""),
            "date": event_data.get("date", ""),
            "venue": event_data.get("venue", ""),
            "fee": event_data.get("fee", 0),
            "college": event_data.get("college", ""),
            "category": event_data.get("category", ""),
            "organizer_name": event_data.get("organizer_name", ""),
            "current_registrations": 0,
            "max_participants": event_data.get("max_participants"),
            "created_at": datetime.now(timezone.utc),
        }
        
        result = await db.events.insert_one(event_dict)
        event_dict["_id"] = str(result.inserted_id)
        
        # Remove MongoDB _id from response
        response = {k: v for k, v in event_dict.items() if k != "_id"}
        return response
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to create event")

@app.get("/api/registrations/my-registrations")
async def get_my_registrations():
    """Get user's event registrations"""
    try:
        registrations = await db.registrations.find({}).to_list(100)
        return [
            {
                "id": reg.get("id", str(reg.get("_id"))),
                "event_id": reg.get("event_id", ""),
                "user_id": reg.get("user_id", ""),
                "status": reg.get("status", "registered"),
                "created_at": reg.get("created_at", ""),
            }
            for reg in registrations
        ]
    except Exception as e:
        logger.error(f"Error fetching registrations: {str(e)}")
        return []

@app.post("/api/registrations")
async def register_for_event(registration_data: dict):
    """Register for an event"""
    try:
        registration_dict = {
            "id": str(uuid.uuid4()),
            "event_id": registration_data.get("event_id"),
            "user_id": registration_data.get("user_id"),
            "status": "registered",
            "created_at": datetime.now(timezone.utc),
        }
        
        result = await db.registrations.insert_one(registration_dict)
        registration_dict["_id"] = str(result.inserted_id)
        
        # Remove MongoDB _id from response
        response = {k: v for k, v in registration_dict.items() if k != "_id"}
        return response
    except Exception as e:
        logger.error(f"Error registering for event: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to register")

# ===== STARTUP/SHUTDOWN =====
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    try:
        # Check if MongoDB is available
        result = await client.admin.command('ping')
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"MongoDB connection warning (will try again on first request): {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
