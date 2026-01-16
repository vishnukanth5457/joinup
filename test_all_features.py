#!/usr/bin/env python3
"""
Complete End-to-End Test of JoinUp Platform
Tests: Auth, Events, Registrations, QR Codes, Certificates
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
STUDENT_EMAIL = "student@test.com"
STUDENT_PASSWORD = "password123"
ORGANIZER_EMAIL = "organizer@test.com"
ORGANIZER_PASSWORD = "password123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.END}\n")

def test_passed(test_name, details=""):
    print(f"{Colors.GREEN}✅ PASSED{Colors.END}: {test_name}")
    if details:
        print(f"   {details}")

def test_failed(test_name, error=""):
    print(f"{Colors.RED}❌ FAILED{Colors.END}: {test_name}")
    if error:
        print(f"   Error: {error}")

def test_api(method, endpoint, data=None, token=None, expected_status=None):
    """Helper to make API calls"""
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=5)
        else:
            return None, None
        
        if expected_status and response.status_code != expected_status:
            return response, False
        
        return response, response.status_code < 400
    except Exception as e:
        print(f"   Request error: {e}")
        return None, False

def test_auth_system():
    """Test Authentication System"""
    print_header("TEST 1: AUTHENTICATION SYSTEM")
    
    # Test 1.1: Register Student
    student_data = {
        "email": STUDENT_EMAIL,
        "password": STUDENT_PASSWORD,
        "name": "Test Student",
        "college": "Tech College",
        "role": "student",
        "department": "CSE",
        "year": 2
    }
    
    response, success = test_api("POST", "/auth/register", student_data, expected_status=200)
    if success and response:
        try:
            result = response.json()
            student_token = result.get("access_token")
            print_header("Student Registration")
            test_passed("Student Registration", f"Token: {student_token[:20]}...")
        except:
            test_failed("Student Registration", "Invalid response format")
            student_token = None
    else:
        test_failed("Student Registration", f"Status: {response.status_code if response else 'No response'}")
        student_token = None
    
    # Test 1.2: Register Organizer
    organizer_data = {
        "email": ORGANIZER_EMAIL,
        "password": ORGANIZER_PASSWORD,
        "name": "Test Organizer",
        "college": "Event Organizers",
        "role": "organizer",
        "organization_name": "Tech Events"
    }
    
    response, success = test_api("POST", "/auth/register", organizer_data, expected_status=200)
    if success and response:
        try:
            result = response.json()
            organizer_token = result.get("access_token")
            print(Colors.YELLOW + "\nOrganizer Registration" + Colors.END)
            test_passed("Organizer Registration", f"Token: {organizer_token[:20]}...")
        except:
            test_failed("Organizer Registration", "Invalid response format")
            organizer_token = None
    else:
        test_failed("Organizer Registration", f"Status: {response.status_code if response else 'No response'}")
        organizer_token = None
    
    # Test 1.3: Login
    login_data = {
        "email": STUDENT_EMAIL,
        "password": STUDENT_PASSWORD
    }
    
    response, success = test_api("POST", "/auth/login", login_data, expected_status=200)
    if success and response:
        test_passed("Student Login", "Successfully authenticated")
    else:
        test_failed("Student Login", f"Status: {response.status_code if response else 'No response'}")
    
    return student_token, organizer_token

def test_events_system(organizer_token):
    """Test Events System"""
    print_header("TEST 2: EVENTS SYSTEM")
    
    if not organizer_token:
        test_failed("Events System", "No organizer token")
        return None
    
    # Test 2.1: Create Event
    event_data = {
        "title": "Tech Conference 2025",
        "description": "Annual technology conference",
        "date": (datetime.now() + timedelta(days=7)).isoformat(),
        "venue": "Main Auditorium",
        "fee": 500,
        "college": "Tech College",
        "category": "Tech",
        "max_participants": 100
    }
    
    response, success = test_api("POST", "/events", event_data, organizer_token, expected_status=200)
    if success and response:
        try:
            result = response.json()
            event_id = result.get("id")
            test_passed("Create Event", f"Event ID: {event_id}")
            return event_id
        except:
            test_failed("Create Event", "Invalid response format")
            return None
    else:
        test_failed("Create Event", f"Status: {response.status_code if response else 'No response'}")
        return None

def test_registrations(student_token, event_id):
    """Test Registrations"""
    print_header("TEST 3: REGISTRATIONS")
    
    if not student_token or not event_id:
        test_failed("Registrations", "Missing token or event ID")
        return None, None
    
    # Test 3.1: Register for Event
    registration_data = {
        "event_id": event_id
    }
    
    response, success = test_api("POST", "/registrations", registration_data, student_token, expected_status=200)
    if success and response:
        try:
            result = response.json()
            registration_id = result.get("id")
            qr_code = result.get("qr_code")
            test_passed("Event Registration", f"Registration ID: {registration_id}")
            return registration_id, qr_code
        except Exception as e:
            test_failed("Event Registration", f"Response error: {e}")
            return None, None
    else:
        test_failed("Event Registration", f"Status: {response.status_code if response else 'No response'}")
        return None, None
    
    # Test 3.2: Get My Registrations
    response, success = test_api("GET", "/registrations/my-registrations", token=student_token)
    if success and response:
        test_passed("Get My Registrations", "Successfully retrieved")
    else:
        test_failed("Get My Registrations", f"Status: {response.status_code if response else 'No response'}")

def test_qr_system(organizer_token, registration_id):
    """Test QR Code System"""
    print_header("TEST 4: QR CODE SYSTEM")
    
    if not organizer_token or not registration_id:
        test_failed("QR Code System", "Missing token or registration ID")
        return
    
    # Test 4.1: Mark Attendance
    attendance_data = {
        "registration_id": registration_id
    }
    
    response, success = test_api("POST", "/mark-attendance", attendance_data, organizer_token)
    if success and response:
        test_passed("Mark Attendance", "Successfully marked")
    else:
        test_failed("Mark Attendance", f"Status: {response.status_code if response else 'No response'}")

def test_dashboard(student_token, organizer_token):
    """Test Dashboard Endpoints"""
    print_header("TEST 5: DASHBOARD")
    
    # Test 5.1: Student Dashboard
    if student_token:
        response, success = test_api("GET", "/dashboard/student", token=student_token)
        if success and response:
            test_passed("Student Dashboard", "Successfully retrieved")
        else:
            test_failed("Student Dashboard", f"Status: {response.status_code if response else 'No response'}")
    
    # Test 5.2: Organizer Dashboard
    if organizer_token:
        response, success = test_api("GET", "/dashboard/organizer", token=organizer_token)
        if success and response:
            test_passed("Organizer Dashboard", "Successfully retrieved")
        else:
            test_failed("Organizer Dashboard", f"Status: {response.status_code if response else 'No response'}")

def test_error_handling():
    """Test Error Handling"""
    print_header("TEST 6: ERROR HANDLING")
    
    # Test 6.1: Invalid credentials
    response, success = test_api("POST", "/auth/login", 
                                {"email": "notexist@test.com", "password": "wrong"})
    if not success and response and response.status_code == 401:
        test_passed("Invalid Credentials", "Returns 401")
    else:
        test_failed("Invalid Credentials", f"Expected 401, got {response.status_code if response else 'No response'}")
    
    # Test 6.2: Missing required fields
    response, success = test_api("POST", "/auth/register", {"email": "test@test.com"})
    if not success and response and response.status_code == 400:
        test_passed("Missing Required Fields", "Returns 400")
    else:
        test_failed("Missing Required Fields", f"Expected 400, got {response.status_code if response else 'No response'}")

def main():
    """Run all tests"""
    print(f"\n{Colors.YELLOW}╔{'═'*68}╗")
    print(f"║ {Colors.BLUE}JoinUp Platform - Complete End-to-End Test Suite{Colors.YELLOW}              ║")
    print(f"║ {Colors.BLUE}Testing: Auth, Events, Registrations, QR Codes{Colors.YELLOW}                 ║")
    print(f"╚{'═'*68}╝{Colors.END}\n")
    
    try:
        # Check if backend is running
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        print(f"{Colors.GREEN}✓ Backend is running on {BASE_URL}{Colors.END}\n")
    except:
        print(f"{Colors.RED}✗ Backend is not running on {BASE_URL}{Colors.END}")
        print("  Please start the backend with: cd backend && python server.py")
        return
    
    # Run all test suites
    student_token, organizer_token = test_auth_system()
    event_id = test_events_system(organizer_token)
    registration_id, qr_code = test_registrations(student_token, event_id)
    test_qr_system(organizer_token, registration_id)
    test_dashboard(student_token, organizer_token)
    test_error_handling()
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"{Colors.YELLOW}All tests completed!{Colors.END}")
    print(f"\nBackend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print(f"\nStudent Token Available: {'Yes' if student_token else 'No'}")
    print(f"Organizer Token Available: {'Yes' if organizer_token else 'No'}")

if __name__ == "__main__":
    main()
