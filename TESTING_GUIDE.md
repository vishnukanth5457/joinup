# JoinUp Platform - Testing Guide

## 🧪 Complete Testing Workflow

### Prerequisites
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:8081
- ✅ MongoDB running
- ✅ Browser open to http://localhost:8081

---

## 1️⃣ Test Student Registration & Login

### Step 1: Register as Student
1. Open http://localhost:8081
2. Click on **"Student"** role card
3. Fill registration form:
   - Email: `student@example.com`
   - Password: `password123`
   - Name: `John Student`
   - College: `ABC College`
   - Department: `Computer Science`
   - Year: `2`
4. Click **Register**
5. ✅ Should see student dashboard

### Step 2: Test Logout
1. Click **Profile** tab
2. Scroll down and click **Logout** button
3. Confirm logout
4. ✅ Should return to home screen with role selection

### Step 3: Test Login
1. Click **Student** again
2. Click **Already have account? Login**
3. Enter:
   - Email: `student@example.com`
   - Password: `password123`
4. Click **Login**
5. ✅ Should see student dashboard

---

## 2️⃣ Test Organizer Registration & Dashboard

### Step 1: Register as Organizer
1. Go back to home
2. Click **University / Club** (Organizer) role
3. Fill form:
   - Email: `organizer@example.com`
   - Password: `password123`
   - Name: `Jane Organizer`
   - College: `XYZ University`
   - Organization: `Tech Club`
4. Click **Register**
5. ✅ Should see organizer dashboard

### Step 2: Create Event
1. In organizer dashboard, click **Create Event**
2. Fill event form:
   - Title: `Tech Conference 2025`
   - Description: `Annual tech conference for students`
   - Date: `2025-02-15`
   - Venue: `Main Auditorium`
   - Fee: `0`
   - Category: `Technology`
   - Max Participants: `100`
3. Click **Create**
4. ✅ Event should appear in dashboard

### Step 3: Test Logout
1. Click **Logout** button
2. ✅ Should return to home

---

## 3️⃣ Test Student Event Registration

### Step 1: Login as Student
1. Go to home and select **Student**
2. Login with student credentials

### Step 2: Browse Events
1. Click **Home** tab
2. ✅ Should see the event created by organizer
3. Click on event card
4. ✅ Should see event details

### Step 3: Register for Event
1. Click **Register** button
2. Confirm registration
3. ✅ Should show success message
4. Event should appear in **My Events** tab

### Step 4: Test Cancel Registration
1. Go to **My Events** tab
2. Find the registered event
3. Click **Cancel** (if available)
4. ✅ Should be removed from my events

---

## 4️⃣ Test Admin Dashboard

### Step 1: Register as Admin
1. Go home, select **Admin** role
2. Register with:
   - Email: `admin@example.com`
   - Password: `password123`
   - Name: `Admin User`
   - College: `Admin College`
3. ✅ Should see admin dashboard

### Step 2: View Stats
1. ✅ Should see:
   - Total users
   - Total events
   - System status

### Step 3: Logout
1. Click logout
2. ✅ Return to home

---

## 5️⃣ Test Error Scenarios

### Invalid Login
1. Try login with wrong email format
2. ✅ Should show: "Please enter a valid email address"

3. Try login with empty password
4. ✅ Should show: "Password is required"

5. Try login with short password
6. ✅ Should show: "Password must be at least 6 characters"

7. Try login with wrong credentials
8. ✅ Should show: "Invalid email or password"

### Network Error
1. Stop backend server
2. Try to login or register
3. ✅ Should show: "Network error. Please check your connection."

---

## 6️⃣ API Testing with curl

### Check Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"JoinUp API"}
```

### Register Student
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "role": "student",
    "college": "Test College"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Get My Info (add Authorization header)
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📋 Checklist for Complete Testing

### Authentication ✅
- [ ] Student registration works
- [ ] Student login works
- [ ] Student logout works
- [ ] Organizer registration works
- [ ] Organizer login works
- [ ] Organizer logout works
- [ ] Admin registration works
- [ ] Admin login works
- [ ] Admin logout works
- [ ] Password validation works
- [ ] Email validation works
- [ ] Error messages display properly

### Events ✅
- [ ] Organizer can create event
- [ ] Event appears in student discovery
- [ ] Student can view event details
- [ ] Event has correct information

### Registration ✅
- [ ] Student can register for event
- [ ] Registration count increases
- [ ] Student can view registered events
- [ ] Student can cancel registration

### Dashboard ✅
- [ ] Student dashboard shows stats
- [ ] Organizer dashboard shows events
- [ ] Admin dashboard shows system info

### Navigation ✅
- [ ] All tabs work in student app
- [ ] Role-based navigation works
- [ ] Back buttons work
- [ ] Logo navigation works

### Error Handling ✅
- [ ] Invalid email shows error
- [ ] Empty fields show error
- [ ] Network errors handled
- [ ] API errors display properly

---

## 🎯 Success Criteria

✅ **All tests pass** when:
1. Can register and login for all roles
2. Logout works on all screens
3. Events can be created, viewed, registered
4. Navigation is smooth
5. Error messages are clear
6. No console errors
7. No white screens/crashes
8. API responds properly
9. Data persists after reload
10. All validations work

---

## 📞 Troubleshooting

### Backend not running
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Or use curl to check health
curl http://localhost:8000/health
```

### Frontend won't start
```bash
# Clear cache and restart
rm -rf node_modules/.cache
npm start
```

### MongoDB connection error
```bash
# Ensure MongoDB is running
# On Windows: Check Services or mongod in admin cmd
# Default: mongodb://localhost:27017
```

### CORS errors
- Backend CORS is configured for all origins
- Check browser console for exact error
- Verify API_URL in frontend .env

### 401 Unauthorized
- Token might be expired
- Try logging out and back in
- Check if token is stored in AsyncStorage

---

**Created**: January 16, 2026
**Status**: Ready for Testing
