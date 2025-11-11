#!/usr/bin/env python3
"""
Integration test script for Step 5.3: ChatService API Integration
Tests the chat endpoint with actual database and agent integration.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory
os.chdir(backend_dir)

import requests
import json
from typing import Dict, Any, Optional

# API base URL
BASE_URL = "http://127.0.0.1:8000/api"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status}: {name}")
    if details:
        print(f"    {Colors.BLUE}→{Colors.RESET} {details}")
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append(f"{name}: {details}")


def make_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
    """Make HTTP request and return response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=60)  # Longer timeout for agent processing
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return None
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
            "headers": dict(response.headers)
        }
    except requests.exceptions.ConnectionError:
        return {"error": "Connection refused - is the server running?"}
    except Exception as e:
        return {"error": str(e)}


def setup_test_data():
    """Set up test data (user, profile, session)."""
    print_header("SETTING UP TEST DATA")
    
    # Create user
    user_data = {
        "email": f"test_chatservice_{os.getpid()}@example.com",
        "username": f"testuser_chatservice_{os.getpid()}"
    }
    result = make_request("POST", "/users", data=user_data)
    
    if result and "error" not in result and result["status_code"] == 201:
        user_id = result["data"]["id"]
        print_test("Created test user", True, f"User ID: {user_id}")
        
        # Create memory profile
        profile_data = {
            "name": "Test Profile",
            "description": "Test profile for ChatService",
            "system_prompt": "You are a helpful assistant."
        }
        result = make_request("POST", f"/users/{user_id}/profiles", data=profile_data)
        
        if result and "error" not in result and result["status_code"] == 201:
            profile_id = result["data"]["id"]
            print_test("Created test profile", True, f"Profile ID: {profile_id}")
            
            # Create session
            session_data = {
                "memory_profile_id": profile_id,
                "privacy_mode": "normal"
            }
            result = make_request("POST", f"/users/{user_id}/sessions", data=session_data)
            
            if result and "error" not in result and result["status_code"] == 201:
                session_id = result["data"]["id"]
                print_test("Created test session", True, f"Session ID: {session_id}")
                return user_id, profile_id, session_id
    
    print_test("Setup test data", False, "Failed to create test data")
    return None, None, None


def test_chat_endpoint_with_chatservice():
    """Test chat endpoint uses ChatService."""
    print_header("TESTING CHAT ENDPOINT WITH CHATSERVICE")
    
    user_id, profile_id, session_id = setup_test_data()
    
    if not session_id:
        print_test("Chat endpoint test", False, "Cannot test without session")
        return
    
    # Test sending a message
    print("\n1. Testing POST /api/chat/message")
    message_data = {
        "session_id": session_id,
        "message": "Hello! My name is Alice and I love Python programming."
    }
    
    result = make_request("POST", "/chat/message", data=message_data)
    
    if result and "error" not in result:
        if result["status_code"] == 200:
            response_data = result["data"]
            
            # Check response structure
            checks = [
                ("message" in response_data, "Response contains message"),
                ("memories_used" in response_data, "Response contains memories_used"),
                ("new_memories_created" in response_data, "Response contains new_memories_created"),
                ("warnings" in response_data, "Response contains warnings"),
                ("metadata" in response_data, "Response contains metadata"),
                (isinstance(response_data["message"], str), "Message is a string"),
                (isinstance(response_data["memories_used"], int), "memories_used is an integer"),
                (isinstance(response_data["new_memories_created"], int), "new_memories_created is an integer"),
                (isinstance(response_data["warnings"], list), "warnings is a list"),
                (isinstance(response_data["metadata"], dict), "metadata is a dictionary"),
            ]
            
            all_passed = True
            for check, description in checks:
                if not check:
                    print_test(description, False)
                    all_passed = False
                else:
                    print_test(description, True)
            
            if all_passed:
                print_test("POST /api/chat/message - Response structure", True)
            else:
                print_test("POST /api/chat/message - Response structure", False)
            
            # Check metadata structure
            if "metadata" in response_data:
                metadata = response_data["metadata"]
                metadata_checks = [
                    ("tokens_used" in metadata, "Metadata contains tokens_used"),
                    ("execution_time_ms" in metadata, "Metadata contains execution_time_ms"),
                    ("agents_executed" in metadata, "Metadata contains agents_executed"),
                    ("privacy_mode" in metadata, "Metadata contains privacy_mode"),
                ]
                
                for check, description in metadata_checks:
                    if check:
                        print_test(description, True)
                    else:
                        print_test(description, False)
            
            # Verify messages were saved
            print("\n2. Testing GET /api/sessions/{session_id}/messages")
            result2 = make_request("GET", f"/sessions/{session_id}/messages")
            
            if result2 and "error" not in result2 and result2["status_code"] == 200:
                messages = result2["data"]
                if len(messages) >= 2:  # User message + assistant response
                    print_test("Messages saved to database", True, f"Found {len(messages)} messages")
                else:
                    print_test("Messages saved to database", False, f"Expected at least 2, got {len(messages)}")
            
            # Test second message to verify memory context
            print("\n3. Testing memory context in second message")
            message_data2 = {
                "session_id": session_id,
                "message": "What programming language did I mention I love?"
            }
            
            result3 = make_request("POST", "/chat/message", data=message_data2)
            
            if result3 and "error" not in result3 and result3["status_code"] == 200:
                response_data3 = result3["data"]
                # The response should reference Python if memory is working
                if "Python" in response_data3["message"] or response_data3["memories_used"] > 0:
                    print_test("Memory context used in conversation", True)
                else:
                    print_test("Memory context used in conversation", False, "Memory may not be working")
            
        else:
            print_test("POST /api/chat/message", False, f"Status code: {result['status_code']}")
    else:
        error_msg = result.get("error", "Unknown error") if result else "No response"
        print_test("POST /api/chat/message", False, error_msg)


