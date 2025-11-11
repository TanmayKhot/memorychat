#!/usr/bin/env python3
"""
Test script for Step 6.3 - Frontend Functionality
Tests state management, chat flow, and profile/session management
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 30

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_test(name: str, passed: bool, details: str = ""):
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} {name}")
    if details and not passed:
        print(f"      {Colors.RED}Error: {details}{Colors.RESET}")

def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200 and response.json().get("status") == "healthy"
    except:
        return False

def api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API request"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
        else:
            error_detail = str(e)
        raise Exception(error_detail)

def test_state_management():
    """Test 1: State Management"""
    print_header("TEST 1: State Management")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1.1: Create user and verify state
    tests_total += 1
    try:
        user_data = {
            "email": f"test_state_{int(time.time())}@example.com",
            "username": f"testuser_state_{int(time.time())}"
        }
        user = api_request("POST", "/api/users", user_data)
        assert user.get("id") is not None
        assert user.get("email") == user_data["email"]
        assert user.get("username") == user_data["username"]
        print_test("1.1: Create user and store state", True)
        tests_passed += 1
        user_id = user["id"]
    except Exception as e:
        print_test("1.1: Create user and store state", False, str(e))
        return False
    
    # Test 1.2: Create profile and verify state
    tests_total += 1
    try:
        profile_data = {
            "name": f"Test Profile {int(time.time())}",
            "description": "Test profile for state management"
        }
        profile = api_request("POST", f"/api/users/{user_id}/profiles", profile_data)
        assert profile.get("id") is not None
        assert profile.get("name") == profile_data["name"]
        print_test("1.2: Create profile and store state", True)
        tests_passed += 1
        profile_id = profile["id"]
    except Exception as e:
        print_test("1.2: Create profile and store state", False, str(e))
        return False
    
    # Test 1.3: Create session and verify state
    tests_total += 1
    try:
        session_data = {
            "memory_profile_id": profile_id,
            "privacy_mode": "normal"
        }
        session = api_request("POST", f"/api/users/{user_id}/sessions", session_data)
        assert session.get("id") is not None
        assert session.get("privacy_mode") == "normal"
        print_test("1.3: Create session and store state", True)
        tests_passed += 1
        session_id = session["id"]
    except Exception as e:
        print_test("1.3: Create session and store state", False, str(e))
        return False
    
    # Test 1.4: Retrieve state
    tests_total += 1
    try:
        retrieved_user = api_request("GET", f"/api/users/{user_id}")
        retrieved_profile = api_request("GET", f"/api/profiles/{profile_id}")
        retrieved_session = api_request("GET", f"/api/sessions/{session_id}")
        
        assert retrieved_user["id"] == user_id
        assert retrieved_profile["id"] == profile_id
        assert retrieved_session["id"] == session_id
        print_test("1.4: Retrieve stored state", True)
        tests_passed += 1
    except Exception as e:
        print_test("1.4: Retrieve stored state", False, str(e))
        return False
    
    print(f"\n  {Colors.BOLD}State Management: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total, user_id, profile_id, session_id

def test_chat_flow(user_id: int, profile_id: int, session_id: int):
    """Test 2: Chat Flow"""
    print_header("TEST 2: Chat Flow")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 2.1: Send message
    tests_total += 1
    try:
        message_data = {
            "session_id": session_id,
            "message": "Hello, this is a test message for chat flow"
        }
        response = api_request("POST", "/api/chat/message", message_data)
        assert "message" in response
        assert isinstance(response.get("memories_used"), int)
        assert isinstance(response.get("new_memories_created"), int)
        print_test("2.1: Send message to API", True)
        tests_passed += 1
    except Exception as e:
        print_test("2.1: Send message to API", False, str(e))
        return False
    
    # Test 2.2: Verify message displayed (check messages endpoint)
    tests_total += 1
    try:
        time.sleep(1)  # Wait for message to be saved
        messages = api_request("GET", f"/api/sessions/{session_id}/messages")
        assert isinstance(messages, list)
        assert len(messages) >= 2  # User message + assistant response
        user_messages = [m for m in messages if m.get("role") == "user"]
        assistant_messages = [m for m in messages if m.get("role") == "assistant"]
        assert len(user_messages) > 0
        assert len(assistant_messages) > 0
        print_test("2.2: Verify messages displayed in UI", True)
        tests_passed += 1
    except Exception as e:
        print_test("2.2: Verify messages displayed in UI", False, str(e))
        return False
    
    # Test 2.3: Send multiple messages
    tests_total += 1
    try:
        for i in range(2):
            message_data = {
                "session_id": session_id,
                "message": f"Test message {i+1}"
            }
            api_request("POST", "/api/chat/message", message_data)
        time.sleep(1)
        messages = api_request("GET", f"/api/sessions/{session_id}/messages")
        assert len(messages) >= 6  # 3 user + 3 assistant messages
        print_test("2.3: Send multiple messages", True)
        tests_passed += 1
    except Exception as e:
        print_test("2.3: Send multiple messages", False, str(e))
        return False
    
    # Test 2.4: Error handling
    tests_total += 1
    try:
        try:
            api_request("POST", "/api/chat/message", {
                "session_id": 99999,
                "message": "This should fail"
            })
            print_test("2.4: Error handling", False, "Should have raised error")
            return False
        except Exception as e:
            # Expected to fail
            print_test("2.4: Error handling", True)
            tests_passed += 1
    except Exception as e:
        print_test("2.4: Error handling", False, str(e))
        return False
    
    print(f"\n  {Colors.BOLD}Chat Flow: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def test_profile_session_management(user_id: int):
    """Test 3: Profile/Session Management CRUD"""
    print_header("TEST 3: Profile/Session Management CRUD")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 3.1: Create profile
    tests_total += 1
    try:
        profile_data = {
            "name": f"CRUD Profile {int(time.time())}",
            "description": "Test profile for CRUD operations"
        }
        profile = api_request("POST", f"/api/users/{user_id}/profiles", profile_data)
        profile_id = profile["id"]
        assert profile.get("name") == profile_data["name"]
        print_test("3.1: Create profile (CREATE)", True)
        tests_passed += 1
    except Exception as e:
        print_test("3.1: Create profile (CREATE)", False, str(e))
        return False
    
    # Test 3.2: Read profile
    tests_total += 1
    try:
        retrieved_profile = api_request("GET", f"/api/profiles/{profile_id}")
        assert retrieved_profile["id"] == profile_id
        print_test("3.2: Read profile (READ)", True)
        tests_passed += 1
    except Exception as e:
        print_test("3.2: Read profile (READ)", False, str(e))
        return False
    
    # Test 3.3: Update profile
    tests_total += 1
    try:
        updated_name = f"Updated Profile {int(time.time())}"
        update_data = {"name": updated_name}
        updated_profile = api_request("PUT", f"/api/profiles/{profile_id}", update_data)
        assert updated_profile["name"] == updated_name
        print_test("3.3: Update profile (UPDATE)", True)
        tests_passed += 1
    except Exception as e:
        print_test("3.3: Update profile (UPDATE)", False, str(e))
        return False
    
    # Test 3.4: Create session
    tests_total += 1
    try:
        session_data = {
            "memory_profile_id": profile_id,
            "privacy_mode": "normal"
        }
        session = api_request("POST", f"/api/users/{user_id}/sessions", session_data)
        session_id = session["id"]
        assert session.get("privacy_mode") == "normal"
        print_test("3.4: Create session (CREATE)", True)
        tests_passed += 1
    except Exception as e:
        print_test("3.4: Create session (CREATE)", False, str(e))
        return False
    
    # Test 3.5: Read session
    tests_total += 1
    try:
        retrieved_session = api_request("GET", f"/api/sessions/{session_id}")
        assert retrieved_session["id"] == session_id
        print_test("3.5: Read session (READ)", True)
        tests_passed += 1
    except Exception as e:
        print_test("3.5: Read session (READ)", False, str(e))
        return False
    
    # Test 3.6: Update session privacy mode
    tests_total += 1
    try:
        update_data = {"privacy_mode": "incognito"}
        updated_session = api_request("PUT", f"/api/sessions/{session_id}/privacy-mode", update_data)
        assert updated_session["privacy_mode"] == "incognito"
        print_test("3.6: Update session (UPDATE)", True)
        tests_passed += 1
    except Exception as e:
        print_test("3.6: Update session (UPDATE)", False, str(e))
        return False
    
    # Test 3.7: Delete session
    tests_total += 1
    try:
        api_request("DELETE", f"/api/sessions/{session_id}")
        # Verify deletion
        try:
            api_request("GET", f"/api/sessions/{session_id}")
            print_test("3.7: Delete session (DELETE)", False, "Session still exists")
            return False
        except:
            print_test("3.7: Delete session (DELETE)", True)
            tests_passed += 1
    except Exception as e:
        print_test("3.7: Delete session (DELETE)", False, str(e))
        return False
    
    # Test 3.8: Delete profile (need to create another profile first)
    tests_total += 1
    try:
        # Create another profile since we can't delete the only one
        profile2_data = {
            "name": f"Second Profile {int(time.time())}",
            "description": "Second profile for deletion test"
        }
        profile2 = api_request("POST", f"/api/users/{user_id}/profiles", profile2_data)
        profile2_id = profile2["id"]
        
        # Delete it
        api_request("DELETE", f"/api/profiles/{profile2_id}")
        # Verify deletion
        try:
            api_request("GET", f"/api/profiles/{profile2_id}")
            print_test("3.8: Delete profile (DELETE)", False, "Profile still exists")
            return False
        except:
            print_test("3.8: Delete profile (DELETE)", True)
            tests_passed += 1
    except Exception as e:
        print_test("3.8: Delete profile (DELETE)", False, str(e))
        return False
    
    print(f"\n  {Colors.BOLD}CRUD Operations: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def main():
    """Run all tests"""
    print_header("STEP 6.3: Frontend Functionality Tests")
    
    # Check API health
    print(f"\n{Colors.YELLOW}Checking API connection...{Colors.RESET}")
    if not check_api_health():
        print(f"{Colors.RED}✗ API is not running at {API_BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please start the backend server first:{Colors.RESET}")
        print(f"  cd memorychat/backend")
        print(f"  python main.py")
        sys.exit(1)
    print(f"{Colors.GREEN}✓ API is running{Colors.RESET}\n")
    
    all_passed = True
    
    # Test 1: State Management
    result = test_state_management()
    if isinstance(result, tuple):
        state_passed, user_id, profile_id, session_id = result
        all_passed = all_passed and state_passed
    else:
        print(f"{Colors.RED}State management tests failed. Cannot continue.{Colors.RESET}")
        sys.exit(1)
    
    # Test 2: Chat Flow
    chat_passed = test_chat_flow(user_id, profile_id, session_id)
    all_passed = all_passed and chat_passed
    
    # Test 3: Profile/Session Management CRUD
    crud_passed = test_profile_session_management(user_id)
    all_passed = all_passed and crud_passed
    
    # Final summary
    print_header("TEST SUMMARY")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.RESET}")
        print(f"\n{Colors.GREEN}Step 6.3 implementation is working correctly!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"\n{Colors.RED}Please review the test results above.{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()

