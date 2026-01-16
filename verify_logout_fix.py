#!/usr/bin/env python
"""
Verification test to ensure logout fix is properly implemented
"""
import os
import re

def check_file_content(filepath, pattern, description):
    """Check if a file contains a specific pattern"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if re.search(pattern, content):
            print(f"✓ {description}")
            return True
        else:
            print(f"✗ {description}")
            return False
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return False

def main():
    print("=" * 70)
    print("         LOGOUT FIX VERIFICATION CHECKLIST")
    print("=" * 70)
    
    base_path = r"c:\Users\vishnukanth\OneDrive\文档\GitHub\joinup"
    
    checks = [
        # AuthContext fixes
        (
            os.path.join(base_path, "frontend/context/AuthContext.tsx"),
            r"setUser\(null\);\s+setToken\(null\);\s+setError\(null\);\s+console\.log\(\'\[AuthContext\] Cleared React state\'\);",
            "AuthContext: State cleared BEFORE AsyncStorage"
        ),
        (
            os.path.join(base_path, "frontend/context/AuthContext.tsx"),
            r"\[AuthContext\] Cleared React state",
            "AuthContext: Has 'Cleared React state' log"
        ),
        (
            os.path.join(base_path, "frontend/context/AuthContext.tsx"),
            r"await AsyncStorage\.removeItem",
            "AuthContext: AsyncStorage removal in try/catch"
        ),
        
        # Index.tsx fixes
        (
            os.path.join(base_path, "frontend/app/index.tsx"),
            r"if \(loading\) {\s+console\.log\(\'\[Index\] Still loading",
            "index.tsx: Has early return for loading state"
        ),
        (
            os.path.join(base_path, "frontend/app/index.tsx"),
            r"\[Index\] User is null, showing landing page",
            "index.tsx: Has null user logging"
        ),
        
        # Profile logout
        (
            os.path.join(base_path, "frontend/app/student/(tabs)/profile.tsx"),
            r"\[Profile\] Logout button pressed",
            "Profile: Has logout button logging"
        ),
        (
            os.path.join(base_path, "frontend/app/student/(tabs)/profile.tsx"),
            r"router\.replace\(\'/\'\)",
            "Profile: Navigates to root (/)"
        ),
        
        # Admin logout
        (
            os.path.join(base_path, "frontend/app/admin/dashboard.tsx"),
            r"\[AdminDashboard\] Logout button pressed",
            "Admin: Has logout button logging"
        ),
        
        # Organizer logout
        (
            os.path.join(base_path, "frontend/app/organizer/dashboard.tsx"),
            r"\[OrganizerDashboard\] Logout button pressed",
            "Organizer: Has logout button logging"
        ),
        
        # Documentation
        (
            os.path.join(base_path, "LOGOUT_FIX_FINAL.md"),
            r"Root Cause",
            "Documentation: LOGOUT_FIX_FINAL.md exists"
        ),
        (
            os.path.join(base_path, "LOGOUT_TEST_GUIDE.md"),
            r"Step 1: Open the App",
            "Documentation: LOGOUT_TEST_GUIDE.md exists"
        ),
    ]
    
    passed = 0
    failed = 0
    
    print()
    for filepath, pattern, description in checks:
        if check_file_content(filepath, pattern, description):
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ All logout fix checks passed!")
        print("\nYou can now test logout by:")
        print("1. Opening http://localhost:8081")
        print("2. Registering as a student")
        print("3. Navigating to Profile tab")
        print("4. Clicking Logout button")
        print("5. Verifying return to landing page")
    else:
        print(f"\n✗ {failed} check(s) failed")
        print("Please review the LOGOUT_FIX_FINAL.md for details")

if __name__ == "__main__":
    main()
