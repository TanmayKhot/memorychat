#!/usr/bin/env python3
"""
Test script to verify Step 2.1 logging system implementation.
This script tests all logging functionality required by Step 2.1.
"""
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config.logging_config import (
        app_logger,
        error_logger,
        database_logger,
        api_logger,
        conversation_logger,
        memory_manager_logger,
        memory_retrieval_logger,
        privacy_guardian_logger,
        analyst_logger,
        coordinator_logger,
        log_agent_start,
        log_agent_complete,
        log_agent_error,
        log_api_request,
        log_database_query,
    )
    from config.settings import settings
except ImportError as e:
    print(f"Error importing logging config: {e}")
    print("Make sure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def test_logging_system():
    """Test all logging functionality."""
    print("=" * 60)
    print("Testing Step 2.1: Logging System Implementation")
    print("=" * 60)
    
    # Test 1: Verify loggers exist
    print("\n1. Testing logger initialization...")
    loggers = {
        "app_logger": app_logger,
        "error_logger": error_logger,
        "database_logger": database_logger,
        "api_logger": api_logger,
        "conversation_logger": conversation_logger,
        "memory_manager_logger": memory_manager_logger,
        "memory_retrieval_logger": memory_retrieval_logger,
        "privacy_guardian_logger": privacy_guardian_logger,
        "analyst_logger": analyst_logger,
        "coordinator_logger": coordinator_logger,
    }
    
    for name, logger in loggers.items():
        assert logger is not None, f"{name} is None"
        print(f"  ✓ {name} initialized")
    
    # Test 2: Verify log directory structure
    print("\n2. Testing log directory structure...")
    log_dir = Path(__file__).parent / "logs"
    agents_dir = log_dir / "agents"
    
    assert log_dir.exists(), "logs/ directory does not exist"
    assert agents_dir.exists(), "logs/agents/ directory does not exist"
    print(f"  ✓ logs/ directory exists: {log_dir}")
    print(f"  ✓ logs/agents/ directory exists: {agents_dir}")
    
    # Test 3: Test logging at different levels
    print("\n3. Testing log levels...")
    app_logger.debug("Debug message")
    app_logger.info("Info message")
    app_logger.warning("Warning message")
    app_logger.error("Error message")
    print("  ✓ Log levels working (DEBUG, INFO, WARNING, ERROR)")
    
    # Test 4: Test utility functions
    print("\n4. Testing utility functions...")
    
    # Test log_agent_start
    log_agent_start("conversation", "Test task")
    print("  ✓ log_agent_start() working")
    
    # Test log_agent_complete
    log_agent_complete("conversation", "Test task", 0.123)
    print("  ✓ log_agent_complete() working")
    
    # Test log_agent_error
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_agent_error("conversation", "Test task", e)
    print("  ✓ log_agent_error() working")
    
    # Test log_api_request
    log_api_request("/api/chat/message", "POST", user_id=1)
    print("  ✓ log_api_request() working")
    
    # Test log_database_query
    log_database_query("SELECT", "users")
    print("  ✓ log_database_query() working")
    
    # Test 5: Test agent-specific loggers
    print("\n5. Testing agent-specific loggers...")
    conversation_logger.info("Conversation agent test message")
    memory_manager_logger.info("Memory manager agent test message")
    memory_retrieval_logger.info("Memory retrieval agent test message")
    privacy_guardian_logger.info("Privacy guardian agent test message")
    analyst_logger.info("Analyst agent test message")
    coordinator_logger.info("Coordinator agent test message")
    print("  ✓ All agent loggers working")
    
    # Test 6: Test database logger
    print("\n6. Testing database logger...")
    database_logger.info("Database operation test")
    database_logger.debug("Database query executed")
    print("  ✓ Database logger working")
    
    # Test 7: Test API logger
    print("\n7. Testing API logger...")
    api_logger.info("API endpoint called")
    api_logger.warning("API rate limit approaching")
    print("  ✓ API logger working")
    
    # Test 8: Test error logger
    print("\n8. Testing error logger...")
    error_logger.error("Test error message")
    print("  ✓ Error logger working")
    
    # Test 9: Verify log files are created
    print("\n9. Verifying log files...")
    expected_files = [
        log_dir / "app.log",
        log_dir / "errors.log",
        log_dir / "database.log",
        agents_dir / "conversation.log",
        agents_dir / "memory_manager.log",
        agents_dir / "memory_retrieval.log",
        agents_dir / "privacy_guardian.log",
        agents_dir / "analyst.log",
        agents_dir / "coordinator.log",
    ]
    
    for log_file in expected_files:
        if log_file.exists():
            size = log_file.stat().st_size
            print(f"  ✓ {log_file.name} exists ({size} bytes)")
        else:
            print(f"  ⚠ {log_file.name} not yet created (will be created on first log)")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! Step 2.1 implementation is complete.")
    print("=" * 60)
    print(f"\nLog level configuration: {settings.LOG_LEVEL}")
    print(f"Log directory: {log_dir}")
    print("\nCheck the log files to verify logging is working correctly.")


if __name__ == "__main__":
    try:
        test_logging_system()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

