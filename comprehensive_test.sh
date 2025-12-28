#!/bin/bash

# JoinUp Backend Comprehensive Testing Script
# Tests all scenarios mentioned in the review request

echo "🚀 JoinUp Backend Comprehensive Testing"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="https://campuslink-69.preview.emergentagent.com/api"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to log test results
log_test() {
    local test_name="$1"
    local success="$2"
    local details="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$success" = "true" ]; then
        echo -e "${GREEN}✅ PASS${NC} $test_name: $details"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} $test_name: $details"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to make API request and check response
make_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local token="$4"
    local expected_status="$5"
    
    local headers="Content-Type: application/json"
    if [ -n "$token" ]; then
        headers="$headers -H Authorization: Bearer $token"
    fi
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" -H "$headers" --max-time 10)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" -H "$headers" -d "$data" --max-time 10)
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract response body (all but last line)
    response_body=$(echo "$response" | head -n -1)
    
    echo "$status_code:$response_body"
}

echo -e "\n${BLUE}📋 1. AUTHENTICATION & USER MANAGEMENT${NC}"
echo "----------------------------------------"

# Test 1: Student Login
echo "🧪 Testing Student Login..."
login_response=$(make_request "POST" "/auth/login" '{"email": "john.smith0@student.com", "password": "student123"}' "" "200")
status_code=$(echo "$login_response" | cut -d: -f1)
response_body=$(echo "$login_response" | cut -d: -f2-)

if [ "$status_code" = "200" ]; then
    STUDENT_TOKEN=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    if [ -n "$STUDENT_TOKEN" ]; then
        log_test "Student Login" "true" "Successfully logged in as john.smith0@student.com"
    else
        log_test "Student Login" "false" "No access token in response"
    fi
else
    log_test "Student Login" "false" "Status: $status_code, Response: $response_body"
fi

# Test 2: Organizer Login
echo "🧪 Testing Organizer Login..."
login_response=$(make_request "POST" "/auth/login" '{"email": "organizer1@mit.com", "password": "organizer123"}' "" "200")
status_code=$(echo "$login_response" | cut -d: -f1)
response_body=$(echo "$login_response" | cut -d: -f2-)

if [ "$status_code" = "200" ]; then
    ORGANIZER_TOKEN=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    if [ -n "$ORGANIZER_TOKEN" ]; then
        log_test "Organizer Login" "true" "Successfully logged in as organizer1@mit.com"
    else
        log_test "Organizer Login" "false" "No access token in response"
    fi
else
    log_test "Organizer Login" "false" "Status: $status_code, Response: $response_body"
fi

