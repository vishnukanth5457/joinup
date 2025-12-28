#!/usr/bin/env python3
"""
Direct JoinUp Backend Testing - All Scenarios from Review Request
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "https://campuslink-69.preview.emergentagent.com/api"

def test_backend_comprehensive():
    print("🚀 JoinUp Backend Comprehensive Testing")
    print("=" * 50)
    
    results = []
    
    # Test 1: Student Login
    print("\n1. Testing Student Login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"email": "john.smith0@student.com", "password": "student123"},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            student_token = data["access_token"]
            print(f"✅ Student login successful: {data['user']['name']}")
            results.append("✅ Student Login: SUCCESS")
        else:
            print(f"❌ Student login failed: {response.status_code} - {response.text}")
            results.append("❌ Student Login: FAILED")
            return results
    except Exception as e:
        print(f"❌ Student login error: {e}")
        results.append("❌ Student Login: ERROR")
        return results
    
    # Test 2: Organizer Login
    print("\n2. Testing Organizer Login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"email": "organizer1@mit.com", "password": "organizer123"},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            organizer_token = data["access_token"]
            print(f"✅ Organizer login successful: {data['user']['name']}")
            results.append("✅ Organizer Login: SUCCESS")
        else:
            print(f"❌ Organizer login failed: {response.status_code} - {response.text}")
            results.append("❌ Organizer Login: FAILED")
            return results
    except Exception as e:
        print(f"❌ Organizer login error: {e}")
        results.append("❌ Organizer Login: ERROR")
        return results
    
    # Test 3: Auth Me Endpoint
    print("\n3. Testing /auth/me endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auth me successful: {data['name']} ({data['role']})")
            results.append("✅ Auth Me Endpoint: SUCCESS")
        else:
            print(f"❌ Auth me failed: {response.status_code} - {response.text}")
            results.append("❌ Auth Me Endpoint: FAILED")
    except Exception as e:
        print(f"❌ Auth me error: {e}")
        results.append("❌ Auth Me Endpoint: ERROR")
    
    # Test 4: Invalid Credentials
    print("\n4. Testing Invalid Credentials...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"email": "invalid@test.com", "password": "wrongpassword"},
                               timeout=10)
        if response.status_code == 401:
            print("✅ Invalid credentials correctly rejected")
            results.append("✅ Invalid Credentials: SUCCESS")
        else:
            print(f"❌ Invalid credentials test failed: {response.status_code}")
            results.append("❌ Invalid Credentials: FAILED")
    except Exception as e:
        print(f"❌ Invalid credentials error: {e}")
        results.append("❌ Invalid Credentials: ERROR")
    
    # Test 5: Get All Events
    print("\n5. Testing Get All Events...")
    try:
        response = requests.get(f"{BASE_URL}/events", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Retrieved {len(events)} events")
            results.append(f"✅ Get All Events: SUCCESS ({len(events)} events)")
            # Store first event for later tests
            first_event_id = events[0]["id"] if events else None
        else:
            print(f"❌ Get events failed: {response.status_code} - {response.text}")
            results.append("❌ Get All Events: FAILED")
            first_event_id = None
    except Exception as e:
        print(f"❌ Get events error: {e}")
        results.append("❌ Get All Events: ERROR")
        first_event_id = None
    
    # Test 6: Search Events
    print("\n6. Testing Search Events...")
    try:
        response = requests.get(f"{BASE_URL}/events?search=AI", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Search found {len(events)} events matching 'AI'")
            results.append(f"✅ Search Events: SUCCESS ({len(events)} results)")
        else:
            print(f"❌ Search events failed: {response.status_code}")
            results.append("❌ Search Events: FAILED")
    except Exception as e:
        print(f"❌ Search events error: {e}")
        results.append("❌ Search Events: ERROR")
    
    # Test 7: Filter Events by College
    print("\n7. Testing Filter Events by College...")
    try:
        response = requests.get(f"{BASE_URL}/events?college=MIT", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Filter found {len(events)} events at MIT")
            results.append(f"✅ Filter Events: SUCCESS ({len(events)} MIT events)")
        else:
            print(f"❌ Filter events failed: {response.status_code}")
            results.append("❌ Filter Events: FAILED")
    except Exception as e:
        print(f"❌ Filter events error: {e}")
        results.append("❌ Filter Events: ERROR")
    
    # Test 8: Get Specific Event Details
    if first_event_id:
        print("\n8. Testing Get Specific Event Details...")
        try:
            response = requests.get(f"{BASE_URL}/events/{first_event_id}", 
                                  headers={"Authorization": f"Bearer {student_token}"},
                                  timeout=10)
            if response.status_code == 200:
                event = response.json()
                print(f"✅ Retrieved event details: {event['title']}")
                results.append("✅ Get Event Details: SUCCESS")
            else:
                print(f"❌ Get event details failed: {response.status_code}")
                results.append("❌ Get Event Details: FAILED")
        except Exception as e:
            print(f"❌ Get event details error: {e}")
            results.append("❌ Get Event Details: ERROR")
    
    # Test 9: Get Organizer Events
    print("\n9. Testing Get Organizer Events...")
    try:
        response = requests.get(f"{BASE_URL}/events/organizer/my-events", 
                              headers={"Authorization": f"Bearer {organizer_token}"},
                              timeout=10)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Organizer has {len(events)} events")
            results.append(f"✅ Organizer Events: SUCCESS ({len(events)} events)")
        else:
            print(f"❌ Get organizer events failed: {response.status_code}")
            results.append("❌ Organizer Events: FAILED")
    except Exception as e:
        print(f"❌ Get organizer events error: {e}")
        results.append("❌ Organizer Events: ERROR")
    
    # Test 10: Register for Event
    if first_event_id:
        print("\n10. Testing Register for Event...")
        try:
            response = requests.post(f"{BASE_URL}/registrations", 
                                   json={"event_id": first_event_id},
                                   headers={"Authorization": f"Bearer {student_token}"},
                                   timeout=10)
            if response.status_code == 200:
                registration = response.json()
                qr_code = registration["qr_code_data"]
                registration_id = registration["id"]
                print(f"✅ Registration successful. QR: {qr_code}")
                results.append("✅ Event Registration: SUCCESS")
            elif response.status_code == 400 and "already registered" in response.text:
                print("✅ Already registered (expected)")
                results.append("✅ Event Registration: SUCCESS (already registered)")
                # Get existing registration
                reg_response = requests.get(f"{BASE_URL}/registrations/my-registrations", 
                                          headers={"Authorization": f"Bearer {student_token}"},
                                          timeout=10)
                if reg_response.status_code == 200:
                    registrations = reg_response.json()
                    for reg in registrations:
                        if reg["event_id"] == first_event_id:
                            qr_code = reg["qr_code_data"]
                            registration_id = reg["id"]
                            break
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                results.append("❌ Event Registration: FAILED")
                qr_code = None
                registration_id = None
        except Exception as e:
            print(f"❌ Registration error: {e}")
            results.append("❌ Event Registration: ERROR")
            qr_code = None
            registration_id = None
    
    # Test 11: Get Student Registrations
    print("\n11. Testing Get Student Registrations...")
    try:
        response = requests.get(f"{BASE_URL}/registrations/my-registrations", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 200:
            registrations = response.json()
            qr_codes_present = all("qr_code_data" in reg for reg in registrations)
            print(f"✅ Retrieved {len(registrations)} registrations. QR codes: {'✅' if qr_codes_present else '❌'}")
            results.append(f"✅ Student Registrations: SUCCESS ({len(registrations)} registrations)")
        else:
            print(f"❌ Get registrations failed: {response.status_code}")
            results.append("❌ Student Registrations: FAILED")
    except Exception as e:
        print(f"❌ Get registrations error: {e}")
        results.append("❌ Student Registrations: ERROR")
    
    # Test 12: Student Dashboard Stats
    print("\n12. Testing Student Dashboard...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/student", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Dashboard stats: {stats['total_events_registered']} registered, {stats['attended_events']} attended, {stats['certificates_earned']} certificates")
            results.append("✅ Student Dashboard: SUCCESS")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            results.append("❌ Student Dashboard: FAILED")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        results.append("❌ Student Dashboard: ERROR")
    
    # Test 13: Duplicate Registration
    if first_event_id:
        print("\n13. Testing Duplicate Registration...")
        try:
            response = requests.post(f"{BASE_URL}/registrations", 
                                   json={"event_id": first_event_id},
                                   headers={"Authorization": f"Bearer {student_token}"},
                                   timeout=10)
            if response.status_code == 400 and "already registered" in response.text:
                print("✅ Duplicate registration correctly rejected")
                results.append("✅ Duplicate Registration Prevention: SUCCESS")
            else:
                print(f"❌ Duplicate registration test failed: {response.status_code}")
                results.append("❌ Duplicate Registration Prevention: FAILED")
        except Exception as e:
            print(f"❌ Duplicate registration error: {e}")
            results.append("❌ Duplicate Registration Prevention: ERROR")
    
    # Test 14: Create New Event (Organizer)
    print("\n14. Testing Create New Event...")
    try:
        event_data = {
            "title": "Backend Testing Workshop",
            "description": "Learn comprehensive backend testing strategies",
            "date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "venue": "MIT Lab 101",
            "fee": 25.0,
            "college": "MIT",
            "category": "Technology",
            "max_participants": 30
        }
        response = requests.post(f"{BASE_URL}/events", 
                               json=event_data,
                               headers={"Authorization": f"Bearer {organizer_token}"},
                               timeout=10)
        if response.status_code == 200:
            event = response.json()
            new_event_id = event["id"]
            print(f"✅ Created event: {event['title']}")
            results.append("✅ Create Event: SUCCESS")
        else:
            print(f"❌ Create event failed: {response.status_code} - {response.text}")
            results.append("❌ Create Event: FAILED")
            new_event_id = None
    except Exception as e:
        print(f"❌ Create event error: {e}")
        results.append("❌ Create Event: ERROR")
        new_event_id = None
    
    # Test 15: Get Event Registrations (Organizer)
    if first_event_id:
        print("\n15. Testing Get Event Registrations...")
        try:
            response = requests.get(f"{BASE_URL}/registrations/event/{first_event_id}", 
                                  headers={"Authorization": f"Bearer {organizer_token}"},
                                  timeout=10)
            if response.status_code == 200:
                registrations = response.json()
                print(f"✅ Event has {len(registrations)} registrations")
                results.append(f"✅ Event Registrations: SUCCESS ({len(registrations)} registrations)")
            else:
                print(f"❌ Get event registrations failed: {response.status_code}")
                results.append("❌ Event Registrations: FAILED")
        except Exception as e:
            print(f"❌ Get event registrations error: {e}")
            results.append("❌ Event Registrations: ERROR")
    
    # Test 16: Mark Attendance via QR
    if 'qr_code' in locals() and qr_code:
        print("\n16. Testing Mark Attendance via QR...")
        try:
            response = requests.post(f"{BASE_URL}/attendance/mark", 
                                   json={"qr_code_data": qr_code},
                                   headers={"Authorization": f"Bearer {organizer_token}"},
                                   timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Attendance marked for: {result['student_name']}")
                results.append("✅ Mark Attendance: SUCCESS")
            elif response.status_code == 400 and "already marked" in response.text:
                print("✅ Attendance already marked (expected)")
                results.append("✅ Mark Attendance: SUCCESS (already marked)")
            else:
                print(f"❌ Mark attendance failed: {response.status_code} - {response.text}")
                results.append("❌ Mark Attendance: FAILED")
        except Exception as e:
            print(f"❌ Mark attendance error: {e}")
            results.append("❌ Mark Attendance: ERROR")
    
    # Test 17: Issue Certificate
    if 'registration_id' in locals() and registration_id:
        print("\n17. Testing Issue Certificate...")
        try:
            response = requests.post(f"{BASE_URL}/certificates/issue", 
                                   json={"registration_id": registration_id},
                                   headers={"Authorization": f"Bearer {organizer_token}"},
                                   timeout=10)
            if response.status_code == 200:
                certificate = response.json()
                print(f"✅ Certificate issued for: {certificate['student_name']}")
                results.append("✅ Issue Certificate: SUCCESS")
            else:
                print(f"❌ Issue certificate failed: {response.status_code} - {response.text}")
                results.append("❌ Issue Certificate: FAILED")
        except Exception as e:
            print(f"❌ Issue certificate error: {e}")
            results.append("❌ Issue Certificate: ERROR")
    
    # Test 18: Organizer Analytics
    print("\n18. Testing Organizer Analytics...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/organizer", 
                              headers={"Authorization": f"Bearer {organizer_token}"},
                              timeout=10)
        if response.status_code == 200:
            analytics = response.json()
            print(f"✅ Analytics: {analytics['total_events']} events, {analytics['total_registrations']} registrations, {analytics['total_attendees']} attendees")
            results.append("✅ Organizer Analytics: SUCCESS")
        else:
            print(f"❌ Organizer analytics failed: {response.status_code}")
            results.append("❌ Organizer Analytics: FAILED")
    except Exception as e:
        print(f"❌ Organizer analytics error: {e}")
        results.append("❌ Organizer Analytics: ERROR")
    
    # Test 19: Rate Event
    if first_event_id:
        print("\n19. Testing Rate Event...")
        try:
            rating_data = {
                "event_id": first_event_id,
                "rating": 5,
                "feedback": "Excellent event! Very well organized and informative."
            }
            response = requests.post(f"{BASE_URL}/ratings", 
                                   json=rating_data,
                                   headers={"Authorization": f"Bearer {student_token}"},
                                   timeout=10)
            if response.status_code == 200:
                rating = response.json()
                print(f"✅ Event rated: {rating['rating']}/5 stars")
                results.append("✅ Rate Event: SUCCESS")
            elif response.status_code == 400:
                error_msg = response.json().get("detail", "")
                if "already rated" in error_msg or "can only rate events you attended" in error_msg:
                    print(f"✅ Expected restriction: {error_msg}")
                    results.append("✅ Rate Event: SUCCESS (expected restriction)")
                else:
                    print(f"❌ Unexpected error: {error_msg}")
                    results.append("❌ Rate Event: FAILED")
            else:
                print(f"❌ Rate event failed: {response.status_code}")
                results.append("❌ Rate Event: FAILED")
        except Exception as e:
            print(f"❌ Rate event error: {e}")
            results.append("❌ Rate Event: ERROR")
    
    # Test 20: Get Event Ratings
    if first_event_id:
        print("\n20. Testing Get Event Ratings...")
        try:
            response = requests.get(f"{BASE_URL}/ratings/event/{first_event_id}", 
                                  headers={"Authorization": f"Bearer {student_token}"},
                                  timeout=10)
            if response.status_code == 200:
                ratings = response.json()
                print(f"✅ Event has {len(ratings)} ratings")
                results.append(f"✅ Get Event Ratings: SUCCESS ({len(ratings)} ratings)")
            else:
                print(f"❌ Get event ratings failed: {response.status_code}")
                results.append("❌ Get Event Ratings: FAILED")
        except Exception as e:
            print(f"❌ Get event ratings error: {e}")
            results.append("❌ Get Event Ratings: ERROR")
    
    # Test 21: AI Recommendations
    print("\n21. Testing AI Recommendations...")
    try:
        response = requests.get(f"{BASE_URL}/recommendations", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Received {len(recommendations)} personalized recommendations")
            results.append(f"✅ AI Recommendations: SUCCESS ({len(recommendations)} recommendations)")
        else:
            print(f"❌ AI recommendations failed: {response.status_code}")
            results.append("❌ AI Recommendations: FAILED")
    except Exception as e:
        print(f"❌ AI recommendations error: {e}")
        results.append("❌ AI Recommendations: ERROR")
    
    # Test 22: 401 Unauthorized Access
    print("\n22. Testing 401 Unauthorized Access...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", timeout=10)  # No token
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized access")
            results.append("✅ 401 Unauthorized: SUCCESS")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            results.append("❌ 401 Unauthorized: FAILED")
    except Exception as e:
        print(f"❌ Unauthorized test error: {e}")
        results.append("❌ 401 Unauthorized: ERROR")
    
    # Test 23: 404 Non-existent Resource
    print("\n23. Testing 404 Non-existent Resource...")
    try:
        response = requests.get(f"{BASE_URL}/events/non-existent-event-id", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent event")
            results.append("✅ 404 Non-existent: SUCCESS")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            results.append("❌ 404 Non-existent: FAILED")
    except Exception as e:
        print(f"❌ 404 test error: {e}")
        results.append("❌ 404 Non-existent: ERROR")
    
    # Test 24: Role-based Access Control
    print("\n24. Testing Role-based Access Control...")
    try:
        response = requests.get(f"{BASE_URL}/events/organizer/my-events", 
                              headers={"Authorization": f"Bearer {student_token}"},
                              timeout=10)
        if response.status_code == 403:
            print("✅ Correctly rejected student access to organizer endpoint")
            results.append("✅ Role-based Access: SUCCESS")
        else:
            print(f"❌ Expected 403, got {response.status_code}")
            results.append("❌ Role-based Access: FAILED")
    except Exception as e:
        print(f"❌ Role-based access error: {e}")
        results.append("❌ Role-based Access: ERROR")
    
    # Test 25: Validation Errors
    print("\n25. Testing Validation Errors...")
    try:
        invalid_data = {
            "title": "",
            "description": "Test",
            "date": "invalid-date",
            "venue": "",
            "fee": -10,
            "college": "MIT"
        }
        response = requests.post(f"{BASE_URL}/events", 
                               json=invalid_data,
                               headers={"Authorization": f"Bearer {organizer_token}"},
                               timeout=10)
        if response.status_code in [400, 422]:
            print("✅ Correctly rejected invalid event data")
            results.append("✅ Validation Errors: SUCCESS")
        else:
            print(f"❌ Expected 400/422, got {response.status_code}")
            results.append("❌ Validation Errors: FAILED")
    except Exception as e:
        print(f"❌ Validation test error: {e}")
        results.append("❌ Validation Errors: ERROR")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results if "✅" in result)
    failed = sum(1 for result in results if "❌" in result)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for result in results:
        print(f"  {result}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Backend is fully functional.")
    else:
        print(f"\n⚠️  {failed} tests failed. See details above.")
    
    return results

if __name__ == "__main__":
    test_backend_comprehensive()