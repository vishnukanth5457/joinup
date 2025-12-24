#!/usr/bin/env python3
"""
JoinUp Backend API Testing Suite
Tests all backend functionality including authentication, events, and registrations
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://campuslink-69.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class JoinUpTester:
    def __init__(self):
        self.student_token = None
        self.organizer_token = None
        self.student_user = None
        self.organizer_user = None
        self.created_events = []
        self.registrations = []
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response": response_data
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, token: str = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{BASE_URL}{endpoint}"
        headers = HEADERS.copy()
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}, 0
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return response.status_code < 400, response_data, response.status_code
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0
    
    def test_student_registration(self):
        """Test student user registration"""
        print("🧪 Testing Student Registration...")
        
        student_data = {
            "email": "student-test@test.com",
            "password": "SecurePass123!",
            "name": "Alex Johnson",
            "role": "student",
            "college": "MIT",
            "department": "Computer Science",
            "year": 3
        }
        
        success, response, status_code = self.make_request("POST", "/auth/register", student_data)
        
        if success and "access_token" in response:
            self.student_token = response["access_token"]
            self.student_user = response["user"]
            self.log_test("Student Registration", True, f"Student registered: {response['user']['name']}")
            return True
        else:
            self.log_test("Student Registration", False, f"Status: {status_code}", response)
            return False
    
    def test_organizer_registration(self):
        """Test organizer user registration"""
        print("🧪 Testing Organizer Registration...")
        
        organizer_data = {
            "email": "org-test@test.com",
            "password": "OrgSecure456!",
            "name": "Sarah Chen",
            "role": "organizer",
            "college": "MIT",
            "organization_name": "Tech Events Club"
        }
        
        success, response, status_code = self.make_request("POST", "/auth/register", organizer_data)
        
        if success and "access_token" in response:
            self.organizer_token = response["access_token"]
            self.organizer_user = response["user"]
            self.log_test("Organizer Registration", True, f"Organizer registered: {response['user']['name']}")
            return True
        else:
            self.log_test("Organizer Registration", False, f"Status: {status_code}", response)
            return False
    
    def test_student_login(self):
        """Test student login"""
        print("🧪 Testing Student Login...")
        
        login_data = {
            "email": "student-test@test.com",
            "password": "SecurePass123!"
        }
        
        success, response, status_code = self.make_request("POST", "/auth/login", login_data)
        
        if success and "access_token" in response:
            self.log_test("Student Login", True, f"Login successful for: {response['user']['name']}")
            return True
        else:
            self.log_test("Student Login", False, f"Status: {status_code}", response)
            return False
    
    def test_organizer_login(self):
        """Test organizer login"""
        print("🧪 Testing Organizer Login...")
        
        login_data = {
            "email": "org-test@test.com",
            "password": "OrgSecure456!"
        }
        
        success, response, status_code = self.make_request("POST", "/auth/login", login_data)
        
        if success and "access_token" in response:
            self.log_test("Organizer Login", True, f"Login successful for: {response['user']['name']}")
            return True
        else:
            self.log_test("Organizer Login", False, f"Status: {status_code}", response)
            return False
    
    def test_auth_me_endpoint(self):
        """Test /auth/me endpoint with valid token"""
        print("🧪 Testing Auth Me Endpoint...")
        
        if not self.student_token:
            self.log_test("Auth Me Endpoint", False, "No student token available")
            return False
        
        success, response, status_code = self.make_request("GET", "/auth/me", token=self.student_token)
        
        if success and "id" in response:
            self.log_test("Auth Me Endpoint", True, f"User info retrieved: {response['name']}")
            return True
        else:
            self.log_test("Auth Me Endpoint", False, f"Status: {status_code}", response)
            return False
    
    def test_create_events(self):
        """Test event creation by organizer"""
        print("🧪 Testing Event Creation...")
        
        if not self.organizer_token:
            self.log_test("Event Creation", False, "No organizer token available")
            return False
        
        # Create multiple events
        events_data = [
            {
                "title": "AI & Machine Learning Workshop",
                "description": "Hands-on workshop covering latest AI trends and practical ML implementations",
                "date": (datetime.now() + timedelta(days=7)).isoformat(),
                "venue": "MIT Tech Center, Room 301",
                "fee": 25.0,
                "college": "MIT",
                "category": "Technology",
                "max_participants": 50
            },
            {
                "title": "Startup Pitch Competition",
                "description": "Present your innovative startup ideas to industry experts and investors",
                "date": (datetime.now() + timedelta(days=14)).isoformat(),
                "venue": "MIT Innovation Hub",
                "fee": 15.0,
                "college": "MIT",
                "category": "Business",
                "max_participants": 30
            },
            {
                "title": "Cybersecurity Bootcamp",
                "description": "Intensive 2-day bootcamp on ethical hacking and cybersecurity fundamentals",
                "date": (datetime.now() + timedelta(days=21)).isoformat(),
                "venue": "MIT Security Lab",
                "fee": 50.0,
                "college": "MIT",
                "category": "Security",
                "max_participants": 25
            }
        ]
        
        created_count = 0
        for event_data in events_data:
            success, response, status_code = self.make_request("POST", "/events", event_data, self.organizer_token)
            
            if success and "id" in response:
                self.created_events.append(response)
                created_count += 1
                print(f"   ✅ Created: {response['title']}")
            else:
                print(f"   ❌ Failed to create: {event_data['title']} - Status: {status_code}")
        
        if created_count > 0:
            self.log_test("Event Creation", True, f"Created {created_count}/{len(events_data)} events")
            return True
        else:
            self.log_test("Event Creation", False, "No events created")
            return False
    
    def test_get_organizer_events(self):
        """Test getting organizer's events"""
        print("🧪 Testing Get Organizer Events...")
        
        if not self.organizer_token:
            self.log_test("Get Organizer Events", False, "No organizer token available")
            return False
        
        success, response, status_code = self.make_request("GET", "/events/organizer/my-events", token=self.organizer_token)
        
        if success and isinstance(response, list):
            self.log_test("Get Organizer Events", True, f"Retrieved {len(response)} events")
            return True
        else:
            self.log_test("Get Organizer Events", False, f"Status: {status_code}", response)
            return False
    
    def test_get_all_events_as_student(self):
        """Test getting all events as student"""
        print("🧪 Testing Get All Events (Student)...")
        
        if not self.student_token:
            self.log_test("Get All Events (Student)", False, "No student token available")
            return False
        
        success, response, status_code = self.make_request("GET", "/events", token=self.student_token)
        
        if success and isinstance(response, list):
            self.log_test("Get All Events (Student)", True, f"Retrieved {len(response)} events")
            return True
        else:
            self.log_test("Get All Events (Student)", False, f"Status: {status_code}", response)
            return False
    
    def test_event_registration(self):
        """Test student registering for events"""
        print("🧪 Testing Event Registration...")
        
        if not self.student_token or not self.created_events:
            self.log_test("Event Registration", False, "Missing student token or events")
            return False
        
        registered_count = 0
        for event in self.created_events[:2]:  # Register for first 2 events
            reg_data = {"event_id": event["id"]}
            success, response, status_code = self.make_request("POST", "/registrations", reg_data, self.student_token)
            
            if success and "id" in response:
                self.registrations.append(response)
                registered_count += 1
                print(f"   ✅ Registered for: {event['title']}")
                print(f"   📱 QR Code: {response['qr_code_data']}")
            else:
                print(f"   ❌ Failed to register for: {event['title']} - Status: {status_code}")
        
        if registered_count > 0:
            self.log_test("Event Registration", True, f"Registered for {registered_count} events")
            return True
        else:
            self.log_test("Event Registration", False, "No registrations completed")
            return False
    
    def test_get_student_registrations(self):
        """Test getting student's registrations"""
        print("🧪 Testing Get Student Registrations...")
        
        if not self.student_token:
            self.log_test("Get Student Registrations", False, "No student token available")
            return False
        
        success, response, status_code = self.make_request("GET", "/registrations/my-registrations", token=self.student_token)
        
        if success and isinstance(response, list):
            self.log_test("Get Student Registrations", True, f"Retrieved {len(response)} registrations")
            
            # Verify QR codes are present
            qr_codes_present = all("qr_code_data" in reg for reg in response)
            if qr_codes_present:
                print("   ✅ All registrations have QR codes")
            else:
                print("   ⚠️  Some registrations missing QR codes")
            
            return True
        else:
            self.log_test("Get Student Registrations", False, f"Status: {status_code}", response)
            return False
    
    def test_student_dashboard(self):
        """Test student dashboard stats"""
        print("🧪 Testing Student Dashboard...")
        
        if not self.student_token:
            self.log_test("Student Dashboard", False, "No student token available")
            return False
        
        success, response, status_code = self.make_request("GET", "/dashboard/student", token=self.student_token)
        
        if success and "total_events_registered" in response:
            self.log_test("Student Dashboard", True, 
                         f"Stats - Registered: {response['total_events_registered']}, "
                         f"Attended: {response['attended_events']}, "
                         f"Certificates: {response['certificates_earned']}")
            return True
        else:
            self.log_test("Student Dashboard", False, f"Status: {status_code}", response)
            return False
    
    def test_duplicate_registration(self):
        """Test duplicate registration (should fail)"""
        print("🧪 Testing Duplicate Registration...")
        
        if not self.student_token or not self.created_events:
            self.log_test("Duplicate Registration", False, "Missing student token or events")
            return False
        
        # Try to register for the same event again
        event = self.created_events[0]
        reg_data = {"event_id": event["id"]}
        success, response, status_code = self.make_request("POST", "/registrations", reg_data, self.student_token)
        
        if not success and status_code == 400:
            self.log_test("Duplicate Registration", True, "Correctly rejected duplicate registration")
            return True
        else:
            self.log_test("Duplicate Registration", False, f"Should have failed but got status: {status_code}", response)
            return False
    
    def test_invalid_login(self):
        """Test login with invalid credentials (should fail)"""
        print("🧪 Testing Invalid Login...")
        
        login_data = {
            "email": "student-test@test.com",
            "password": "WrongPassword123!"
        }
        
        success, response, status_code = self.make_request("POST", "/auth/login", login_data)
        
        if not success and status_code == 401:
            self.log_test("Invalid Login", True, "Correctly rejected invalid credentials")
            return True
        else:
            self.log_test("Invalid Login", False, f"Should have failed but got status: {status_code}", response)
            return False
    
    def test_unauthorized_access(self):
        """Test unauthorized access (should fail)"""
        print("🧪 Testing Unauthorized Access...")
        
        # Try to access protected endpoint without token
        success, response, status_code = self.make_request("GET", "/auth/me")
        
        if not success and status_code in [401, 403]:
            self.log_test("Unauthorized Access", True, "Correctly rejected unauthorized access")
            return True
        else:
            self.log_test("Unauthorized Access", False, f"Should have failed but got status: {status_code}", response)
            return False
    
    def test_student_accessing_organizer_endpoint(self):
        """Test student trying to access organizer-only endpoint"""
        print("🧪 Testing Role-based Access Control...")
        
        if not self.student_token:
            self.log_test("Role-based Access Control", False, "No student token available")
            return False
        
        # Try to create event as student (should fail)
        event_data = {
            "title": "Unauthorized Event",
            "description": "This should not be created",
            "date": (datetime.now() + timedelta(days=1)).isoformat(),
            "venue": "Nowhere",
            "fee": 0.0,
            "college": "MIT"
        }
        
        success, response, status_code = self.make_request("POST", "/events", event_data, self.student_token)
        
        if not success and status_code == 403:
            self.log_test("Role-based Access Control", True, "Correctly enforced role restrictions")
            return True
        else:
            self.log_test("Role-based Access Control", False, f"Should have failed but got status: {status_code}", response)
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting JoinUp Backend API Tests")
        print("=" * 50)
        
        # Authentication Flow Tests
        print("\n📋 AUTHENTICATION TESTS")
        print("-" * 30)
        self.test_student_registration()
        self.test_organizer_registration()
        self.test_student_login()
        self.test_organizer_login()
        self.test_auth_me_endpoint()
        
        # Event Management Tests
        print("\n📋 EVENT MANAGEMENT TESTS")
        print("-" * 30)
        self.test_create_events()
        self.test_get_organizer_events()
        
        # Student Features Tests
        print("\n📋 STUDENT FEATURES TESTS")
        print("-" * 30)
        self.test_get_all_events_as_student()
        self.test_event_registration()
        self.test_get_student_registrations()
        self.test_student_dashboard()
        
        # Error Handling Tests
        print("\n📋 ERROR HANDLING TESTS")
        print("-" * 30)
        self.test_duplicate_registration()
        self.test_invalid_login()
        self.test_unauthorized_access()
        self.test_student_accessing_organizer_endpoint()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n" + "=" * 50)
        return passed_tests, failed_tests

def main():
    """Main test execution"""
    print("JoinUp Backend API Test Suite")
    print(f"Testing against: {BASE_URL}")
    print()
    
    tester = JoinUpTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()