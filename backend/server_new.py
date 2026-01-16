from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from dotenv import load_dotenv
import logging

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
    department: str = None
    year: int = None
    organization_name: str = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    college: str
    role: str
    department: str = None
    year: int = None
    organization_name: str = None

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
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(lambda: None)):
    """Get current user from token"""
    # For now, this is a placeholder - we'll implement token verification later
    return None

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
        import uuid
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
            "created_at": datetime.utcnow(),
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
        # Try to ping MongoDB
        await db.admin.command('ping')
        return {"status": "healthy", "service": "JoinUp API", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {"status": "unhealthy", "service": "JoinUp API", "database": "disconnected"}

# ===== TEST ROUTE =====
@app.get("/api/test")
async def test_route():
    """Test route to verify API is working"""
    return {"message": "API is working", "timestamp": datetime.utcnow()}

# ===== STARTUP/SHUTDOWN =====
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    try:
        await db.admin.command('ping')
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
