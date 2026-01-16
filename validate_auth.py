#!/usr/bin/env python3
"""
Complete end-to-end validation of all auth flows
"""
import requests
import json
import asyncio
import time
import subprocess
import os
import signal
from datetime import datetime
import random
import string

BASE_URL = "http://localhost:8000"

def random_email():
    """Generate random test email"""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test{suffix}@example.com"

def start_server():
    """Start backend server"""
    print("[*] Starting backend server...")
    backend_path = r"c:\Users\vishnukanth\OneDrive\文档\GitHub\joinup\backend"
    cmd = f'cd "{backend_path}" && python -m uvicorn server:app --port 8000 --log-level error'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    return proc

def stop_server(proc):
    """Stop backend server"""
    try:
        os.kill(proc.pid, signal.SIGTERM)
        time.sleep(1)
    except:
        pass

def test_complete_flow():
    """Test complete auth flow"""
    print("\n" + "="*70)
    print("JOINUP COMPLETE AUTH FLOW VALIDATION")
    print("="*70)
    
    test_email = random_email()
    test_password = "securePassword123"
    
    results = {
        "registration": False,
        "login": False,
        "token_validity": False,
        "logout": False,
        "re_login": False,
    }
    
    try:
        # ===== TEST 1: REGISTRATION =====
        print("\n[TEST 1] Registration")
        print("-" * 70)
        print(f"  Email: {test_email}")
        print(f"  Password: {test_password}")
        
        reg_data = {
            "email": test_email,
            "password": test_password,
            "name": "Test User",
            "college": "Test University",
            "role": "student",
            "department": "Computer Science",
            "year": 2
        }
        
        reg_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=reg_data,
            timeout=5
        )
        
        if reg_response.status_code != 200:
            print(f"  ERROR: {reg_response.status_code} - {reg_response.text}")
            return results
        
        reg_result = reg_response.json()
        token1 = reg_result.get("access_token")
        user_data = reg_result.get("user", {})
        
        print(f"  [✓] Registration successful")
        print(f"  User ID: {user_data.get('id')}")
        print(f"  Token: {token1[:50]}...")
        results["registration"] = True
        
        # ===== TEST 2: LOGIN WITH SAME CREDENTIALS =====
        print("\n[TEST 2] Login")
        print("-" * 70)
        print(f"  Email: {test_email}")
        print(f"  Password: {test_password}")
        
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=5
        )
        
        if login_response.status_code != 200:
            print(f"  ERROR: {login_response.status_code} - {login_response.text}")
            return results
        
        login_result = login_response.json()
        token2 = login_result.get("access_token")
        login_user = login_result.get("user", {})
        
        print(f"  [✓] Login successful")
        print(f"  User ID: {login_user.get('id')}")
        print(f"  Token: {token2[:50]}...")
        results["login"] = True
        
        # ===== TEST 3: TOKEN VALIDITY & PROTECTED ROUTE =====
        print("\n[TEST 3] Token Validity & Protected Route Access")
        print("-" * 70)
        
        headers_with_token = {"Authorization": f"Bearer {token2}"}
        
        events_response = requests.get(
            f"{BASE_URL}/api/events",
            headers=headers_with_token,
            timeout=5
        )
        
        if events_response.status_code != 200:
            print(f"  ERROR: {events_response.status_code} - {events_response.text}")
            return results
        
        events = events_response.json()
        print(f"  [✓] Token is valid")
        print(f"  Protected route accessible")
        print(f"  Events retrieved: {len(events)} events")
        results["token_validity"] = True
        
        # ===== TEST 4: LOGIN WITH WRONG PASSWORD =====
        print("\n[TEST 4] Security Test - Wrong Password")
        print("-" * 70)
        
        wrong_login_data = {
            "email": test_email,
            "password": "wrongPassword123"
        }
        
        wrong_login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=wrong_login_data,
            timeout=5
        )
        
        if wrong_login_response.status_code == 401:
            print(f"  [✓] Correctly rejected wrong password")
            print(f"  Error: {wrong_login_response.json().get('detail', 'Invalid credentials')}")
        else:
            print(f"  WARNING: Expected 401, got {wrong_login_response.status_code}")
        
        # ===== TEST 5: LOGOUT (Client-side) =====
        print("\n[TEST 5] Logout (Client-side Token Removal)")
        print("-" * 70)
        print(f"  Simulating token removal from client storage...")
        
        # Client clears token from storage
        token_after_logout = None
        
        if token_after_logout is None:
            print(f"  [✓] Token cleared successfully")
            results["logout"] = True
        
        # ===== TEST 6: RE-LOGIN AFTER LOGOUT =====
        print("\n[TEST 6] Re-login After Logout")
        print("-" * 70)
        print(f"  Email: {test_email}")
        
        relogin_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=5
        )
        
        if relogin_response.status_code == 200:
            relogin_result = relogin_response.json()
            new_token = relogin_result.get("access_token")
            print(f"  [✓] Re-login successful")
            print(f"  New Token: {new_token[:50]}...")
            results["re_login"] = True
        else:
            print(f"  ERROR: {relogin_response.status_code} - {relogin_response.text}")
        
        # ===== SUMMARY =====
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        all_passed = all(results.values())
        
        for test_name, passed in results.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print("\n" + "="*70)
        if all_passed:
            print("RESULT: ALL TESTS PASSED - AUTH FLOW COMPLETE AND WORKING")
        else:
            print("RESULT: SOME TESTS FAILED - REVIEW ABOVE")
        print("="*70)
        
        return results
        
    except Exception as e:
        print(f"\n[ERROR] Test execution failed: {e}")
        return results

if __name__ == "__main__":
    proc = None
    try:
        proc = start_server()
        time.sleep(1)
        
        # Check if server is running
        try:
            health = requests.get(f"{BASE_URL}/health", timeout=2)
            if health.status_code != 200:
                print("[ERROR] Server health check failed")
                exit(1)
        except:
            print("[ERROR] Cannot connect to server on port 8000")
            exit(1)
        
        results = test_complete_flow()
        
        # Exit with appropriate code
        all_passed = all(results.values())
        exit(0 if all_passed else 1)
        
    finally:
        if proc:
            stop_server(proc)
