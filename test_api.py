#!/usr/bin/env python3
"""
Test HTTP API endpoints with direct requests
"""
import requests
import json
import time
import subprocess
import os
import signal

BASE_URL = "http://localhost:8000"

def start_server():
    """Start backend server"""
    print("🚀 Starting backend server...")
    backend_path = r"c:\Users\vishnukanth\OneDrive\文档\GitHub\joinup\backend"
    cmd = f'cd "{backend_path}" && python -m uvicorn server:app --port 8000 --log-level error'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)  # Give server time to start
    print("✅ Server started (PID: {})".format(proc.pid))
    return proc

def stop_server(proc):
    """Stop backend server"""
    print("\n🛑 Stopping server...")
    try:
        os.kill(proc.pid, signal.SIGTERM)
        time.sleep(1)
    except:
        pass

def test_register():
    """Test registration endpoint"""
    print("\n📝 Testing Registration...")
    data = {
        "email": "apitest@example.com",
        "password": "password123",
        "name": "API Test User",
        "college": "Test College",
        "role": "student"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Registration successful")
            print(f"   Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"   User: {result.get('user', {}).get('email')}")
            return result.get('access_token'), result.get('user', {}).get('id')
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None

def test_login():
    """Test login endpoint"""
    print("\n🔓 Testing Login...")
    data = {
        "email": "apitest@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login successful")
            print(f"   Token: {result.get('access_token', 'N/A')[:50]}...")
            return result.get('access_token')
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_protected_route(token):
    """Test protected route"""
    print("\n🔐 Testing Protected Route...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/events", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Protected route accessible")
            print(f"   Events count: {len(result.get('events', []))}")
            return True
        else:
            print(f"   ❌ Access failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("\n❤️ Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Server is healthy")
            return True
        else:
            print(f"   ❌ Health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    proc = None
    try:
        proc = start_server()
        
        print("\n" + "="*60)
        print("Testing JoinUp API Endpoints")
        print("="*60)
        
        if not test_health():
            print("\n❌ Server not responding. Check if port 8000 is free.")
            exit(1)
        
        # Test registration
        token, user_id = test_register()
        if not token:
            print("\n❌ Registration failed. Stopping tests.")
            exit(1)
        
        # Test login
        login_token = test_login()
        if not login_token:
            print("\n❌ Login failed. Stopping tests.")
            exit(1)
        
        # Test protected route
        if not test_protected_route(token):
            print("\n⚠️ Protected route test failed")
        
        print("\n" + "="*60)
        print("✅ All API tests passed!")
        print("="*60)
        
    finally:
        if proc:
            stop_server(proc)
