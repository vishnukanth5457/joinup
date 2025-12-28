#!/usr/bin/env python3
"""
Comprehensive JoinUp Backend Testing
Tests all features mentioned in the review request including advanced scenarios
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class ComprehensiveJoinUpTester:
    def __init__(self, base_url: str = "https://campuslink-69.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.student_token = None
        self.organizer_token = None
        self.test_results = []
        self.created_event_id = None
        self.registration_id = None
        self.qr_code_data = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": f"{response_time:.3f}s" if response_time > 0 else "N/A"
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, token: str = None, params: Dict = None) -> tuple:
        """Make HTTP request and return response, success status, and response time"""
        url = f"{self.api_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            return response, True, response_time
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            print(f"Request failed: {e}")
            return None, False, response_time

    def test_login_with_provided_credentials(self):
        """Test login with the specific credentials provided in the review request"""
        print("\n🔐 TESTING PROVIDED CREDENTIALS")
        
        # Test student login
        student_login = {
            "email": "john.smith0@student.com",
            "password": "student123"
        }
        
        response, success, response_time = self.make_request("POST", "/auth/login", student_login)
        
        if success and response and response.status_code == 200:
            data = response.json()
            self.student_token = data["access_token"]
            self.log_test("Student Login (john.smith0@student.com)", True, f"Login successful. User: {data['user']['name']}", response_time)
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
            self.log_test("Student Login (john.smith0@student.com)", False, f"Status: {response.status_code if response else 'No response'}, Error: {error_msg}", response_time)
            return False
            
        # Test organizer login
        organizer_login = {
            "email": "organizer1@mit.com",
            "password": "organizer123"
        }
        
        response, success, response_time = self.make_request("POST", "/auth/login", organizer_login)
        
        if success and response and response.status_code == 200:
            data = response.json()
            self.organizer_token = data["access_token"]
            self.log_test("Organizer Login (organizer1@mit.com)", True, f"Login successful. User: {data['user']['name']}", response_time)
            return True
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
            self.log_test("Organizer Login (organizer1@mit.com)", False, f"Status: {response.status_code if response else 'No response'}, Error: {error_msg}", response_time)
            return False

    def test_auth_me_endpoint(self):
        """Test /auth/me endpoint with token"""
        if not self.student_token:
            self.log_test("Auth Me Endpoint", False, "No student token available")
            return False
            
        response, success, response_time = self.make_request("GET", "/auth/me", token=self.student_token)
        
        if success and response and response.status_code == 200:
            data = response.json()
            if "email" in data and "name" in data and "role" in data:
                self.log_test("Auth Me Endpoint", True, f"User info retrieved: {data['name']} ({data['role']})", response_time)
                return True
            else:
                self.log_test("Auth Me Endpoint", False, f"Invalid user data format: {data}", response_time)
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
            self.log_test("Auth Me Endpoint", False, f"Status: {response.status_code if response else 'No response'}, Error: {error_msg}", response_time)
        return False

    def test_event_management_comprehensive(self):
        """Test comprehensive event management features"""
        print("\n🎯 TESTING EVENT MANAGEMENT")
        
        # Test get all events as student
        response, success, response_time = self.make_request("GET", "/events", token=self.student_token)
        if success and response and response.status_code == 200:
            events = response.json()
            self.log_test("Get All Events (Student)", True, f"Retrieved {len(events)} events", response_time)
        else:
            self.log_test("Get All Events (Student)", False, f"Failed to get events", response_time)
            
        # Test search events with query
        search_params = {"search": "AI"}
        response, success, response_time = self.make_request("GET", "/events", params=search_params, token=self.student_token)
        if success and response and response.status_code == 200:
            events = response.json()
            self.log_test("Search Events (AI)", True, f"Found {len(events)} events matching 'AI'", response_time)
        else:
            self.log_test("Search Events (AI)", False, f"Search failed", response_time)
            
        # Test filter events by college
        filter_params = {"college": "MIT"}
        response, success, response_time = self.make_request("GET", "/events", params=filter_params, token=self.student_token)
        if success and response and response.status_code == 200:
            events = response.json()
            self.log_test("Filter Events by College (MIT)", True, f"Found {len(events)} events at MIT", response_time)
            # Store first event for later tests
            if events:
                self.created_event_id = events[0]["id"]
        else:
            self.log_test("Filter Events by College (MIT)", False, f"Filter failed", response_time)
            
        # Test get specific event details
        if self.created_event_id:
            response, success, response_time = self.make_request("GET", f"/events/{self.created_event_id}", token=self.student_token)
            if success and response and response.status_code == 200:
                event = response.json()
                self.log_test("Get Specific Event Details", True, f"Retrieved event: {event['title']}", response_time)
            else:
                self.log_test("Get Specific Event Details", False, f"Failed to get event details", response_time)
        
        # Test get organizer's events
        response, success, response_time = self.make_request("GET", "/events/organizer/my-events", token=self.organizer_token)
        if success and response and response.status_code == 200:
            events = response.json()
            self.log_test("Get Organizer Events", True, f"Organizer has {len(events)} events", response_time)
        else:
            self.log_test("Get Organizer Events", False, f"Failed to get organizer events", response_time)

    def test_student_registration_flow(self):
        """Test complete student registration flow"""
        print("\n👨‍🎓 TESTING STUDENT REGISTRATION FLOW")
        
        if not self.created_event_id:
            self.log_test("Student Registration Flow", False, "No event ID available for registration")
            return False
            
        # Test register for event
        reg_data = {"event_id": self.created_event_id}
        response, success, response_time = self.make_request("POST", "/registrations", reg_data, self.student_token)
        
        if success and response and response.status_code == 200:
            registration = response.json()
            self.registration_id = registration["id"]
            self.qr_code_data = registration["qr_code_data"]
            self.log_test("Register for Event", True, f"Registration successful. QR: {registration['qr_code_data']}", response_time)
        elif success and response and response.status_code == 400 and "already registered" in response.json().get("detail", ""):
            self.log_test("Register for Event", True, "Already registered (expected for existing user)", response_time)
            # Get existing registration
            response, success, response_time = self.make_request("GET", "/registrations/my-registrations", token=self.student_token)
            if success and response and response.status_code == 200:
                registrations = response.json()
                for reg in registrations:
                    if reg["event_id"] == self.created_event_id:
                        self.registration_id = reg["id"]
                        self.qr_code_data = reg["qr_code_data"]
                        break
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
            self.log_test("Register for Event", False, f"Registration failed: {error_msg}", response_time)
            return False
            
        # Test get student's registrations
        response, success, response_time = self.make_request("GET", "/registrations/my-registrations", token=self.student_token)
        if success and response and response.status_code == 200:
            registrations = response.json()
            qr_codes_present = all("qr_code_data" in reg for reg in registrations)
            self.log_test("Get Student Registrations", True, f"Retrieved {len(registrations)} registrations. QR codes: {'✅' if qr_codes_present else '❌'}", response_time)
        else:
            self.log_test("Get Student Registrations", False, f"Failed to get registrations", response_time)
            
        # Test student dashboard stats
        response, success, response_time = self.make_request("GET", "/dashboard/student", token=self.student_token)
        if success and response and response.status_code == 200:
            stats = response.json()
            required_fields = ["total_events_registered", "attended_events", "certificates_earned", "upcoming_events"]
            if all(field in stats for field in required_fields):
                self.log_test("Student Dashboard Stats", True, f"Stats: {stats['total_events_registered']} registered, {stats['attended_events']} attended, {stats['certificates_earned']} certificates", response_time)
            else:
                self.log_test("Student Dashboard Stats", False, f"Missing required fields in dashboard", response_time)
        else:
            self.log_test("Student Dashboard Stats", False, f"Failed to get dashboard stats", response_time)
            
        # Test duplicate registration (should fail)
        reg_data = {"event_id": self.created_event_id}
        response, success, response_time = self.make_request("POST", "/registrations", reg_data, self.student_token)
        if success and response and response.status_code == 400:
            error_msg = response.json().get("detail", "")
            if "already registered" in error_msg.lower():
                self.log_test("Duplicate Registration Prevention", True, "Correctly rejected duplicate registration", response_time)
            else:
                self.log_test("Duplicate Registration Prevention", False, f"Wrong error message: {error_msg}", response_time)
        else:
            self.log_test("Duplicate Registration Prevention", False, f"Expected 400, got {response.status_code if response else 'No response'}", response_time)

    def test_organizer_features(self):
        """Test organizer-specific features"""
        print("\n👨‍💼 TESTING ORGANIZER FEATURES")
        
        # Test create new event
        event_data = {
            "title": "Advanced Python Programming",
            "description": "Deep dive into advanced Python concepts and best practices",
            "date": (datetime.utcnow() + timedelta(days=45)).isoformat(),
            "venue": "MIT Computer Lab",
            "fee": 75.0,
            "college": "MIT",
            "category": "Programming",
            "max_participants": 50
        }
        
        response, success, response_time = self.make_request("POST", "/events", event_data, self.organizer_token)
        if success and response and response.status_code == 200:
            event = response.json()
            new_event_id = event["id"]
            self.log_test("Create New Event (Organizer)", True, f"Created event: {event['title']} (ID: {event['id']})", response_time)
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
            self.log_test("Create New Event (Organizer)", False, f"Event creation failed: {error_msg}", response_time)
            new_event_id = None
            
        # Test get event registrations
        if self.created_event_id:
            response, success, response_time = self.make_request("GET", f"/registrations/event/{self.created_event_id}", token=self.organizer_token)
            if success and response and response.status_code == 200:
                registrations = response.json()
                self.log_test("Get Event Registrations", True, f"Event has {len(registrations)} registrations", response_time)
            else:
                self.log_test("Get Event Registrations", False, f"Failed to get event registrations", response_time)
                
        # Test mark attendance via QR code
        if self.qr_code_data:
            attendance_data = {"qr_code_data": self.qr_code_data}
            response, success, response_time = self.make_request("POST", "/attendance/mark", attendance_data, self.organizer_token)
            if success and response and response.status_code == 200:
                result = response.json()
                self.log_test("Mark Attendance via QR", True, f"Attendance marked for: {result.get('student_name', 'student')}", response_time)
            elif success and response and response.status_code == 400 and "already marked" in response.json().get("detail", ""):
                self.log_test("Mark Attendance via QR", True, "Attendance already marked (expected)", response_time)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
                self.log_test("Mark Attendance via QR", False, f"Attendance marking failed: {error_msg}", response_time)
                
        # Test issue certificate
        if self.registration_id:
            cert_data = {"registration_id": self.registration_id}
            response, success, response_time = self.make_request("POST", "/certificates/issue", cert_data, self.organizer_token)
            if success and response and response.status_code == 200:
                certificate = response.json()
                self.log_test("Issue Certificate", True, f"Certificate issued for: {certificate['student_name']}", response_time)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
                self.log_test("Issue Certificate", False, f"Certificate issuance failed: {error_msg}", response_time)
                
        # Test organizer analytics
        response, success, response_time = self.make_request("GET", "/dashboard/organizer", token=self.organizer_token)
        if success and response and response.status_code == 200:
            analytics = response.json()
            required_fields = ["total_events", "total_registrations", "total_attendees", "upcoming_events", "past_events", "average_rating", "top_events"]
            if all(field in analytics for field in required_fields):
                self.log_test("Organizer Analytics", True, f"Analytics: {analytics['total_events']} events, {analytics['total_registrations']} registrations, {analytics['total_attendees']} attendees", response_time)
            else:
                self.log_test("Organizer Analytics", False, f"Missing required fields in analytics", response_time)
        else:
            self.log_test("Organizer Analytics", False, f"Failed to get organizer analytics", response_time)

    def test_rating_system(self):
        """Test rating and feedback system"""
        print("\n⭐ TESTING RATING SYSTEM")
        
        if not self.created_event_id:
            self.log_test("Rating System", False, "No event ID available for rating")
            return
            
        # Test rate an attended event
        rating_data = {
            "event_id": self.created_event_id,
            "rating": 5,
            "feedback": "Excellent event! Very informative and well-organized."
        }
        
        response, success, response_time = self.make_request("POST", "/ratings", rating_data, self.student_token)
        if success and response and response.status_code == 200:
            rating = response.json()
            self.log_test("Rate Attended Event", True, f"Event rated: {rating['rating']}/5 stars", response_time)
        elif success and response and response.status_code == 400:
            error_msg = response.json().get("detail", "")
            if "already rated" in error_msg.lower():
                self.log_test("Rate Attended Event", True, "Already rated this event (expected)", response_time)
            elif "can only rate events you attended" in error_msg.lower():
                self.log_test("Rate Attended Event", True, "Correctly enforced attendance requirement", response_time)
            else:
                self.log_test("Rate Attended Event", False, f"Unexpected error: {error_msg}", response_time)
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
            self.log_test("Rate Attended Event", False, f"Rating failed: {error_msg}", response_time)
            
        # Test get event ratings
        response, success, response_time = self.make_request("GET", f"/ratings/event/{self.created_event_id}", token=self.student_token)
        if success and response and response.status_code == 200:
            ratings = response.json()
            self.log_test("Get Event Ratings", True, f"Event has {len(ratings)} ratings", response_time)
        else:
            self.log_test("Get Event Ratings", False, f"Failed to get event ratings", response_time)
            
        # Test duplicate rating (should fail)
        rating_data = {
            "event_id": self.created_event_id,
            "rating": 4,
            "feedback": "Trying to rate again"
        }
        
        response, success, response_time = self.make_request("POST", "/ratings", rating_data, self.student_token)
        if success and response and response.status_code == 400:
            error_msg = response.json().get("detail", "")
            if "already rated" in error_msg.lower():
                self.log_test("Duplicate Rating Prevention", True, "Correctly rejected duplicate rating", response_time)
            else:
                self.log_test("Duplicate Rating Prevention", False, f"Wrong error message: {error_msg}", response_time)
        else:
            self.log_test("Duplicate Rating Prevention", False, f"Expected 400, got {response.status_code if response else 'No response'}", response_time)

    def test_ai_recommendations(self):
        """Test AI recommendation system"""
        print("\n🤖 TESTING AI RECOMMENDATIONS")
        
        response, success, response_time = self.make_request("GET", "/recommendations", token=self.student_token)
        if success and response and response.status_code == 200:
            recommendations = response.json()
            if isinstance(recommendations, list):
                # Check that recommendations exclude registered events
                registered_event_ids = set()
                reg_response, reg_success, _ = self.make_request("GET", "/registrations/my-registrations", token=self.student_token)
                if reg_success and reg_response and reg_response.status_code == 200:
                    registrations = reg_response.json()
                    registered_event_ids = {reg["event_id"] for reg in registrations}
                
                recommended_event_ids = {rec["id"] for rec in recommendations}
                overlap = registered_event_ids.intersection(recommended_event_ids)
                
                if not overlap:
                    self.log_test("AI Recommendations", True, f"Received {len(recommendations)} personalized recommendations (excludes registered events)", response_time)
                else:
                    self.log_test("AI Recommendations", False, f"Recommendations include {len(overlap)} already registered events", response_time)
            else:
                self.log_test("AI Recommendations", False, f"Expected list, got: {type(recommendations)}", response_time)
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Request failed"
            self.log_test("AI Recommendations", False, f"Recommendations failed: {error_msg}", response_time)

    def test_error_handling(self):
        """Test comprehensive error handling"""
        print("\n🛡️ TESTING ERROR HANDLING")
        
        # Test 401 unauthorized access
        response, success, response_time = self.make_request("GET", "/auth/me")  # No token
        if success and response and response.status_code == 401:
            self.log_test("401 Unauthorized Access", True, "Correctly rejected unauthorized access", response_time)
        else:
            self.log_test("401 Unauthorized Access", False, f"Expected 401, got {response.status_code if response else 'No response'}", response_time)
            
        # Test 404 for non-existent resources
        fake_event_id = "non-existent-event-id-12345"
        response, success, response_time = self.make_request("GET", f"/events/{fake_event_id}", token=self.student_token)
        if success and response and response.status_code == 404:
            self.log_test("404 Non-existent Resource", True, "Correctly returned 404 for non-existent event", response_time)
        else:
            self.log_test("404 Non-existent Resource", False, f"Expected 404, got {response.status_code if response else 'No response'}", response_time)
            
        # Test validation errors
        invalid_event_data = {
            "title": "",  # Empty title should fail validation
            "description": "Test event",
            "date": "invalid-date-format",
            "venue": "Test Venue",
            "fee": -10,  # Negative fee should fail
            "college": "MIT"
        }
        
        response, success, response_time = self.make_request("POST", "/events", invalid_event_data, self.organizer_token)
        if success and response and response.status_code in [400, 422]:  # 422 for validation errors
            self.log_test("Validation Error Handling", True, "Correctly rejected invalid event data", response_time)
        else:
            self.log_test("Validation Error Handling", False, f"Expected 400/422, got {response.status_code if response else 'No response'}", response_time)

    def test_response_times(self):
        """Test response times for performance"""
        print("\n⏱️ TESTING RESPONSE TIMES")
        
        # Test multiple endpoints for response time
        endpoints_to_test = [
            ("GET", "/events", "Get Events"),
            ("GET", "/auth/me", "Auth Me"),
            ("GET", "/dashboard/student", "Student Dashboard"),
            ("GET", "/recommendations", "AI Recommendations")
        ]
        
        slow_endpoints = []
        
        for method, endpoint, name in endpoints_to_test:
            token = self.student_token if endpoint != "/dashboard/organizer" else self.organizer_token
            response, success, response_time = self.make_request(method, endpoint, token=token)
            
            if success and response and response.status_code == 200:
                if response_time > 2.0:  # Consider > 2s as slow
                    slow_endpoints.append(f"{name}: {response_time:.3f}s")
                    
        if not slow_endpoints:
            self.log_test("Response Time Performance", True, "All endpoints respond within 2 seconds")
        else:
            self.log_test("Response Time Performance", False, f"Slow endpoints: {', '.join(slow_endpoints)}")

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting JoinUp Backend Comprehensive Testing")
        print("=" * 70)
        
        # Login with provided credentials
        if not self.test_login_with_provided_credentials():
            print("❌ Failed to login with provided credentials. Stopping tests.")
            return
            
        # Test auth/me endpoint
        self.test_auth_me_endpoint()
        
        # Test event management
        self.test_event_management_comprehensive()
        
        # Test student registration flow
        self.test_student_registration_flow()
        
        # Test organizer features
        self.test_organizer_features()
        
        # Test rating system
        self.test_rating_system()
        
        # Test AI recommendations
        self.test_ai_recommendations()
        
        # Test error handling
        self.test_error_handling()
        
        # Test response times
        self.test_response_times()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['details']}")
        else:
            print("\n🎉 All tests passed! Backend is fully functional.")
        
        print("\n" + "=" * 70)
        return passed, failed, total

if __name__ == "__main__":
    tester = ComprehensiveJoinUpTester()
    passed, failed, total = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)