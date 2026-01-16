# LOGOUT TEST - Step by Step Instructions

## Prerequisites
✅ Backend running on http://localhost:8080
✅ Frontend running on http://localhost:8081
✅ Both servers connected

## Test Procedure

### Part 1: Register a Test Student
1. Go to http://localhost:8081 in your browser
2. Click on the **Student** role card (blue card on the left)
3. You'll see the role selection page, click Student to continue
4. Fill in the registration form:
   - **Email:** test@example.com
   - **Password:** Test123!
   - **Name:** Test Student
   - **College:** Test College
   - **Department:** Computer Science
   - **Year:** 3
5. Click **Register** button
6. You should now be logged in and see the student dashboard with tabs

### Part 2: Logout Test
1. Click the **Profile** tab (should be the rightmost tab at the bottom)
2. You should see your profile information and a Logout button (top right icon - log out)
3. Click the **Logout button** (the icon on the top right)
4. An alert dialog will appear: "Are you sure you want to logout?"
5. Click **Logout** in the alert (red button)
6. The alert should close

### Part 3: Verification
**Expected outcome:**
- Alert disappears
- You are redirected to the **landing page**
- You should see "Welcome! Choose Your Role"
- Three role cards (Student, University/Club, Admin) should be visible
- You should be able to start fresh or choose a different role

**If this works:** ✅ Logout is FIXED!

### Part 4: Check Console Logs
This is important for verifying the fix worked correctly.

**On Web (Chrome/Firefox):**
1. Press `F12` to open Developer Tools
2. Click on the **Console** tab
3. During logout, scroll up and look for logs like:
   ```
   [Profile] Logout button pressed
   [AuthContext] Starting logout...
   [AuthContext] Cleared React state
   [AuthContext] Logout complete
   [Profile] Navigation command sent
   [Index] User is null, showing landing page
   ```

These logs prove the fix is working!

### Part 5: Test Other Roles (Optional)
Repeat the test with other roles:

**As Admin:**
1. Go to http://localhost:8081
2. Click **Admin** role card
3. Register and login as admin
4. Click Logout
5. Verify return to landing page

**As Organizer:**
1. Go to http://localhost:8081
2. Click **University/Club** role card (organizer)
3. Register and login as organizer
4. Click Logout (top right corner)
5. Verify return to landing page

## Troubleshooting

### Issue: Logout doesn't navigate back
- Check browser console for errors
- Look for `[Index]` logs - should show "User is null"
- Make sure backend is running

### Issue: No console logs appearing
- Open Developer Tools (F12)
- Go to Console tab
- Try logout again
- Logs should appear in real-time

### Issue: Alert doesn't close
- Click the X button if one appears
- Try refreshing the page
- Check that AsyncStorage clearing didn't fail

### Issue: Can't register
- Check backend is running on :8080
- Frontend should show `API_URL: http://localhost:8080` in console
- Try a different email address (must be unique)

## Expected Console Flow
```
API_URL: http://localhost:8080  ← Backend connection confirmed

[Index] useEffect triggered - user: test@example.com loading: false
[Index] User is logged in, navigating to: /student/(tabs) email: test@example.com
← User logged in, navigating to student dashboard

[Profile] Logout button pressed  ← User clicked logout
[AuthContext] Starting logout...
[AuthContext] Current user before logout: test@example.com
[AuthContext] Current token before logout: exists
[AuthContext] Cleared React state
[AuthContext] Cleared AsyncStorage
[AuthContext] Logout complete
[Profile] Logout function completed, navigating to home
[Profile] Navigation command sent  ← Navigation happening

[Index] useEffect triggered - user: null loading: false  ← State changed!
[Index] User is null, showing landing page (this is correct after logout)  ← SUCCESS!
```

## Success Criteria
- ✓ Logout button is clickable
- ✓ Alert confirmation appears
- ✓ Alert closes after confirming
- ✓ App navigates to landing page
- ✓ "Choose Your Role" page is displayed
- ✓ Console shows the expected logs
- ✓ Can register and login again after logout

## Additional Testing

### Test Multiple Logouts
1. Login as student
2. Logout (should work)
3. Login again
4. Logout again (should work)
5. Repeat 3-4 times to ensure consistency

### Test Role Switching
1. Login as student
2. Logout
3. Login as admin
4. Logout
5. Login as organizer
6. Logout
- All should work without issues

### Test on Different Browsers
- Chrome/Chromium ✓
- Firefox ✓
- Safari (if available) ✓
- Mobile browser (if available) ✓

## When to Report Success
After completing all tests:
1. Logout works on all three roles
2. Console logs show correct sequence
3. App returns to landing page
4. Can login again after logout
5. Multiple logout/login cycles work

## Files Modified for This Fix
1. `frontend/context/AuthContext.tsx`
   - Changed logout order: state first, storage second
   
2. `frontend/app/index.tsx`
   - Improved useEffect logic for proper redirects
   
3. `frontend/app/student/(tabs)/profile.tsx`
   - Added console logging for debugging
   
4. `frontend/app/admin/dashboard.tsx`
   - Added console logging for debugging
   
5. `frontend/app/organizer/dashboard.tsx`
   - Added console logging for debugging

## Final Notes
- The fix ensures React state is updated immediately
- AsyncStorage clearing happens in background (non-blocking)
- This prevents the race condition that was causing logout failures
- All three user roles now have consistent logout behavior
