#!/usr/bin/env python3
"""
Test script for Step 5.3: ChatService Integration
Tests ChatService functionality and agent integration.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory
os.chdir(backend_dir)

from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = None

from services.chat_service import ChatService
from services.database_service import DatabaseService
try:
    from database.models import ChatSession, User, MemoryProfile
except ImportError:
    ChatSession = User = MemoryProfile = None


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


def print_check(description: str, passed: bool, details: str = ""):
    """Print a check result."""
    status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    print(f"  {status} {description}")
    if details and passed:
        print(f"    {Colors.BLUE}→{Colors.RESET} {details}")


def test_chat_service_initialization():
    """Test ChatService initialization."""
    print_header("TESTING CHATSERVICE INITIALIZATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        
        # Create ChatService
        checks_total += 1
        chat_service = ChatService(mock_db)
        
        if chat_service.db == mock_db:
            checks_passed += 1
            print_check("ChatService initializes with database session", True)
        else:
            print_check("ChatService initializes with database session", False)
        
        checks_total += 1
        if hasattr(chat_service, 'db_service'):
            checks_passed += 1
            print_check("ChatService has db_service", True)
        else:
            print_check("ChatService has db_service", False)
        
        checks_total += 1
        if hasattr(chat_service, 'coordinator'):
            checks_passed += 1
            print_check("ChatService has coordinator", True)
        else:
            print_check("ChatService has coordinator", False)
        
        checks_total += 1
        if hasattr(chat_service, 'vector_service'):
            checks_passed += 1
            print_check("ChatService has vector_service", True)
        else:
            print_check("ChatService has vector_service", False)
        
    except Exception as e:
        print_check("ChatService initialization", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_prepare_agent_input():
    """Test _prepare_agent_input helper method."""
    print_header("TESTING _PREPARE_AGENT_INPUT")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        chat_service = ChatService(mock_db)
        
        # Create mock session
        mock_session = Mock()
        mock_session.id = 1
        mock_session.privacy_mode = "normal"
        mock_session.memory_profile_id = 1
        
        # Test prepare_agent_input
        checks_total += 1
        agent_input = chat_service._prepare_agent_input(
            session=mock_session,
            message="Hello",
            conversation_history=[{"role": "user", "content": "Hi"}]
        )
        
        if agent_input.get("session_id") == 1:
            checks_passed += 1
            print_check("_prepare_agent_input sets session_id", True)
        else:
            print_check("_prepare_agent_input sets session_id", False)
        
        checks_total += 1
        if agent_input.get("user_message") == "Hello":
            checks_passed += 1
            print_check("_prepare_agent_input sets user_message", True)
        else:
            print_check("_prepare_agent_input sets user_message", False)
        
        checks_total += 1
        if agent_input.get("privacy_mode") == "normal":
            checks_passed += 1
            print_check("_prepare_agent_input sets privacy_mode", True)
        else:
            print_check("_prepare_agent_input sets privacy_mode", False)
        
        checks_total += 1
        if "context" in agent_input and "conversation_history" in agent_input["context"]:
            checks_passed += 1
            print_check("_prepare_agent_input includes conversation_history", True)
        else:
            print_check("_prepare_agent_input includes conversation_history", False)
        
    except Exception as e:
        print_check("_prepare_agent_input", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_save_conversation():
    """Test _save_conversation helper method."""
    print_header("TESTING _SAVE_CONVERSATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        chat_service = ChatService(mock_db)
        
        # Mock database service methods
        mock_user_msg = Mock()
        mock_user_msg.id = 1
        mock_assistant_msg = Mock()
        mock_assistant_msg.id = 2
        
        chat_service.db_service.create_message = Mock(side_effect=[mock_user_msg, mock_assistant_msg])
        
        # Test save_conversation
        checks_total += 1
        user_msg, assistant_msg = chat_service._save_conversation(
            session_id=1,
            user_message="Hello",
            assistant_message="Hi there!"
        )
        
        if user_msg.id == 1 and assistant_msg.id == 2:
            checks_passed += 1
            print_check("_save_conversation returns message objects", True)
        else:
            print_check("_save_conversation returns message objects", False)
        
        checks_total += 1
        if chat_service.db_service.create_message.call_count == 2:
            checks_passed += 1
            print_check("_save_conversation calls create_message twice", True)
        else:
            print_check("_save_conversation calls create_message twice", False)
        
        # Verify user message call
        checks_total += 1
        user_call = chat_service.db_service.create_message.call_args_list[0]
        if user_call[1]["role"] == "user" and user_call[1]["content"] == "Hello":
            checks_passed += 1
            print_check("_save_conversation saves user message correctly", True)
        else:
            print_check("_save_conversation saves user message correctly", False)
        
        # Verify assistant message call
        checks_total += 1
        assistant_call = chat_service.db_service.create_message.call_args_list[1]
        if (assistant_call[1]["role"] == "assistant" and 
            assistant_call[1]["content"] == "Hi there!" and
            assistant_call[1]["agent_name"] == "ContextCoordinatorAgent"):
            checks_passed += 1
            print_check("_save_conversation saves assistant message correctly", True)
        else:
            print_check("_save_conversation saves assistant message correctly", False)
        
    except Exception as e:
        print_check("_save_conversation", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_save_memories():
    """Test _save_memories helper method."""
    print_header("TESTING _SAVE_MEMORIES")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        chat_service = ChatService(mock_db)
        
        # Mock memory objects
        mock_memory1 = Mock()
        mock_memory1.id = 1
        mock_memory1.content = "User prefers Python"
        
        mock_memory2 = Mock()
        mock_memory2.id = 2
        mock_memory2.content = "User is a developer"
        
        chat_service.db_service.create_memory = Mock(side_effect=[mock_memory1, mock_memory2])
        chat_service.vector_service.add_memory_embedding = Mock(return_value=True)
        
        # Test memories
        memories = [
            {
                "content": "User prefers Python",
                "importance_score": 0.7,
                "memory_type": "preference",
                "tags": ["programming", "python"]
            },
            {
                "content": "User is a developer",
                "importance_score": 0.8,
                "memory_type": "fact",
                "tags": ["career"]
            }
        ]
        
        checks_total += 1
        saved_count = chat_service._save_memories(
            memories=memories,
            profile_id=1,
            user_id=1
        )
        
        if saved_count == 2:
            checks_passed += 1
            print_check("_save_memories saves all memories", True, f"Saved {saved_count} memories")
        else:
            print_check("_save_memories saves all memories", False, f"Expected 2, got {saved_count}")
        
        checks_total += 1
        if chat_service.db_service.create_memory.call_count == 2:
            checks_passed += 1
            print_check("_save_memories calls create_memory for each memory", True)
        else:
            print_check("_save_memories calls create_memory for each memory", False)
        
        checks_total += 1
        if chat_service.vector_service.add_memory_embedding.call_count == 2:
            checks_passed += 1
            print_check("_save_memories calls add_memory_embedding for each memory", True)
        else:
            print_check("_save_memories calls add_memory_embedding for each memory", False)
        
    except Exception as e:
        print_check("_save_memories", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_handle_privacy_mode():
    """Test _handle_privacy_mode helper method."""
    print_header("TESTING _HANDLE_PRIVACY_MODE")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        chat_service = ChatService(mock_db)
        
        # Test normal mode
        checks_total += 1
        mock_session_normal = Mock()
        mock_session_normal.id = 1
        mock_session_normal.privacy_mode = "normal"
        
        try:
            chat_service._handle_privacy_mode(mock_session_normal, {})
            checks_passed += 1
            print_check("_handle_privacy_mode handles normal mode", True)
        except Exception as e:
            print_check("_handle_privacy_mode handles normal mode", False, str(e))
        
        # Test incognito mode
        checks_total += 1
        mock_session_incognito = Mock()
        mock_session_incognito.id = 2
        mock_session_incognito.privacy_mode = "incognito"
        
        try:
            chat_service._handle_privacy_mode(mock_session_incognito, {})
            checks_passed += 1
            print_check("_handle_privacy_mode handles incognito mode", True)
        except Exception as e:
            print_check("_handle_privacy_mode handles incognito mode", False, str(e))
        
        # Test pause_memory mode
        checks_total += 1
        mock_session_pause = Mock()
        mock_session_pause.id = 3
        mock_session_pause.privacy_mode = "pause_memory"
        
        try:
            chat_service._handle_privacy_mode(mock_session_pause, {})
            checks_passed += 1
            print_check("_handle_privacy_mode handles pause_memory mode", True)
        except Exception as e:
            print_check("_handle_privacy_mode handles pause_memory mode", False, str(e))
        
    except Exception as e:
        print_check("_handle_privacy_mode", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_process_message_integration():
    """Test process_message with mocked coordinator."""
    print_header("TESTING PROCESS_MESSAGE INTEGRATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        chat_service = ChatService(mock_db)
        
        # Mock session
        mock_session = Mock()
        mock_session.id = 1
        mock_session.user_id = 1
        mock_session.memory_profile_id = 1
        mock_session.privacy_mode = "normal"
        
        chat_service.db_service.get_session_by_id = Mock(return_value=mock_session)
        chat_service.db_service.get_memory_profile_by_id = Mock(return_value=Mock())
        chat_service.db_service.get_messages_by_session = Mock(return_value=[])
        
        # Mock coordinator result
        mock_coordinator_result = {
            "success": True,
            "data": {
                "response": "Hello! How can I help you?",
                "warnings": [],
                "memory_info": {
                    "memories_retrieved": 2
                },
                "memory_extraction_info": {
                    "memories_extracted": 1
                },
                "extracted_memories": [
                    {
                        "content": "User prefers Python",
                        "importance_score": 0.7,
                        "memory_type": "preference",
                        "tags": ["programming"]
                    }
                ]
            },
            "tokens_used": 150,
            "execution_time_ms": 1200,
            "agents_executed": ["PrivacyGuardianAgent", "MemoryRetrievalAgent", "ConversationAgent", "MemoryManagerAgent"],
            "tokens_by_agent": {"ConversationAgent": 100}
        }
        
        chat_service.coordinator.execute = Mock(return_value=mock_coordinator_result)
        
        # Mock message creation
        mock_user_msg = Mock()
        mock_assistant_msg = Mock()
        chat_service.db_service.create_message = Mock(side_effect=[mock_user_msg, mock_assistant_msg])
        chat_service.db_service.log_agent_action = Mock()
        
        # Mock memory saving
        chat_service._save_memories = Mock(return_value=1)
        
        # Test process_message
        checks_total += 1
        result = chat_service.process_message(
            session_id=1,
            user_message="Hello"
        )
        
        if result.get("message") == "Hello! How can I help you?":
            checks_passed += 1
            print_check("process_message returns correct response", True)
        else:
            print_check("process_message returns correct response", False)
        
        checks_total += 1
        if result.get("memories_used") == 2:
            checks_passed += 1
            print_check("process_message returns correct memories_used", True)
        else:
            print_check("process_message returns correct memories_used", False)
        
        checks_total += 1
        if result.get("new_memories_created") == 1:
            checks_passed += 1
            print_check("process_message returns correct new_memories_created", True)
        else:
            print_check("process_message returns correct new_memories_created", False)
        
        checks_total += 1
        if "metadata" in result and result["metadata"].get("tokens_used") == 150:
            checks_passed += 1
            print_check("process_message includes metadata", True)
        else:
            print_check("process_message includes metadata", False)
        
        checks_total += 1
        if chat_service.coordinator.execute.called:
            checks_passed += 1
            print_check("process_message calls coordinator.execute", True)
        else:
            print_check("process_message calls coordinator.execute", False)
        
        checks_total += 1
        if chat_service._save_memories.called:
            checks_passed += 1
            print_check("process_message saves memories in normal mode", True)
        else:
            print_check("process_message saves memories in normal mode", False)
        
    except Exception as e:
        print_check("process_message integration", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_process_message_error_handling():
    """Test process_message error handling."""
    print_header("TESTING PROCESS_MESSAGE ERROR HANDLING")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        chat_service = ChatService(mock_db)
        
        # Test session not found
        checks_total += 1
        chat_service.db_service.get_session_by_id = Mock(return_value=None)
        
        try:
            chat_service.process_message(session_id=999, user_message="Hello")
            print_check("process_message raises error for missing session", False)
        except ValueError:
            checks_passed += 1
            print_check("process_message raises error for missing session", True)
        except Exception as e:
            print_check("process_message raises error for missing session", False, f"Wrong exception: {type(e).__name__}")
        
        # Test coordinator failure
        checks_total += 1
        mock_session = Mock()
        mock_session.id = 1
        mock_session.privacy_mode = "normal"
        mock_session.memory_profile_id = 1
        
        chat_service.db_service.get_session_by_id = Mock(return_value=mock_session)
        chat_service.db_service.get_memory_profile_by_id = Mock(return_value=Mock())
        chat_service.db_service.get_messages_by_session = Mock(return_value=[])
        
        chat_service.coordinator.execute = Mock(return_value={
            "success": False,
            "error": "Agent orchestration failed"
        })
        
        try:
            chat_service.process_message(session_id=1, user_message="Hello")
            print_check("process_message raises error for coordinator failure", False)
        except RuntimeError:
            checks_passed += 1
            print_check("process_message raises error for coordinator failure", True)
        except Exception as e:
            print_check("process_message raises error for coordinator failure", False, f"Wrong exception: {type(e).__name__}")
        
    except Exception as e:
        print_check("process_message error handling", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_privacy_mode_memory_saving():
    """Test that memories are not saved in incognito/pause_memory modes."""
    print_header("TESTING PRIVACY MODE MEMORY SAVING")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock database session
        mock_db = Mock(spec=Session)
        chat_service = ChatService(mock_db)
        
        # Test incognito mode - memories should not be saved
        checks_total += 1
        mock_session_incognito = Mock()
        mock_session_incognito.id = 1
        mock_session_incognito.user_id = 1
        mock_session_incognito.memory_profile_id = 1
        mock_session_incognito.privacy_mode = "incognito"
        
        chat_service.db_service.get_session_by_id = Mock(return_value=mock_session_incognito)
        chat_service.db_service.get_memory_profile_by_id = Mock(return_value=Mock())
        chat_service.db_service.get_messages_by_session = Mock(return_value=[])
        
        mock_coordinator_result = {
            "success": True,
            "data": {
                "response": "Hello!",
                "warnings": [],
                "memory_info": {"memories_retrieved": 0},
                "memory_extraction_info": {"memories_extracted": 0},
                "extracted_memories": []
            },
            "tokens_used": 100,
            "execution_time_ms": 1000,
            "agents_executed": [],
            "tokens_by_agent": {}
        }
        
        chat_service.coordinator.execute = Mock(return_value=mock_coordinator_result)
        chat_service.db_service.create_message = Mock(return_value=Mock())
        chat_service.db_service.log_agent_action = Mock()
        chat_service._save_memories = Mock(return_value=0)
        
        result = chat_service.process_message(session_id=1, user_message="Hello")
        
        if not chat_service._save_memories.called:
            checks_passed += 1
            print_check("Memories not saved in incognito mode", True)
        else:
            print_check("Memories not saved in incognito mode", False)
        
        # Test pause_memory mode - memories should not be saved
        checks_total += 1
        mock_session_pause = Mock()
        mock_session_pause.id = 2
        mock_session_pause.user_id = 1
        mock_session_pause.memory_profile_id = 1
        mock_session_pause.privacy_mode = "pause_memory"
        
        chat_service.db_service.get_session_by_id = Mock(return_value=mock_session_pause)
        
        result = chat_service.process_message(session_id=2, user_message="Hello")
        
        # _save_memories should not be called because memories_extracted is 0
        if result.get("new_memories_created") == 0:
            checks_passed += 1
            print_check("Memories not saved in pause_memory mode", True)
        else:
            print_check("Memories not saved in pause_memory mode", False)
        
    except Exception as e:
        print_check("Privacy mode memory saving", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'CHATSERVICE TEST SUITE - STEP 5.3'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Run all tests
    passed, checks = test_chat_service_initialization()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_prepare_agent_input()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_save_conversation()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_save_memories()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_handle_privacy_mode()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_process_message_integration()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_process_message_error_handling()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_privacy_mode_memory_saving()
    total_passed += passed
    total_checks += checks
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"  Total Checks: {total_checks}")
    print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {total_checks - total_passed}{Colors.RESET}")
    
    if total_passed == total_checks:
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}✗ SOME TESTS FAILED{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

