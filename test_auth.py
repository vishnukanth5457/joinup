#!/usr/bin/env python3
"""
Simple auth flow test - no async, direct testing
"""
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import os
from dotenv import load_dotenv

# Load env
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "joinup")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-xyz123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    """Hash password"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password"""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception as e:
        print(f"❌ Password verify error: {e}")
        return False

def create_access_token(data: dict, expires_days: int = ACCESS_TOKEN_EXPIRE_DAYS):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Token decode error: {e}")
        return None

async def test_auth_flow():
    """Test complete auth flow"""
    print("[AUTH TEST] Testing Auth Flow")
    print("=" * 60)
    
    # Connect to MongoDB
    print("[1] Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        await db.command("ping")
        print("[OK] Connected to MongoDB")
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        return False
    
    # Clear test users
    print("\n[2] Clearing test data...")
    try:
        await db.users.delete_many({"email": {"$regex": "^test.*@example.com$"}})
        print("[OK] Test data cleared")
    except Exception as e:
        print(f"[ERROR] Clearing test data failed: {e}")
    
    # Test Registration
    print("\n[3] Testing Registration...")
    test_user = {
        "id": "test-user-123",
        "email": "testuser@example.com",
        "password": hash_password("password123"),
        "name": "Test User",
        "college": "Test College",
        "role": "student",
        "department": "CS",
        "year": 2,
        "organization_name": None,
        "created_at": datetime.now(timezone.utc),
        "is_approved": True,
    }
    
    try:
        result = await db.users.insert_one(test_user)
        print(f"[OK] User registered (ID: {result.inserted_id})")
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return False
    
    # Test Login
    print("\n[4] Testing Login...")
    try:
        user = await db.users.find_one({"email": "testuser@example.com"})
        if not user:
            print("[ERROR] User not found")
            return False
        
        # Test password verification
        if not verify_password("password123", user["password"]):
            print("[ERROR] Password verification failed")
            return False
        
        print("[OK] Password verified")
        
        # Create token
        token = create_access_token({"sub": user["id"], "role": user["role"]})
        print(f"[OK] Token created: {token[:50]}...")
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            print("[ERROR] Token decode failed")
            return False
        
        print(f"[OK] Token decoded: {payload}")
        
    except Exception as e:
        print(f"[ERROR] Login test failed: {e}")
        return False
    
    # Test Logout (delete token from client side)
    print("\n[5] Testing Logout...")
    try:
        # Logout is client-side (remove token from storage)
        print("[OK] Token cleared from client storage (simulated)")
    except Exception as e:
        print(f"[ERROR] Logout failed: {e}")
        return False
    
    # Clean up
    print("\n[6] Cleaning up...")
    try:
        await db.users.delete_one({"email": "testuser@example.com"})
        print("[OK] Test data cleaned")
    except Exception as e:
        print(f"[ERROR] Cleanup failed: {e}")
    
    client.close()
    print("\n[OK] All auth tests passed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_auth_flow())
    sys.exit(0 if result else 1)
