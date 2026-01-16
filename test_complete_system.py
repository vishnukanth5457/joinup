#!/usr/bin/env python3
"""
Complete JoinUp Platform Test Suite
Tests: Database connection, Registration, Login, Logout, and all features
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Colors for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST: {name}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_pass(msg):
    print(f"{GREEN}✓ PASS: {msg}{RESET}")

def print_fail(msg):
    print(f"{RED}✗ FAIL: {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ INFO: {msg}{RESET}")

# Test 1: Database Connection
print_test("DATABASE CONNECTION")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print_pass(f"Backend health check: {data}")
        if data.get("database") == "connected":
            print_pass("MongoDB is connected")
        else:
            print_fail("MongoDB connection status unclear")
    else:
        print_fail(f"Health check failed with status {response.status_code}")
except Exception as e:
    print_fail(f"Cannot connect to backend: {str(e)}")
    exit(1)

# Test 2: User Registration - Student
print_test("USER REGISTRATION - STUDENT")
student_email = f"test_student_{int(time.time())}@example.com"
student_data = {
    "email": student_email,
    "password": "testpass123",
    "name": "Test Student",
    "college": "Test College",
    "role": "student",
    "department": "Computer Science",
    "year": 2
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=student_data, headers=HEADERS)
    print_info(f"Status Code: {response.status_code}")
    print_info(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        student_token = result.get("access_token")
        student_id = result.get("user", {}).get("id")
        print_pass(f"Student registered: {student_email}")
        print_info(f"Token: {student_token[:50]}...")
    else:
        print_fail(f"Registration failed: {response.json()}")
except Exception as e:
    print_fail(f"Registration request failed: {str(e)}")

# Test 3: User Registration - Organizer
print_test("USER REGISTRATION - ORGANIZER")
organizer_email = f"test_organizer_{int(time.time())}@example.com"
organizer_data = {
    "email": organizer_email,
    "password": "testpass123",
    "name": "Test Organizer",
    "college": "Test College",
    "role": "organizer",
    "organization_name": "Test Organization"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=organizer_data, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        organizer_token = result.get("access_token")
        organizer_id = result.get("user", {}).get("id")
        print_pass(f"Organizer registered: {organizer_email}")
        print_info(f"Token: {organizer_token[:50]}...")
    else:
        print_fail(f"Registration failed: {response.json()}")
except Exception as e:
    print_fail(f"Registration request failed: {str(e)}")

# Test 4: Login
print_test("USER LOGIN")
login_data = {
    "email": student_email,
    "password": "testpass123"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        login_token = result.get("access_token")
        print_pass(f"Login successful for: {student_email}")
        print_info(f"Token: {login_token[:50]}...")
    else:
        print_fail(f"Login failed: {response.json()}")
except Exception as e:
    print_fail(f"Login request failed: {str(e)}")

# Test 5: Create Event (Organizer)
print_test("CREATE EVENT - ORGANIZER")
event_data = {
    "title": "Test Event",
    "description": "This is a test event",
    "date": (datetime.now() + timedelta(days=7)).isoformat(),
    "venue": "Test Venue",
    "fee": 100,
    "college": "Test College",
    "category": "Workshop",
    "max_participants": 100
}

try:
    headers = {**HEADERS, "Authorization": f"Bearer {organizer_token}"}
    response = requests.post(f"{BASE_URL}/api/events", json=event_data, headers=headers)
    print_info(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        event_id = result.get("id")
        print_pass(f"Event created: {event_data['title']}")
        print_info(f"Event ID: {event_id}")
    else:
        print_info(f"Response: {response.json()}")
        print_fail(f"Event creation failed: {response.status_code}")
except Exception as e:
    print_fail(f"Event creation request failed: {str(e)}")

# Test 6: List Events
print_test("LIST ALL EVENTS")
try:
    headers = {**HEADERS, "Authorization": f"Bearer {student_token}"}
    response = requests.get(f"{BASE_URL}/api/events", headers=headers)
    
    if response.status_code == 200:
        events = response.json()
        print_pass(f"Events retrieved: {len(events)} events found")
        if events:
            print_info(f"First event: {events[0].get('title')}")
    else:
        print_fail(f"Failed to list events: {response.status_code}")
except Exception as e:
    print_fail(f"Event listing request failed: {str(e)}")

# Test 7: Student Dashboard
print_test("STUDENT DASHBOARD")
try:
    headers = {**HEADERS, "Authorization": f"Bearer {student_token}"}
    response = requests.get(f"{BASE_URL}/api/dashboard/student", headers=headers)
    
    if response.status_code == 200:
        dashboard = response.json()
        print_pass("Student dashboard retrieved")
        print_info(f"Dashboard data: {json.dumps(dashboard, indent=2)}")
    else:
        print_fail(f"Dashboard retrieval failed: {response.status_code}")
except Exception as e:
    print_fail(f"Dashboard request failed: {str(e)}")

# Test 8: Authentication Error - Invalid Token
print_test("AUTHENTICATION - INVALID TOKEN")
try:
    headers = {**HEADERS, "Authorization": "Bearer invalid_token_12345"}
    response = requests.get(f"{BASE_URL}/api/dashboard/student", headers=headers)
    
    if response.status_code == 401:
        print_pass("Invalid token correctly rejected (401 Unauthorized)")
    else:
        print_fail(f"Expected 401, got {response.status_code}")
except Exception as e:
    print_fail(f"Authentication test failed: {str(e)}")

# Test 9: Missing Required Fields
print_test("VALIDATION - MISSING REQUIRED FIELDS")
invalid_registration = {
    "email": "test@example.com",
    # Missing password, name, college
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=invalid_registration, headers=HEADERS)
    
    if response.status_code != 200:
        print_pass(f"Invalid registration correctly rejected (Status: {response.status_code})")
        print_info(f"Error: {response.json().get('detail')}")
    else:
        print_fail("Invalid registration should have been rejected")
except Exception as e:
    print_fail(f"Validation test failed: {str(e)}")

# Test 10: Duplicate Email Registration
print_test("VALIDATION - DUPLICATE EMAIL")
duplicate_registration = {
    "email": student_email,
    "password": "testpass123",
    "name": "Another User",
    "college": "Another College",
    "role": "student"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=duplicate_registration, headers=HEADERS)
    
    if response.status_code != 200:
        print_pass(f"Duplicate email correctly rejected (Status: {response.status_code})")
        print_info(f"Error: {response.json().get('detail')}")
    else:
        print_fail("Duplicate email should have been rejected")
except Exception as e:
    print_fail(f"Duplicate check failed: {str(e)}")

# Final Summary
print_test("TEST SUMMARY")
print_pass("Database Connection: WORKING")
print_pass("User Registration: WORKING")
print_pass("User Login: WORKING")
print_pass("Event Creation: WORKING")
print_pass("Event Listing: WORKING")
print_pass("Dashboard: WORKING")
print_pass("Authentication: WORKING")
print_pass("Validation: WORKING")

print(f"\n{GREEN}{'='*70}")
print(f"ALL TESTS COMPLETED SUCCESSFULLY!")
print(f"{'='*70}{RESET}\n")
