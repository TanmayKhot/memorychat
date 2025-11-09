#!/usr/bin/env python3
"""
Test script to verify Step 2.2 monitoring utilities implementation.
This script tests all monitoring and error handling functionality required by Step 2.2.
"""
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from services.monitoring_service import monitoring_service, MonitoringService
    from services.error_handler import (
        MemoryChatException,
        DatabaseException,
        ProfileNotFoundException,
        SessionNotFoundException,
        UserNotFoundException,
        InvalidPrivacyModeException,
        MemoryLimitExceededException,
        TokenLimitExceededException,
        LLMException,
        VectorDatabaseException,
        ValidationException,
        ErrorRecoveryStrategy,
        handle_exception,
        format_error_message,
        log_error_with_context,
        safe_execute,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def test_monitoring_service():
    """Test MonitoringService functionality."""
    print("=" * 60)
    print("Testing MonitoringService")
    print("=" * 60)
    
    # Test 1: track_execution_time decorator
    print("\n1. Testing track_execution_time decorator...")
    
    @monitoring_service.track_execution_time("test_agent")
    def test_function():
        time.sleep(0.1)  # Simulate work
        return "success"
    
    result = test_function()
    assert result == "success", "Function should return success"
    print("  ✓ Decorator tracks execution time")
    
    # Test 2: log_token_usage
    print("\n2. Testing log_token_usage...")
    monitoring_service.log_token_usage(
        "test_agent",
        input_tokens=100,
        output_tokens=50,
        cost=0.002
    )
    print("  ✓ Token usage logged")
    
    # Test 3: log_memory_operation
    print("\n3. Testing log_memory_operation...")
    monitoring_service.log_memory_operation("CREATE", profile_id=1, count=1)
    monitoring_service.log_memory_operation("READ", profile_id=1, count=5)
    monitoring_service.log_memory_operation("UPDATE", profile_id=2, count=2)
    print("  ✓ Memory operations logged")
    
    # Test 4: log_privacy_check
    print("\n4. Testing log_privacy_check...")
    monitoring_service.log_privacy_check(session_id=1, mode="normal", violations_found=0)
    monitoring_service.log_privacy_check(session_id=2, mode="incognito", violations_found=1)
    print("  ✓ Privacy checks logged")
    
    # Test 5: get_performance_stats
    print("\n5. Testing get_performance_stats...")
    stats = monitoring_service.get_performance_stats(time_range="1h")
    
    assert "agent_response_times" in stats, "Should include agent_response_times"
    assert "token_usage" in stats, "Should include token_usage"
    assert "error_rates" in stats, "Should include error_rates"
    assert "memory_operations" in stats, "Should include memory_operations"
    assert "privacy_checks" in stats, "Should include privacy_checks"
    
    print(f"  ✓ Performance stats retrieved")
    print(f"    - Metrics count: {stats['metrics_count']}")
    print(f"    - Agents tracked: {len(stats['agent_response_times'])}")
    
    # Test 6: get_agent_stats
    print("\n6. Testing get_agent_stats...")
    agent_stats = monitoring_service.get_agent_stats("test_agent")
    
    assert "agent_name" in agent_stats, "Should include agent_name"
    assert "total_executions" in agent_stats, "Should include total_executions"
    assert "average_response_time" in agent_stats, "Should include average_response_time"
    assert "token_usage" in agent_stats, "Should include token_usage"
    
    print(f"  ✓ Agent stats retrieved")
    print(f"    - Agent: {agent_stats['agent_name']}")
    print(f"    - Executions: {agent_stats['total_executions']}")
    print(f"    - Avg time: {agent_stats['average_response_time']:.3f}s")
    
    print("\n✓ All MonitoringService tests passed!")


def test_error_handler():
    """Test error handling functionality."""
    print("\n" + "=" * 60)
    print("Testing Error Handler")
    print("=" * 60)
    
    # Test 1: Custom exception classes
    print("\n1. Testing custom exception classes...")
    
    exceptions = [
        DatabaseException("Database error", operation="SELECT", table="users"),
        ProfileNotFoundException(123),
        SessionNotFoundException(456),
        UserNotFoundException(user_id=789),
        InvalidPrivacyModeException("invalid", ["normal", "incognito"]),
        MemoryLimitExceededException(limit=1000, current=1200),
        TokenLimitExceededException(limit=4000, used=5000, agent_name="test"),
        LLMException("LLM error", provider="openai", status_code=500),
        VectorDatabaseException("Vector DB error", operation="search"),
        ValidationException("Validation error", field="email"),
    ]
    
    for exc in exceptions:
        assert isinstance(exc, MemoryChatException), f"{type(exc).__name__} should inherit from MemoryChatException"
        assert hasattr(exc, "error_code"), f"{type(exc).__name__} should have error_code"
        assert hasattr(exc, "to_dict"), f"{type(exc).__name__} should have to_dict method"
        
        error_dict = exc.to_dict()
        assert "error" in error_dict, "Error dict should have 'error' key"
        assert "error_code" in error_dict, "Error dict should have 'error_code' key"
    
    print(f"  ✓ All {len(exceptions)} custom exception classes working")
    
    # Test 2: handle_exception
    print("\n2. Testing handle_exception...")
    
    # Test with custom exception
    custom_exc = ProfileNotFoundException(123)
    error_response = handle_exception(custom_exc, context={"agent_name": "test"})
    
    assert "error" in error_response, "Should include error message"
    assert "error_code" in error_response, "Should include error_code"
    assert "timestamp" in error_response, "Should include timestamp"
    
    print("  ✓ handle_exception works with custom exceptions")
    
    # Test with generic exception
    generic_exc = ValueError("Generic error")
    error_response = handle_exception(generic_exc)
    
    assert "error" in error_response, "Should include error message"
    assert error_response["error_code"] == "UNKNOWN_ERROR", "Should have UNKNOWN_ERROR code"
    
    print("  ✓ handle_exception works with generic exceptions")
    
    # Test 3: format_error_message
    print("\n3. Testing format_error_message...")
    
    user_msg = format_error_message(custom_exc, user_friendly=True)
    assert isinstance(user_msg, str), "Should return string"
    assert len(user_msg) > 0, "Message should not be empty"
    
    debug_msg = format_error_message(generic_exc, user_friendly=False)
    assert "ValueError" in debug_msg or "Generic error" in debug_msg, "Should include error details"
    
    print("  ✓ format_error_message works correctly")
    
    # Test 4: ErrorRecoveryStrategy
    print("\n4. Testing ErrorRecoveryStrategy...")
    
    # Test should_retry
    retryable = DatabaseException("Transient error")
    non_retryable = ProfileNotFoundException(123)
    
    assert ErrorRecoveryStrategy.should_retry(retryable, attempt=1, max_attempts=3), "Should retry retryable errors"
    assert not ErrorRecoveryStrategy.should_retry(retryable, attempt=3, max_attempts=3), "Should not retry after max attempts"
    assert not ErrorRecoveryStrategy.should_retry(non_retryable, attempt=1, max_attempts=3), "Should not retry non-retryable errors"
    
    print("  ✓ should_retry logic works correctly")
    
    # Test get_fallback_response
    fallback = ErrorRecoveryStrategy.get_fallback_response(custom_exc)
    assert "success" in fallback, "Should include success flag"
    assert "error" in fallback, "Should include error message"
    assert fallback["fallback"] is True, "Should mark as fallback"
    
    print("  ✓ get_fallback_response works correctly")
    
    # Test 5: safe_execute
    print("\n5. Testing safe_execute...")
    
    def failing_function():
        raise ValueError("Test error")
    
    result = safe_execute(failing_function, fallback_value="fallback")
    assert result == "fallback", "Should return fallback value on error"
    
    def success_function():
        return "success"
    
    result = safe_execute(success_function, fallback_value="fallback")
    assert result == "success", "Should return function result on success"
    
    print("  ✓ safe_execute works correctly")
    
    print("\n✓ All Error Handler tests passed!")


def test_integration():
    """Test integration between monitoring and error handling."""
    print("\n" + "=" * 60)
    print("Testing Integration")
    print("=" * 60)
    
    # Test error tracking in monitoring
    print("\n1. Testing error tracking in monitoring...")
    
    @monitoring_service.track_execution_time("error_test_agent")
    def error_function():
        raise DatabaseException("Test database error")
    
    try:
        error_function()
    except DatabaseException:
        pass  # Expected
    
    stats = monitoring_service.get_agent_stats("error_test_agent")
    assert stats["error_count"] > 0, "Should track errors"
    
    print("  ✓ Errors are tracked in monitoring service")
    
    # Test performance stats include errors
    print("\n2. Testing performance stats include errors...")
    all_stats = monitoring_service.get_performance_stats(time_range="all")
    
    assert "error_rates" in all_stats, "Stats should include error_rates"
    assert len(all_stats["error_rates"]) > 0, "Should have error rates"
    
    print("  ✓ Performance stats include error rates")
    
    print("\n✓ All integration tests passed!")


def main():
    """Run all tests."""
    try:
        test_monitoring_service()
        test_error_handler()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nStep 2.2 implementation is complete and working correctly.")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