def test_privacy_modes():
    """Test privacy modes with ChatService."""
    print_header("TESTING PRIVACY MODES")
    
    user_id, profile_id, session_id = setup_test_data()
    
    if not session_id:
        print_test("Privacy mode test", False, "Cannot test without session")
        return
    
    # Test incognito mode
    print("\n1. Testing incognito mode")
    session_data = {
        "memory_profile_id": profile_id,
        "privacy_mode": "incognito"
    }
    result = make_request("POST", f"/users/{user_id}/sessions", data=session_data)
    
    if result and "error" not in result and result["status_code"] == 201:
        incognito_session_id = result["data"]["id"]
        
        message_data = {
            "session_id": incognito_session_id,
            "message": "My favorite color is blue."
        }
        
        result2 = make_request("POST", "/chat/message", data=message_data)
        
        if result2 and "error" not in result2 and result2["status_code"] == 200:
            response_data = result2["data"]
            if response_data["new_memories_created"] == 0:
                print_test("Incognito mode prevents memory creation", True)
            else:
                print_test("Incognito mode prevents memory creation", False, 
                          f"Created {response_data['new_memories_created']} memories")
    
    # Test pause_memory mode
    print("\n2. Testing pause_memory mode")
    session_data = {
        "memory_profile_id": profile_id,
        "privacy_mode": "pause_memory"
    }
    result = make_request("POST", f"/users/{user_id}/sessions", data=session_data)
    
    if result and "error" not in result and result["status_code"] == 201:
        pause_session_id = result["data"]["id"]
        
        message_data = {
            "session_id": pause_session_id,
            "message": "I like to read books."
        }
        
        result2 = make_request("POST", "/chat/message", data=message_data)
        
        if result2 and "error" not in result2 and result2["status_code"] == 200:
            response_data = result2["data"]
            if response_data["new_memories_created"] == 0:
                print_test("Pause memory mode prevents memory creation", True)
            else:
                print_test("Pause memory mode prevents memory creation", False,
                          f"Created {response_data['new_memories_created']} memories")


def test_error_handling():
    """Test error handling in chat endpoint."""
    print_header("TESTING ERROR HANDLING")
    
    # Test invalid session
    print("\n1. Testing invalid session ID")
    message_data = {
        "session_id": 99999,
        "message": "Hello"
    }
    result = make_request("POST", "/chat/message", data=message_data)
    
    if result and "error" not in result:
        if result["status_code"] == 404:
            print_test("Invalid session returns 404", True)
        else:
            print_test("Invalid session returns 404", False, f"Got {result['status_code']}")
    
    # Test empty message
    user_id, profile_id, session_id = setup_test_data()
    if session_id:
        print("\n2. Testing empty message")
        message_data = {
            "session_id": session_id,
            "message": ""
        }
        result = make_request("POST", "/chat/message", data=message_data)
        
        if result and "error" not in result:
            if result["status_code"] == 422:  # Validation error
                print_test("Empty message returns validation error", True)
            else:
                print_test("Empty message returns validation error", False, f"Got {result['status_code']}")


def main():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'CHATSERVICE INTEGRATION TEST - STEP 5.3'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Note: This test requires the API server to be running.{Colors.RESET}")
    print(f"{Colors.YELLOW}Start the server with: python main.py{Colors.RESET}\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/users", timeout=5)
        if response.status_code not in [200, 404]:
            print(f"{Colors.RED}Server may not be running or accessible.{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}Cannot connect to server. Please start the API server first.{Colors.RESET}\n")
        return 1
    
    # Run tests
    test_chat_endpoint_with_chatservice()
    test_privacy_modes()
    test_error_handling()
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"  Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"  {Colors.GREEN}Passed: {test_results['passed']}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {test_results['failed']}{Colors.RESET}")
    
    if test_results["errors"]:
        print(f"\n{Colors.RED}Errors:{Colors.RESET}")
        for error in test_results["errors"]:
            print(f"  - {error}")
    
    if test_results["failed"] == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}✗ SOME TESTS FAILED{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

