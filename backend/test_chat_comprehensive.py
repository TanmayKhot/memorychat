"""
Comprehensive tests for Checkpoint 3.12 - Chat API.

Tests both chat endpoints:
- POST /chat/{session_id} - Standard chat
- POST /chat/{session_id}/stream - Streaming chat

Run with: python test_chat_comprehensive.py
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
import json


# =============================================================================
# Configuration
# =============================================================================
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test user credentials (you may need to adjust these)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"


# =============================================================================
# Helper Functions
# =============================================================================
def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_test(test_name: str):
    """Print a test name."""
    print(f"\n▶ {test_name}")


def print_result(success: bool, message: str, data: Any = None):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status}: {message}")
    if data:
        print(f"  Data: {data}")


async def login() -> Optional[str]:
    """Login and get access token."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print_result(True, "Login successful")
                return token
            else:
                print_result(False, f"Login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print_result(False, f"Login error: {e}")
            return None


async def create_test_session(token: str) -> Optional[str]:
    """Create a test chat session."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/sessions",
                headers={"Authorization": f"Bearer {token}"},
                json={"privacy_mode": "normal"}
            )
            if response.status_code == 201:
                data = response.json()
                session_id = data.get("id")
                print_result(True, f"Test session created: {session_id[:8]}...")
                return session_id
            else:
                print_result(False, f"Failed to create session: {response.status_code}")
                return None
        except Exception as e:
            print_result(False, f"Error creating session: {e}")
            return None


# =============================================================================
# Test Functions
# =============================================================================
async def test_send_basic_message(token: str, session_id: str):
    """Test sending a basic message and receiving response."""
    print_test("Test 1: Send basic message")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_BASE}/chat/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "message": "Hello! What is 2+2?",
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, "Message sent and response received", {
                    "success": data.get("success"),
                    "content_preview": data.get("content", "")[:100] + "...",
                    "session_id": data.get("session_id", "")[:8] + "...",
                    "privacy_mode": data.get("privacy_mode"),
                    "memories_used": data.get("memories_used"),
                    "memories_extracted": data.get("memories_extracted")
                })
                return True
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


async def test_send_message_with_context(token: str, session_id: str):
    """Test sending multiple messages to build context."""
    print_test("Test 2: Send messages with conversation context")
    
    messages = [
        "My name is Alice.",
        "I love programming in Python.",
        "What's my name?",
        "What programming language do I like?"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, message in enumerate(messages, 1):
            try:
                print(f"  Sending message {i}/{len(messages)}: '{message}'")
                response = await client.post(
                    f"{API_BASE}/chat/{session_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"message": message, "stream": False}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", "")
                    print(f"    Response: {content[:80]}{'...' if len(content) > 80 else ''}")
                else:
                    print_result(False, f"Message {i} failed with status {response.status_code}")
                    return False
                    
            except Exception as e:
                print_result(False, f"Error on message {i}: {e}")
                return False
        
        print_result(True, "All context messages processed successfully")
        return True


async def test_incognito_mode(token: str):
    """Test chat in incognito mode (no memories)."""
    print_test("Test 3: Chat in incognito mode")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Create incognito session
            response = await client.post(
                f"{API_BASE}/sessions",
                headers={"Authorization": f"Bearer {token}"},
                json={"privacy_mode": "incognito"}
            )
            
            if response.status_code != 201:
                print_result(False, "Failed to create incognito session")
                return False
            
            incognito_session_id = response.json().get("id")
            
            # Send message in incognito
            response = await client.post(
                f"{API_BASE}/chat/{incognito_session_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "This is a private message", "stream": False}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("privacy_mode") == "incognito":
                    if data.get("memories_extracted") == False:
                        print_result(True, "Incognito mode working correctly", {
                            "memories_used": data.get("memories_used"),
                            "memories_extracted": data.get("memories_extracted")
                        })
                        return True
                    else:
                        print_result(False, "Memories were extracted in incognito mode!")
                        return False
                else:
                    print_result(False, f"Wrong privacy mode: {data.get('privacy_mode')}")
                    return False
            else:
                print_result(False, f"Failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


async def test_streaming_response(token: str, session_id: str):
    """Test streaming chat response."""
    print_test("Test 4: Streaming response")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print("  Sending streaming request...")
            async with client.stream(
                "POST",
                f"{API_BASE}/chat/{session_id}/stream",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "Tell me a short joke", "stream": True}
            ) as response:
                
                if response.status_code != 200:
                    print_result(False, f"Failed with status {response.status_code}")
                    return False
                
                chunks_received = 0
                content_received = ""
                
                print("  Receiving chunks:")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str == "[DONE]":
                            print("  Stream completed")
                            break
                        
                        try:
                            chunk = json.loads(data_str)
                            chunks_received += 1
                            
                            if chunk.get("type") == "content":
                                content = chunk.get("content", "")
                                content_received += content
                                print(f"    Chunk {chunks_received}: {content}", end="", flush=True)
                            elif chunk.get("type") == "metadata":
                                print(f"    Metadata: {chunk}")
                            elif chunk.get("type") == "complete":
                                print(f"\n    Complete: {chunk}")
                            elif chunk.get("type") == "error":
                                print_result(False, f"Stream error: {chunk.get('error')}")
                                return False
                        except json.JSONDecodeError as e:
                            print(f"\n    Warning: Failed to parse chunk: {e}")
                
                print()
                if chunks_received > 0:
                    print_result(True, f"Streaming successful ({chunks_received} chunks)", {
                        "content_length": len(content_received),
                        "content_preview": content_received[:100] + "..."
                    })
                    return True
                else:
                    print_result(False, "No chunks received")
                    return False
                    
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


async def test_error_invalid_session(token: str):
    """Test sending message to non-existent session."""
    print_test("Test 5: Error handling - Invalid session")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_BASE}/chat/00000000-0000-0000-0000-000000000000",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "Test", "stream": False}
            )
            
            if response.status_code == 404:
                print_result(True, "Correctly returns 404 for invalid session")
                return True
            else:
                print_result(False, f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


async def test_error_unauthenticated(session_id: str):
    """Test sending message without authentication."""
    print_test("Test 6: Error handling - No authentication")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_BASE}/chat/{session_id}",
                json={"message": "Test", "stream": False}
            )
            
            if response.status_code == 403:
                print_result(True, "Correctly returns 403 for unauthenticated request")
                return True
            else:
                print_result(False, f"Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


async def test_message_persistence(token: str, session_id: str):
    """Test that messages are saved to database."""
    print_test("Test 7: Message persistence")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Send a unique message
            unique_msg = "Test message for persistence check 12345"
            
            response = await client.post(
                f"{API_BASE}/chat/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": unique_msg, "stream": False}
            )
            
            if response.status_code != 200:
                print_result(False, f"Failed to send message: {response.status_code}")
                return False
            
            # Retrieve messages from session
            response = await client.get(
                f"{API_BASE}/sessions/{session_id}/messages",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                print_result(False, f"Failed to retrieve messages: {response.status_code}")
                return False
            
            messages = response.json()
            
            # Check if our message is there
            found_user_msg = False
            found_assistant_msg = False
            
            for msg in messages:
                if msg.get("role") == "user" and msg.get("content") == unique_msg:
                    found_user_msg = True
                if msg.get("role") == "assistant" and found_user_msg:
                    found_assistant_msg = True
            
            if found_user_msg and found_assistant_msg:
                print_result(True, "Messages persisted correctly", {
                    "total_messages": len(messages),
                    "user_message_found": found_user_msg,
                    "assistant_message_found": found_assistant_msg
                })
                return True
            else:
                print_result(False, "Messages not found in database")
                return False
                
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


async def test_empty_message_validation(token: str, session_id: str):
    """Test validation for empty messages."""
    print_test("Test 8: Empty message validation")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_BASE}/chat/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "", "stream": False}
            )
            
            if response.status_code == 422:  # Validation error
                print_result(True, "Correctly rejects empty message")
                return True
            else:
                print_result(False, f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


async def test_long_message(token: str, session_id: str):
    """Test handling of long messages."""
    print_test("Test 9: Long message handling")
    
    # Create a reasonably long message (not hitting the limit)
    long_message = "Write a detailed explanation about: " + "test " * 100
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{API_BASE}/chat/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": long_message, "stream": False}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, "Long message processed successfully", {
                    "message_length": len(long_message),
                    "response_length": len(data.get("content", ""))
                })
                return True
            else:
                print_result(False, f"Failed with status {response.status_code}")
                return False
        except Exception as e:
            print_result(False, f"Error: {e}")
            return False


# =============================================================================
# Main Test Runner
# =============================================================================
async def run_all_tests():
    """Run all tests in sequence."""
    print_section("CHECKPOINT 3.12 - COMPREHENSIVE CHAT TESTS")
    
    # Step 1: Login
    print_section("AUTHENTICATION")
    token = await login()
    if not token:
        print("\n❌ Failed to authenticate. Cannot continue tests.")
        print("Please ensure:")
        print(f"  1. Backend server is running at {BASE_URL}")
        print(f"  2. User exists: {TEST_EMAIL}")
        print(f"  3. Password is correct: {TEST_PASSWORD}")
        return
    
    # Step 2: Create test session
    print_section("SETUP - CREATE TEST SESSION")
    session_id = await create_test_session(token)
    if not session_id:
        print("\n❌ Failed to create test session. Cannot continue tests.")
        return
    
    # Step 3: Run chat tests
    print_section("BASIC CHAT TESTS")
    results = []
    
    results.append(await test_send_basic_message(token, session_id))
    results.append(await test_send_message_with_context(token, session_id))
    
    # Step 4: Privacy mode tests
    print_section("PRIVACY MODE TESTS")
    results.append(await test_incognito_mode(token))
    
    # Step 5: Streaming tests
    print_section("STREAMING TESTS")
    results.append(await test_streaming_response(token, session_id))
    
    # Step 6: Error handling tests
    print_section("ERROR HANDLING TESTS")
    results.append(await test_error_invalid_session(token))
    results.append(await test_error_unauthenticated(session_id))
    results.append(await test_empty_message_validation(token, session_id))
    
    # Step 7: Advanced tests
    print_section("ADVANCED TESTS")
    results.append(await test_message_persistence(token, session_id))
    results.append(await test_long_message(token, session_id))
    
    # Summary
    print_section("TEST SUMMARY")
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! Checkpoint 3.12 is working correctly.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Review the results above.")
    
    print("\nCheckpoint 3.12 testing complete.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

