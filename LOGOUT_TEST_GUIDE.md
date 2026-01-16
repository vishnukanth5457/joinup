# Quick Test Guide - Logout Fix

## Current Status
✅ **Backend:** Running on http://localhost:8080
✅ **Frontend:** Running on http://localhost:8081
✅ **Both connected and ready for testing**

## How to Test Logout

### Step 1: Open the App
- Go to http://localhost:8081 in your browser
- Or use Expo Go on your phone and scan the QR code

### Step 2: Register a Student
1. Click on "Student" role card
2. Fill in the registration form:
   - Email: `test@example.com` (any email)
   - Password: `Test123!` (any password)
   - Name: `Test User`
   - College: `Test College`
   - Department: `CS`
   - Year: `3`
3. Click Register
4. You should be logged in and see the student dashboard

### Step 3: Test Logout
1. Click on "Profile" tab (bottom right icon)
2. Scroll down to find the Logout button
3. Click the Logout button
4. Confirm logout in the alert

### Step 4: Verify Logout Works
**You should see:**
- Alert closes
- App navigates back to "Welcome! Choose Your Role" landing page
- Role selection cards (Student, University/Club, Admin) appear

**If logout works:**
- ✅ The fix is successful!
- ✅ Logout button now works on all roles (Student, Admin, Organizer)

## Check Console Logs
To see detailed logs:

### On Web (Browser):
1. Press `F12` to open Developer Tools
2. Go to Console tab
3. During logout, you should see logs like:
   ```
   [Profile] Logout button pressed
   [AuthContext] Starting logout...
   [AuthContext] Cleared React state
   [AuthContext] Logout complete
   [Index] User is null, showing landing page
   ```

### On Mobile (Expo Go):
1. Shake the phone to open Expo menu
2. Select "View logs" or check the "Logs" tab
3. You should see the same console logs

## What Was Fixed

### Before (Broken):
- Logout button clicked but app stayed on profile page
- Or showed blank screen
- Or didn't navigate properly

### After (Fixed):
1. State is cleared immediately in React
2. AsyncStorage is cleared in background (non-blocking)
3. Navigation happens with proper timing
4. Landing page is displayed correctly
5. User can re-login or choose different role

## Architecture

```
┌─────────────────────────────────────────┐
│          Logout Flow (Fixed)            │
├─────────────────────────────────────────┤
│                                         │
│  1. User clicks Logout button          │
│                    ↓                    │
│  2. Confirm in Alert dialog            │
│                    ↓                    │
│  3. logout() clears React state        │
│     (setUser(null), setToken(null))    │
│                    ↓ (IMMEDIATE)        │
│  4. React re-renders                   │
│     useEffect in index.tsx triggers    │
│                    ↓                    │
│  5. Detects user=null                  │
│                    ↓                    │
│  6. Shows landing page                 │
│     (Choose Your Role)                 │
│                    ↓ (in background)    │
│  7. AsyncStorage is cleared            │
│     (doesn't block UI)                 │
│                                         │
│  8. Navigation command: router.replace('/')
│                                         │
└─────────────────────────────────────────┘
```

## Files Changed
- ✅ `frontend/context/AuthContext.tsx` - Fixed state clearing order
- ✅ `frontend/app/index.tsx` - Improved useEffect logic
- ✅ `frontend/app/student/(tabs)/profile.tsx` - Added logging
- ✅ `frontend/app/admin/dashboard.tsx` - Added logging
- ✅ `frontend/app/organizer/dashboard.tsx` - Added logging

## Next Steps After Testing

If logout works:
1. ✅ Auth system is complete and functional
2. Test other features (create events, register for events, etc.)
3. Ready for production deployment

If there are still issues:
1. Check browser console for error messages
2. Look for logs in the pattern `[ComponentName]` 
3. Report the specific logs that appear during logout
