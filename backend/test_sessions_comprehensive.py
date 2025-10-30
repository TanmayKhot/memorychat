"""
Comprehensive tests for Checkpoint 3.11 - Chat Sessions API.

Tests all 6 endpoints with various scenarios including:
- Creating sessions (with/without profiles, different privacy modes)
- Listing sessions (with pagination and filtering)
- Getting specific sessions
- Updating sessions
- Deleting sessions
- Getting session messages

Run with: pytest test_sessions_comprehensive.py -v
"""

import asyncio
import httpx
from typing import Dict, Any, Optional


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


async def get_memory_profiles(token: str) -> list:
    """Get all memory profiles for the user."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/memory-profiles",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                profiles = response.json()
                print_result(True, f"Found {len(profiles)} memory profiles")
                return profiles
            else:
                print_result(False, f"Failed to get profiles: {response.status_code}")
                return []
        except Exception as e:
            print_result(False, f"Error getting profiles: {e}")
            return []


# =============================================================================
# Test Functions
# =============================================================================
async def test_create_session_with_default_profile(token: str) -> Optional[str]:
    """Test creating a session without specifying a profile (uses default)."""
    print_test("Test 1: Create session with default profile")
    
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
                print_result(True, "Session created successfully", {
                    "id": session_id,
                    "privacy_mode": data.get("privacy_mode"),
                    "memory_profile_id": data.get("memory_profile_id"),
                    "message_count": data.get("message_count")
                })
                return session_id
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print_result(False, f"Error: {e}")
            return None


async def test_create_session_with_specific_profile(token: str, profile_id: str) -> Optional[str]:
    """Test creating a session with a specific memory profile."""
    print_test("Test 2: Create session with specific profile")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/sessions",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "memory_profile_id": profile_id,
                    "privacy_mode": "normal"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                session_id = data.get("id")
                print_result(True, "Session created with specific profile", {
                    "id": session_id,
                    "memory_profile_id": data.get("memory_profile_id")
                })
                return session_id
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print_result(False, f"Error: {e}")
            return None


async def test_create_incognito_session(token: str) -> Optional[str]:
    """Test creating an incognito session."""
    print_test("Test 3: Create incognito session")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/sessions",
                headers={"Authorization": f"Bearer {token}"},
                json={"privacy_mode": "incognito"}
            )
            
            if response.status_code == 201:
                data = response.json()
                session_id = data.get("id")
                print_result(True, "Incognito session created", {
                    "id": session_id,
                    "privacy_mode": data.get("privacy_mode")
                })
                return session_id
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print_result(False, f"Error: {e}")
            return None


async def test_create_pause_memories_session(token: str) -> Optional[str]:
    """Test creating a pause_memories session."""
    print_test("Test 4: Create pause_memories session")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/sessions",
                headers={"Authorization": f"Bearer {token}"},
                json={"privacy_mode": "pause_memories"}
            )
            
            if response.status_code == 201:
                data = response.json()
                session_id = data.get("id")
                print_result(True, "Pause memories session created", {
                    "id": session_id,
                    "privacy_mode": data.get("privacy_mode")
                })
                return session_id
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print_result(False, f"Error: {e}")
            return None


async def test_get_all_sessions(token: str) -> int:
    """Test getting all sessions."""
    print_test("Test 5: Get all sessions")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/sessions",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                sessions = response.json()
                print_result(True, f"Retrieved {len(sessions)} sessions")
                for i, session in enumerate(sessions[:3]):  # Show first 3
                    print(f"    Session {i+1}: {session.get('id')[:8]}... "
                          f"[{session.get('privacy_mode')}] "
                          f"({session.get('message_count')} messages)")
                return len(sessions)
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return 0
        except Exception as e:
            print_result(False, f"Error: {e}")
            return 0


async def test_get_sessions_with_pagination(token: str):
    """Test getting sessions with pagination."""
    print_test("Test 6: Get sessions with pagination")
    
    async with httpx.AsyncClient() as client:
        try:
            # Get first 2 sessions
            response = await client.get(
                f"{API_BASE}/sessions?limit=2&offset=0",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                sessions_page1 = response.json()
                print_result(True, f"Page 1: Retrieved {len(sessions_page1)} sessions")
                
                # Get next 2 sessions
                response = await client.get(
                    f"{API_BASE}/sessions?limit=2&offset=2",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    sessions_page2 = response.json()
                    print_result(True, f"Page 2: Retrieved {len(sessions_page2)} sessions")
                else:
                    print_result(False, f"Page 2 failed with status {response.status_code}")
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print_result(False, f"Error: {e}")


async def test_filter_sessions_by_profile(token: str, profile_id: str):
    """Test filtering sessions by memory profile."""
    print_test("Test 7: Filter sessions by memory profile")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/sessions?memory_profile_id={profile_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                sessions = response.json()
                print_result(True, f"Found {len(sessions)} sessions for profile")
                # Verify all have the correct profile
                all_match = all(s.get("memory_profile_id") == profile_id for s in sessions)
                if all_match:
                    print_result(True, "All sessions have the correct profile ID")
                else:
                    print_result(False, "Some sessions have incorrect profile ID")
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print_result(False, f"Error: {e}")


async def test_get_specific_session(token: str, session_id: str):
    """Test getting a specific session by ID."""
    print_test("Test 8: Get specific session")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/sessions/{session_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                session = response.json()
                print_result(True, "Session retrieved", {
                    "id": session.get("id")[:8] + "...",
                    "privacy_mode": session.get("privacy_mode"),
                    "message_count": session.get("message_count")
                })
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print_result(False, f"Error: {e}")


async def test_update_session_privacy_mode(token: str, session_id: str):
    """Test updating session privacy mode."""
    print_test("Test 9: Update session privacy mode")
    
    async with httpx.AsyncClient() as client:
        try:
            # Update to incognito
            response = await client.put(
                f"{API_BASE}/sessions/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"privacy_mode": "incognito"}
            )
            
            if response.status_code == 200:
                session = response.json()
                if session.get("privacy_mode") == "incognito":
                    print_result(True, "Privacy mode updated to incognito")
                else:
                    print_result(False, f"Privacy mode is {session.get('privacy_mode')}, expected incognito")
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print_result(False, f"Error: {e}")


async def test_update_session_memory_profile(token: str, session_id: str, new_profile_id: str):
    """Test updating session memory profile."""
    print_test("Test 10: Update session memory profile")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{API_BASE}/sessions/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"memory_profile_id": new_profile_id}
            )
            
            if response.status_code == 200:
                session = response.json()
                if session.get("memory_profile_id") == new_profile_id:
                    print_result(True, "Memory profile updated")
                else:
                    print_result(False, "Memory profile not updated correctly")
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print_result(False, f"Error: {e}")


async def test_get_session_messages(token: str, session_id: str):
    """Test getting messages from a session."""
    print_test("Test 11: Get session messages")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/sessions/{session_id}/messages",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                messages = response.json()
                print_result(True, f"Retrieved {len(messages)} messages")
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print_result(False, f"Error: {e}")


async def test_delete_session(token: str, session_id: str):
    """Test deleting a session."""
    print_test("Test 12: Delete session")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{API_BASE}/sessions/{session_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, "Session deleted", {"message": data.get("message")})
                
                # Verify it's gone
                verify_response = await client.get(
                    f"{API_BASE}/sessions/{session_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if verify_response.status_code == 404:
                    print_result(True, "Verified: Session no longer exists")
                else:
                    print_result(False, "Session still exists after deletion!")
            else:
                print_result(False, f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print_result(False, f"Error: {e}")


# =============================================================================
# Error Case Tests
# =============================================================================
async def test_error_cases(token: str):
    """Test various error scenarios."""
    print_section("ERROR CASE TESTS")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Access non-existent session
        print_test("Error Test 1: Access non-existent session")
        try:
            response = await client.get(
                f"{API_BASE}/sessions/00000000-0000-0000-0000-000000000000",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 404:
                print_result(True, "Correctly returns 404 for non-existent session")
            else:
                print_result(False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            print_result(False, f"Error: {e}")
        
        # Test 2: Create session with non-existent profile
        print_test("Error Test 2: Create session with non-existent profile")
        try:
            response = await client.post(
                f"{API_BASE}/sessions",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "memory_profile_id": "00000000-0000-0000-0000-000000000000",
                    "privacy_mode": "normal"
                }
            )
            if response.status_code == 404:
                print_result(True, "Correctly returns 404 for non-existent profile")
            else:
                print_result(False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            print_result(False, f"Error: {e}")
        
        # Test 3: Access without authentication
        print_test("Error Test 3: Access without authentication")
        try:
            response = await client.get(f"{API_BASE}/sessions")
            if response.status_code == 403:
                print_result(True, "Correctly returns 403 for unauthenticated request")
            else:
                print_result(False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            print_result(False, f"Error: {e}")


# =============================================================================
# Main Test Runner
# =============================================================================
async def run_all_tests():
    """Run all tests in sequence."""
    print_section("CHECKPOINT 3.11 - COMPREHENSIVE SESSION TESTS")
    
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
    
    # Step 2: Get memory profiles
    print_section("SETUP - GET MEMORY PROFILES")
    profiles = await get_memory_profiles(token)
    if not profiles:
        print("\n⚠️  No memory profiles found. Some tests may fail.")
        default_profile_id = None
    else:
        default_profile_id = profiles[0]["id"]
        print(f"Using profile: {default_profile_id[:8]}... ({profiles[0].get('name')})")
    
    # Step 3: Create sessions
    print_section("SESSION CREATION TESTS")
    session1 = await test_create_session_with_default_profile(token)
    
    if default_profile_id:
        session2 = await test_create_session_with_specific_profile(token, default_profile_id)
    else:
        session2 = None
    
    session3 = await test_create_incognito_session(token)
    session4 = await test_create_pause_memories_session(token)
    
    # Step 4: Retrieve sessions
    print_section("SESSION RETRIEVAL TESTS")
    total_sessions = await test_get_all_sessions(token)
    await test_get_sessions_with_pagination(token)
    
    if default_profile_id:
        await test_filter_sessions_by_profile(token, default_profile_id)
    
    if session1:
        await test_get_specific_session(token, session1)
    
    # Step 5: Update sessions
    print_section("SESSION UPDATE TESTS")
    if session1:
        await test_update_session_privacy_mode(token, session1)
        
        if len(profiles) >= 2:
            # Update to a different profile
            await test_update_session_memory_profile(token, session1, profiles[1]["id"])
    
    # Step 6: Get messages
    print_section("MESSAGE RETRIEVAL TESTS")
    if session1:
        await test_get_session_messages(token, session1)
    
    # Step 7: Delete sessions
    print_section("SESSION DELETION TESTS")
    if session3:
        await test_delete_session(token, session3)
    
    # Step 8: Error cases
    await test_error_cases(token)
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"✅ All tests completed!")
    print(f"   Total sessions created: {4 if session4 else 0}")
    print(f"   Sessions remaining: {total_sessions}")
    print(f"\nCheckpoint 3.11 testing complete.")
    print("Review the results above to identify any failures.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