# Test 3: Auth Me Endpoint
echo "🧪 Testing /auth/me endpoint..."
if [ -n "$STUDENT_TOKEN" ]; then
    auth_response=$(make_request "GET" "/auth/me" "" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$auth_response" | cut -d: -f1)
    response_body=$(echo "$auth_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        user_name=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])" 2>/dev/null)
        log_test "Auth Me Endpoint" "true" "Retrieved user info: $user_name"
    else
        log_test "Auth Me Endpoint" "false" "Status: $status_code"
    fi
else
    log_test "Auth Me Endpoint" "false" "No student token available"
fi

# Test 4: Invalid Credentials
echo "🧪 Testing Invalid Credentials..."
invalid_response=$(make_request "POST" "/auth/login" '{"email": "invalid@test.com", "password": "wrongpassword"}' "" "401")
status_code=$(echo "$invalid_response" | cut -d: -f1)

if [ "$status_code" = "401" ]; then
    log_test "Invalid Credentials Test" "true" "Correctly rejected invalid credentials"
else
    log_test "Invalid Credentials Test" "false" "Expected 401, got $status_code"
fi

echo -e "\n${BLUE}📋 2. EVENT MANAGEMENT${NC}"
echo "------------------------"

# Test 5: Get All Events (as student)
echo "🧪 Testing Get All Events..."
if [ -n "$STUDENT_TOKEN" ]; then
    events_response=$(make_request "GET" "/events" "" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$events_response" | cut -d: -f1)
    response_body=$(echo "$events_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        event_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "Get All Events" "true" "Retrieved $event_count events"
        
        # Get first event ID for later tests
        FIRST_EVENT_ID=$(echo "$response_body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null)
    else
        log_test "Get All Events" "false" "Status: $status_code"
    fi
else
    log_test "Get All Events" "false" "No student token available"
fi

# Test 6: Search Events
echo "🧪 Testing Search Events..."
if [ -n "$STUDENT_TOKEN" ]; then
    search_response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/events?search=AI" -H "Authorization: Bearer $STUDENT_TOKEN" --max-time 10)
    status_code=$(echo "$search_response" | tail -n1)
    response_body=$(echo "$search_response" | head -n -1)
    
    if [ "$status_code" = "200" ]; then
        search_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "Search Events" "true" "Found $search_count events matching 'AI'"
    else
        log_test "Search Events" "false" "Status: $status_code"
    fi
else
    log_test "Search Events" "false" "No student token available"
fi

# Test 7: Filter Events by College
echo "🧪 Testing Filter Events by College..."
if [ -n "$STUDENT_TOKEN" ]; then
    filter_response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/events?college=MIT" -H "Authorization: Bearer $STUDENT_TOKEN" --max-time 10)
    status_code=$(echo "$filter_response" | tail -n1)
    response_body=$(echo "$filter_response" | head -n -1)
    
    if [ "$status_code" = "200" ]; then
        filter_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "Filter Events by College" "true" "Found $filter_count events at MIT"
    else
        log_test "Filter Events by College" "false" "Status: $status_code"
    fi
else
    log_test "Filter Events by College" "false" "No student token available"
fi

# Test 8: Get Specific Event Details
echo "🧪 Testing Get Specific Event Details..."
if [ -n "$STUDENT_TOKEN" ] && [ -n "$FIRST_EVENT_ID" ]; then
    event_response=$(make_request "GET" "/events/$FIRST_EVENT_ID" "" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$event_response" | cut -d: -f1)
    response_body=$(echo "$event_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        event_title=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['title'])" 2>/dev/null)
        log_test "Get Specific Event Details" "true" "Retrieved event: $event_title"
    else
        log_test "Get Specific Event Details" "false" "Status: $status_code"
    fi
else
    log_test "Get Specific Event Details" "false" "No student token or event ID available"
fi

# Test 9: Get Organizer's Events
echo "🧪 Testing Get Organizer Events..."
if [ -n "$ORGANIZER_TOKEN" ]; then
    org_events_response=$(make_request "GET" "/events/organizer/my-events" "" "$ORGANIZER_TOKEN" "200")
    status_code=$(echo "$org_events_response" | cut -d: -f1)
    response_body=$(echo "$org_events_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        org_event_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "Get Organizer Events" "true" "Organizer has $org_event_count events"
    else
        log_test "Get Organizer Events" "false" "Status: $status_code"
    fi
else
    log_test "Get Organizer Events" "false" "No organizer token available"
fi

echo -e "\n${BLUE}📋 3. STUDENT REGISTRATION FLOW${NC}"
echo "--------------------------------"

# Test 10: Register for Event
echo "🧪 Testing Register for Event..."
if [ -n "$STUDENT_TOKEN" ] && [ -n "$FIRST_EVENT_ID" ]; then
    reg_response=$(make_request "POST" "/registrations" "{\"event_id\": \"$FIRST_EVENT_ID\"}" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$reg_response" | cut -d: -f1)
    response_body=$(echo "$reg_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        QR_CODE=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['qr_code_data'])" 2>/dev/null)
        REGISTRATION_ID=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
        log_test "Register for Event" "true" "Registration successful. QR: $QR_CODE"
    elif [ "$status_code" = "400" ]; then
        error_msg=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['detail'])" 2>/dev/null)
        if [[ "$error_msg" == *"already registered"* ]]; then
            log_test "Register for Event" "true" "Already registered (expected for existing user)"
            # Get existing registration
            existing_reg=$(make_request "GET" "/registrations/my-registrations" "" "$STUDENT_TOKEN" "200")
            existing_status=$(echo "$existing_reg" | cut -d: -f1)
            existing_body=$(echo "$existing_reg" | cut -d: -f2-)
            if [ "$existing_status" = "200" ]; then
                QR_CODE=$(echo "$existing_body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['qr_code_data'] if data else '')" 2>/dev/null)
                REGISTRATION_ID=$(echo "$existing_body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null)
            fi
        else
            log_test "Register for Event" "false" "Unexpected error: $error_msg"
        fi
    else
        log_test "Register for Event" "false" "Status: $status_code, Response: $response_body"
    fi
else
    log_test "Register for Event" "false" "No student token or event ID available"
fi

# Test 11: Get Student Registrations
echo "🧪 Testing Get Student Registrations..."
if [ -n "$STUDENT_TOKEN" ]; then
    my_reg_response=$(make_request "GET" "/registrations/my-registrations" "" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$my_reg_response" | cut -d: -f1)
    response_body=$(echo "$my_reg_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        reg_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "Get Student Registrations" "true" "Retrieved $reg_count registrations"
    else
        log_test "Get Student Registrations" "false" "Status: $status_code"
    fi
else
    log_test "Get Student Registrations" "false" "No student token available"
fi

# Test 12: Student Dashboard Stats
echo "🧪 Testing Student Dashboard..."
if [ -n "$STUDENT_TOKEN" ]; then
    dashboard_response=$(make_request "GET" "/dashboard/student" "" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$dashboard_response" | cut -d: -f1)
    response_body=$(echo "$dashboard_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        total_events=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_events_registered'])" 2>/dev/null)
        attended=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['attended_events'])" 2>/dev/null)
        certificates=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['certificates_earned'])" 2>/dev/null)
        log_test "Student Dashboard Stats" "true" "Stats: $total_events registered, $attended attended, $certificates certificates"
    else
        log_test "Student Dashboard Stats" "false" "Status: $status_code"
    fi
else
    log_test "Student Dashboard Stats" "false" "No student token available"
fi

# Test 13: Duplicate Registration (should fail)
echo "🧪 Testing Duplicate Registration..."
if [ -n "$STUDENT_TOKEN" ] && [ -n "$FIRST_EVENT_ID" ]; then
    dup_reg_response=$(make_request "POST" "/registrations" "{\"event_id\": \"$FIRST_EVENT_ID\"}" "$STUDENT_TOKEN" "400")
    status_code=$(echo "$dup_reg_response" | cut -d: -f1)
    response_body=$(echo "$dup_reg_response" | cut -d: -f2-)
    
    if [ "$status_code" = "400" ]; then
        error_msg=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['detail'])" 2>/dev/null)
        if [[ "$error_msg" == *"already registered"* ]]; then
            log_test "Duplicate Registration Prevention" "true" "Correctly rejected duplicate registration"
        else
            log_test "Duplicate Registration Prevention" "false" "Wrong error message: $error_msg"
        fi
    else
        log_test "Duplicate Registration Prevention" "false" "Expected 400, got $status_code"
    fi
else
    log_test "Duplicate Registration Prevention" "false" "No student token or event ID available"
fi

echo -e "\n${BLUE}📋 4. ORGANIZER FEATURES${NC}"
echo "-------------------------"

# Test 14: Create New Event
echo "🧪 Testing Create New Event..."
if [ -n "$ORGANIZER_TOKEN" ]; then
    event_data='{
        "title": "Backend Testing Workshop",
        "description": "Learn comprehensive backend testing strategies",
        "date": "2025-02-15T14:00:00",
        "venue": "MIT Lab 101",
        "fee": 25.0,
        "college": "MIT",
        "category": "Technology",
        "max_participants": 30
    }'
    
    create_response=$(make_request "POST" "/events" "$event_data" "$ORGANIZER_TOKEN" "200")
    status_code=$(echo "$create_response" | cut -d: -f1)
    response_body=$(echo "$create_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        new_event_title=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['title'])" 2>/dev/null)
        NEW_EVENT_ID=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
        log_test "Create New Event" "true" "Created event: $new_event_title"
    else
        log_test "Create New Event" "false" "Status: $status_code, Response: $response_body"
    fi
else
    log_test "Create New Event" "false" "No organizer token available"
fi

# Test 15: Get Event Registrations
echo "🧪 Testing Get Event Registrations..."
if [ -n "$ORGANIZER_TOKEN" ] && [ -n "$FIRST_EVENT_ID" ]; then
    event_reg_response=$(make_request "GET" "/registrations/event/$FIRST_EVENT_ID" "" "$ORGANIZER_TOKEN" "200")
    status_code=$(echo "$event_reg_response" | cut -d: -f1)
    response_body=$(echo "$event_reg_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        event_reg_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "Get Event Registrations" "true" "Event has $event_reg_count registrations"
    else
        log_test "Get Event Registrations" "false" "Status: $status_code"
    fi
else
    log_test "Get Event Registrations" "false" "No organizer token or event ID available"
fi

# Test 16: Mark Attendance via QR
echo "🧪 Testing Mark Attendance..."
if [ -n "$ORGANIZER_TOKEN" ] && [ -n "$QR_CODE" ]; then
    attendance_response=$(make_request "POST" "/attendance/mark" "{\"qr_code_data\": \"$QR_CODE\"}" "$ORGANIZER_TOKEN" "200")
    status_code=$(echo "$attendance_response" | cut -d: -f1)
    response_body=$(echo "$attendance_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        student_name=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['student_name'])" 2>/dev/null)
        log_test "Mark Attendance via QR" "true" "Attendance marked for: $student_name"
    elif [ "$status_code" = "400" ]; then
        error_msg=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['detail'])" 2>/dev/null)
        if [[ "$error_msg" == *"already marked"* ]]; then
            log_test "Mark Attendance via QR" "true" "Attendance already marked (expected)"
        else
            log_test "Mark Attendance via QR" "false" "Unexpected error: $error_msg"
        fi
    else
        log_test "Mark Attendance via QR" "false" "Status: $status_code, Response: $response_body"
    fi
else
    log_test "Mark Attendance via QR" "false" "No organizer token or QR code available"
fi

# Test 17: Issue Certificate
echo "🧪 Testing Issue Certificate..."
if [ -n "$ORGANIZER_TOKEN" ] && [ -n "$REGISTRATION_ID" ]; then
    cert_response=$(make_request "POST" "/certificates/issue" "{\"registration_id\": \"$REGISTRATION_ID\"}" "$ORGANIZER_TOKEN" "200")
    status_code=$(echo "$cert_response" | cut -d: -f1)
    response_body=$(echo "$cert_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        cert_student=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['student_name'])" 2>/dev/null)
        log_test "Issue Certificate" "true" "Certificate issued for: $cert_student"
    else
        error_msg=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['detail'])" 2>/dev/null)
        log_test "Issue Certificate" "false" "Status: $status_code, Error: $error_msg"
    fi
else
    log_test "Issue Certificate" "false" "No organizer token or registration ID available"
fi

# Test 18: Organizer Analytics
echo "🧪 Testing Organizer Analytics..."
if [ -n "$ORGANIZER_TOKEN" ]; then
    analytics_response=$(make_request "GET" "/dashboard/organizer" "" "$ORGANIZER_TOKEN" "200")
    status_code=$(echo "$analytics_response" | cut -d: -f1)
    response_body=$(echo "$analytics_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        total_events=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_events'])" 2>/dev/null)
        total_regs=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_registrations'])" 2>/dev/null)
        log_test "Organizer Analytics" "true" "Analytics: $total_events events, $total_regs registrations"
    else
        log_test "Organizer Analytics" "false" "Status: $status_code"
    fi
else
    log_test "Organizer Analytics" "false" "No organizer token available"
fi

echo -e "\n${BLUE}📋 5. RATING SYSTEM${NC}"
echo "--------------------"

# Test 19: Rate Event
echo "🧪 Testing Rate Event..."
if [ -n "$STUDENT_TOKEN" ] && [ -n "$FIRST_EVENT_ID" ]; then
    rating_data='{
        "event_id": "'$FIRST_EVENT_ID'",
        "rating": 5,
        "feedback": "Excellent event! Very well organized and informative."
    }'
    
    rating_response=$(make_request "POST" "/ratings" "$rating_data" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$rating_response" | cut -d: -f1)
    response_body=$(echo "$rating_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        rating_value=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['rating'])" 2>/dev/null)
        log_test "Rate Event" "true" "Event rated: $rating_value/5 stars"
    elif [ "$status_code" = "400" ]; then
        error_msg=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin)['detail'])" 2>/dev/null)
        if [[ "$error_msg" == *"already rated"* ]] || [[ "$error_msg" == *"can only rate events you attended"* ]]; then
            log_test "Rate Event" "true" "Expected restriction: $error_msg"
        else
            log_test "Rate Event" "false" "Unexpected error: $error_msg"
        fi
    else
        log_test "Rate Event" "false" "Status: $status_code, Response: $response_body"
    fi
else
    log_test "Rate Event" "false" "No student token or event ID available"
fi

# Test 20: Get Event Ratings
echo "🧪 Testing Get Event Ratings..."
if [ -n "$STUDENT_TOKEN" ] && [ -n "$FIRST_EVENT_ID" ]; then
    ratings_response=$(make_request "GET" "/ratings/event/$FIRST_EVENT_ID" "" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$ratings_response" | cut -d: -f1)
    response_body=$(echo "$ratings_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        ratings_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "Get Event Ratings" "true" "Event has $ratings_count ratings"
    else
        log_test "Get Event Ratings" "false" "Status: $status_code"
    fi
else
    log_test "Get Event Ratings" "false" "No student token or event ID available"
fi

echo -e "\n${BLUE}📋 6. AI RECOMMENDATIONS${NC}"
echo "-------------------------"

# Test 21: Get AI Recommendations
echo "🧪 Testing AI Recommendations..."
if [ -n "$STUDENT_TOKEN" ]; then
    rec_response=$(make_request "GET" "/recommendations" "" "$STUDENT_TOKEN" "200")
    status_code=$(echo "$rec_response" | cut -d: -f1)
    response_body=$(echo "$rec_response" | cut -d: -f2-)
    
    if [ "$status_code" = "200" ]; then
        rec_count=$(echo "$response_body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
        log_test "AI Recommendations" "true" "Received $rec_count personalized recommendations"
    else
        log_test "AI Recommendations" "false" "Status: $status_code"
    fi
else
    log_test "AI Recommendations" "false" "No student token available"
fi

echo -e "\n${BLUE}📋 7. ERROR HANDLING${NC}"
echo "---------------------"

# Test 22: 401 Unauthorized Access
echo "🧪 Testing 401 Unauthorized Access..."
unauth_response=$(make_request "GET" "/auth/me" "" "" "401")
status_code=$(echo "$unauth_response" | cut -d: -f1)

if [ "$status_code" = "401" ]; then
    log_test "401 Unauthorized Access" "true" "Correctly rejected unauthorized access"
else
    log_test "401 Unauthorized Access" "false" "Expected 401, got $status_code"
fi

# Test 23: 404 Non-existent Resource
echo "🧪 Testing 404 Non-existent Resource..."
if [ -n "$STUDENT_TOKEN" ]; then
    notfound_response=$(make_request "GET" "/events/non-existent-event-id" "" "$STUDENT_TOKEN" "404")
    status_code=$(echo "$notfound_response" | cut -d: -f1)
    
    if [ "$status_code" = "404" ]; then
        log_test "404 Non-existent Resource" "true" "Correctly returned 404 for non-existent event"
    else
        log_test "404 Non-existent Resource" "false" "Expected 404, got $status_code"
    fi
else
    log_test "404 Non-existent Resource" "false" "No student token available"
fi

# Test 24: Role-based Access Control
echo "🧪 Testing Role-based Access Control..."
if [ -n "$STUDENT_TOKEN" ]; then
    rbac_response=$(make_request "GET" "/events/organizer/my-events" "" "$STUDENT_TOKEN" "403")
    status_code=$(echo "$rbac_response" | cut -d: -f1)
    
    if [ "$status_code" = "403" ]; then
        log_test "Role-based Access Control" "true" "Correctly rejected student access to organizer endpoint"
    else
        log_test "Role-based Access Control" "false" "Expected 403, got $status_code"
    fi
else
    log_test "Role-based Access Control" "false" "No student token available"
fi

# Test 25: Validation Errors
echo "🧪 Testing Validation Errors..."
if [ -n "$ORGANIZER_TOKEN" ]; then
    invalid_data='{
        "title": "",
        "description": "Test",
        "date": "invalid-date",
        "venue": "",
        "fee": -10,
        "college": "MIT"
    }'
    
    validation_response=$(make_request "POST" "/events" "$invalid_data" "$ORGANIZER_TOKEN" "422")
    status_code=$(echo "$validation_response" | cut -d: -f1)
    
    if [ "$status_code" = "422" ] || [ "$status_code" = "400" ]; then
        log_test "Validation Error Handling" "true" "Correctly rejected invalid event data"
    else
        log_test "Validation Error Handling" "false" "Expected 400/422, got $status_code"
    fi
else
    log_test "Validation Error Handling" "false" "No organizer token available"
fi

# Summary
echo -e "\n${YELLOW}========================================"
echo "📊 COMPREHENSIVE TEST SUMMARY"
echo "========================================"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS ✅${NC}"
echo -e "${RED}Failed: $FAILED_TESTS ❌${NC}"

if [ $TOTAL_TESTS -gt 0 ]; then
    success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    echo -e "Success Rate: ${success_rate}%"
fi

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Backend is fully functional.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the results above.${NC}"
    exit 1
fi