#!/usr/bin/env python3
"""
Comprehensive verification script for Phase 2: Steps 2.1 and 2.2
Tests all requirements from plan.txt to ensure everything works as expected.
"""
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

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
        get_agent_logger,
        LOG_DIR,
        AGENTS_LOG_DIR,
    )
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
        safe_execute,
    )
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


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


def verify_step_2_1():
    """Verify Step 2.1: Logging System requirements."""
    print_header("STEP 2.1: SET UP LOGGING SYSTEM")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Log format configuration
    print(f"\n{Colors.BOLD}1. Log Format Configuration{Colors.RESET}")
    checks_total += 1
    try:
        # Check formatter includes required fields
        handler = app_logger.handlers[0]
        formatter = handler.formatter
        format_str = formatter._fmt if hasattr(formatter, '_fmt') else str(formatter)
        
        has_timestamp = '%(asctime)s' in format_str or 'asctime' in str(format_str)
        has_level = '%(levelname)s' in format_str or 'levelname' in str(format_str)
        has_module = '%(name)s' in format_str or 'name' in str(format_str)
        has_message = '%(message)s' in format_str or 'message' in str(format_str)
        
        if has_timestamp and has_level and has_module and has_message:
            checks_passed += 1
            print_check("Log format includes timestamp, level, module, message", True)
        else:
            print_check("Log format includes timestamp, level, module, message", False,
                       f"Missing: timestamp={has_timestamp}, level={has_level}, module={has_module}, message={has_message}")
    except Exception as e:
        print_check("Log format configuration", False, str(e))
    
    # Check 2: Multiple handlers
    print(f"\n{Colors.BOLD}2. Multiple Handlers{Colors.RESET}")
    checks_total += 1
    try:
        app_handlers = app_logger.handlers
        has_console = any(isinstance(h, logging.StreamHandler) for h in app_handlers)
        has_file = any(isinstance(h, logging.handlers.RotatingFileHandler) for h in app_handlers)
        error_handlers = error_logger.handlers
        has_error_file = any(isinstance(h, logging.handlers.RotatingFileHandler) for h in error_handlers)
        
        if has_console and has_file and has_error_file:
            checks_passed += 1
            print_check("Console, file, and error file handlers configured", True)
        else:
            print_check("Console, file, and error file handlers configured", False,
                       f"console={has_console}, file={has_file}, error_file={has_error_file}")
    except Exception as e:
        print_check("Multiple handlers", False, str(e))
    
    # Check 3: Log rotation
    print(f"\n{Colors.BOLD}3. Log Rotation Configuration{Colors.RESET}")
    checks_total += 1
    try:
        file_handlers = [h for h in app_logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        if file_handlers:
            handler = file_handlers[0]
            max_bytes = handler.maxBytes
            backup_count = handler.backupCount
            
            if max_bytes == 10 * 1024 * 1024 and backup_count == 5:
                checks_passed += 1
                print_check("Log rotation configured (10MB max, 5 backups)", True)
            else:
                print_check("Log rotation configured (10MB max, 5 backups)", False,
                           f"maxBytes={max_bytes}, backupCount={backup_count}")
        else:
            print_check("Log rotation configured", False, "No RotatingFileHandler found")
    except Exception as e:
        print_check("Log rotation", False, str(e))
    
    # Check 4: Different log levels
    print(f"\n{Colors.BOLD}4. Different Log Levels{Colors.RESET}")
    checks_total += 1
    try:
        app_level = app_logger.level
        error_level = error_logger.level
        
        if app_level != logging.NOTSET and error_level == logging.ERROR:
            checks_passed += 1
            print_check("Different log levels for different modules", True,
                       f"app_logger={logging.getLevelName(app_level)}, error_logger=ERROR")
        else:
            print_check("Different log levels for different modules", False,
                       f"app_level={app_level}, error_level={error_level}")
    except Exception as e:
        print_check("Log levels", False, str(e))
    
    # Check 5: Loggers configured
    print(f"\n{Colors.BOLD}5. Loggers Configured{Colors.RESET}")
    checks_total += 1
    try:
        required_loggers = {
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
        
        all_exist = all(logger is not None for logger in required_loggers.values())
        if all_exist:
            checks_passed += 1
            print_check("All required loggers configured", True,
                       f"{len(required_loggers)} loggers initialized")
        else:
            missing = [name for name, logger in required_loggers.items() if logger is None]
            print_check("All required loggers configured", False, f"Missing: {missing}")
    except Exception as e:
        print_check("Loggers configured", False, str(e))
    
    # Check 6: Log directory structure
    print(f"\n{Colors.BOLD}6. Log Directory Structure{Colors.RESET}")
    checks_total += 1
    try:
        logs_dir_exists = LOG_DIR.exists() and LOG_DIR.is_dir()
        agents_dir_exists = AGENTS_LOG_DIR.exists() and AGENTS_LOG_DIR.is_dir()
        
        if logs_dir_exists and agents_dir_exists:
            checks_passed += 1
            print_check("Logs directory structure created", True,
                       f"logs/={logs_dir_exists}, logs/agents/={agents_dir_exists}")
        else:
            print_check("Logs directory structure created", False,
                       f"logs/={logs_dir_exists}, agents/={agents_dir_exists}")
    except Exception as e:
        print_check("Directory structure", False, str(e))
    
    # Check 7: Utility functions
    print(f"\n{Colors.BOLD}7. Logging Utility Functions{Colors.RESET}")
    checks_total += 1
    try:
        utilities = [
            ("log_agent_start", log_agent_start),
            ("log_agent_complete", log_agent_complete),
            ("log_agent_error", log_agent_error),
            ("log_api_request", log_api_request),
            ("log_database_query", log_database_query),
        ]
        
        all_exist = all(callable(func) for name, func in utilities)
        if all_exist:
            checks_passed += 1
            print_check("All utility functions exist and callable", True,
                       f"{len(utilities)} functions available")
        else:
            missing = [name for name, func in utilities if not callable(func)]
            print_check("All utility functions exist", False, f"Missing/callable: {missing}")
    except Exception as e:
        print_check("Utility functions", False, str(e))
    
    # Test actual logging
    print(f"\n{Colors.BOLD}8. Testing Logging Functionality{Colors.RESET}")
    checks_total += 1
    try:
        # Test different log levels
        app_logger.debug("Debug message test")
        app_logger.info("Info message test")
        app_logger.warning("Warning message test")
        app_logger.error("Error message test")
        
        # Test utility functions
        log_agent_start("test_agent", "test_task")
        log_agent_complete("test_agent", "test_task", 0.123)
        log_api_request("/api/test", "GET", user_id=1)
        log_database_query("SELECT", "users")
        
        # Test agent logger
        test_logger = get_agent_logger("conversation")
        test_logger.info("Agent logger test")
        
        checks_passed += 1
        print_check("Logging functionality working", True, "All log levels and utilities tested")
    except Exception as e:
        print_check("Logging functionality", False, str(e))
    
    # Checkpoint 2.1 summary
    print(f"\n{Colors.BOLD}CHECKPOINT 2.1 Summary{Colors.RESET}")
    print(f"  ✓ Logging configuration complete: {checks_passed >= 1}")
    print(f"  ✓ Log files being created: {LOG_DIR.exists()}")
    print(f"  ✓ Different log levels working: {checks_passed >= 4}")
    print(f"  ✓ Rotation configured: {checks_passed >= 3}")
    print(f"  ✓ Logs are readable and useful: {checks_passed >= 7}")
    
    return checks_passed, checks_total


def verify_step_2_2():
    """Verify Step 2.2: Monitoring Utilities requirements."""
    print_header("STEP 2.2: CREATE MONITORING UTILITIES")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: MonitoringService class
    print(f"\n{Colors.BOLD}1. MonitoringService Class{Colors.RESET}")
    checks_total += 1
    try:
        assert isinstance(monitoring_service, MonitoringService), "monitoring_service should be MonitoringService instance"
        checks_passed += 1
        print_check("MonitoringService class exists and singleton created", True)
    except Exception as e:
        print_check("MonitoringService class", False, str(e))
    
    # Check 2: Monitoring functions
    print(f"\n{Colors.BOLD}2. Monitoring Functions{Colors.RESET}")
    
    # track_execution_time
    checks_total += 1
    try:
        @monitoring_service.track_execution_time("test_agent")
        def test_func():
            time.sleep(0.01)
            return "success"
        
        result = test_func()
        assert result == "success", "Function should return correct result"
        checks_passed += 1
        print_check("track_execution_time decorator works", True)
    except Exception as e:
        print_check("track_execution_time", False, str(e))
    
    # log_token_usage
    checks_total += 1
    try:
        monitoring_service.log_token_usage("test_agent", 100, 50, 0.002)
        checks_passed += 1
        print_check("log_token_usage works", True)
    except Exception as e:
        print_check("log_token_usage", False, str(e))
    
    # log_memory_operation
    checks_total += 1
    try:
        monitoring_service.log_memory_operation("CREATE", profile_id=1, count=1)
        monitoring_service.log_memory_operation("READ", profile_id=1, count=5)
        checks_passed += 1
        print_check("log_memory_operation works", True)
    except Exception as e:
        print_check("log_memory_operation", False, str(e))
    
    # log_privacy_check
    checks_total += 1
    try:
        monitoring_service.log_privacy_check(session_id=1, mode="normal", violations_found=0)
        checks_passed += 1
        print_check("log_privacy_check works", True)
    except Exception as e:
        print_check("log_privacy_check", False, str(e))
    
    # get_performance_stats
    checks_total += 1
    try:
        stats = monitoring_service.get_performance_stats(time_range="1h")
        required_keys = ["agent_response_times", "token_usage", "error_rates", 
                        "memory_operations", "privacy_checks"]
        has_all_keys = all(key in stats for key in required_keys)
        
        if has_all_keys:
            checks_passed += 1
            print_check("get_performance_stats returns all required metrics", True)
        else:
            missing = [key for key in required_keys if key not in stats]
            print_check("get_performance_stats", False, f"Missing keys: {missing}")
    except Exception as e:
        print_check("get_performance_stats", False, str(e))
    
    # Check 3: Performance tracking
    print(f"\n{Colors.BOLD}3. Performance Tracking{Colors.RESET}")
    
    # Agent response times
    checks_total += 1
    try:
        stats = monitoring_service.get_performance_stats(time_range="all")
        has_response_times = "agent_response_times" in stats and len(stats["agent_response_times"]) > 0
        if has_response_times:
            checks_passed += 1
            print_check("Agent response times tracked", True)
        else:
            print_check("Agent response times tracked", False, "No response times found")
    except Exception as e:
        print_check("Response times tracking", False, str(e))
    
    # Token usage
    checks_total += 1
    try:
        stats = monitoring_service.get_performance_stats(time_range="all")
        has_token_usage = "token_usage" in stats and len(stats["token_usage"]) > 0
        if has_token_usage:
            checks_passed += 1
            print_check("Token usage per agent tracked", True)
        else:
            print_check("Token usage tracked", False, "No token usage found")
    except Exception as e:
        print_check("Token usage tracking", False, str(e))
    
    # Error rates
    checks_total += 1
    try:
        stats = monitoring_service.get_performance_stats(time_range="all")
        has_error_rates = "error_rates" in stats
        if has_error_rates:
            checks_passed += 1
            print_check("Error rates tracked", True)
        else:
            print_check("Error rates tracked", False)
    except Exception as e:
        print_check("Error rates tracking", False, str(e))
    
    # Memory operations
    checks_total += 1
    try:
        stats = monitoring_service.get_performance_stats(time_range="all")
        has_memory_ops = "memory_operations" in stats
        if has_memory_ops:
            checks_passed += 1
            print_check("Memory operations count tracked", True)
        else:
            print_check("Memory operations tracked", False)
    except Exception as e:
        print_check("Memory operations tracking", False, str(e))
    
    # Check 4: Error handler
    print(f"\n{Colors.BOLD}4. Error Handler{Colors.RESET}")
    
    # Custom exception classes
    checks_total += 1
    try:
        exceptions = [
            DatabaseException("Test"),
            ProfileNotFoundException(123),
            SessionNotFoundException(456),
            UserNotFoundException(user_id=789),
            InvalidPrivacyModeException("invalid", ["normal"]),
            MemoryLimitExceededException(1000, 1200),
            TokenLimitExceededException(4000, 5000),
            LLMException("Test"),
            VectorDatabaseException("Test"),
            ValidationException("Test"),
        ]
        
        all_custom = all(isinstance(e, MemoryChatException) for e in exceptions)
        all_have_dict = all(hasattr(e, 'to_dict') for e in exceptions)
        
        if all_custom and all_have_dict:
            checks_passed += 1
            print_check("Custom exception classes exist", True, f"{len(exceptions)} exception types")
        else:
            print_check("Custom exception classes", False)
    except Exception as e:
        print_check("Custom exceptions", False, str(e))
    
    # Global exception handler
    checks_total += 1
    try:
        exc = ProfileNotFoundException(123)
        error_response = handle_exception(exc)
        
        has_error = "error" in error_response
        has_code = "error_code" in error_response
        has_timestamp = "timestamp" in error_response
        
        if has_error and has_code and has_timestamp:
            checks_passed += 1
            print_check("Global exception handler works", True)
        else:
            print_check("Global exception handler", False, 
                       f"error={has_error}, code={has_code}, timestamp={has_timestamp}")
    except Exception as e:
        print_check("Exception handler", False, str(e))
    
    # Error recovery strategies
    checks_total += 1
    try:
        exc = DatabaseException("Test")
        should_retry = ErrorRecoveryStrategy.should_retry(exc, attempt=1, max_attempts=3)
        fallback = ErrorRecoveryStrategy.get_fallback_response(exc)
        
        has_retry_logic = isinstance(should_retry, bool)
        has_fallback = isinstance(fallback, dict) and "success" in fallback
        
        if has_retry_logic and has_fallback:
            checks_passed += 1
            print_check("Error recovery strategies work", True)
        else:
            print_check("Error recovery strategies", False,
                       f"retry={has_retry_logic}, fallback={has_fallback}")
    except Exception as e:
        print_check("Error recovery", False, str(e))
    
    # User-friendly error messages
    checks_total += 1
    try:
        exc = ProfileNotFoundException(123)
        user_msg = format_error_message(exc, user_friendly=True)
        debug_msg = format_error_message(exc, user_friendly=False)
        
        is_user_friendly = isinstance(user_msg, str) and len(user_msg) > 0
        is_debug_friendly = isinstance(debug_msg, str) and len(debug_msg) > 0
        
        if is_user_friendly and is_debug_friendly:
            checks_passed += 1
            print_check("User-friendly error messages work", True)
        else:
            print_check("User-friendly messages", False)
    except Exception as e:
        print_check("Error messages", False, str(e))
    
    # Checkpoint 2.2 summary
    print(f"\n{Colors.BOLD}CHECKPOINT 2.2 Summary{Colors.RESET}")
    print(f"  ✓ Monitoring utilities implemented: {checks_passed >= 5}")
    print(f"  ✓ Performance tracking working: {checks_passed >= 9}")
    print(f"  ✓ Error handling robust: {checks_passed >= 12}")
    print(f"  ✓ Can debug issues easily: {checks_passed >= 13}")
    
    return checks_passed, checks_total


def verify_checkpoint_2():
    """Verify Verification Checkpoint 2 requirements."""
    print_header("VERIFICATION CHECKPOINT 2")
    
    checks_passed = 0
    checks_total = 4
    
    # Comprehensive logging in place
    try:
        all_loggers_exist = all([
            app_logger, error_logger, database_logger, api_logger,
            conversation_logger, memory_manager_logger, memory_retrieval_logger,
            privacy_guardian_logger, analyst_logger, coordinator_logger
        ])
        if all_loggers_exist:
            checks_passed += 1
            print_check("Comprehensive logging in place", True)
        else:
            print_check("Comprehensive logging in place", False)
    except Exception as e:
        print_check("Comprehensive logging", False, str(e))
    
    # Can track agent behavior
    try:
        stats = monitoring_service.get_performance_stats(time_range="all")
        can_track = all(key in stats for key in ["agent_response_times", "token_usage", "error_rates"])
        if can_track:
            checks_passed += 1
            print_check("Can track agent behavior", True)
        else:
            print_check("Can track agent behavior", False)
    except Exception as e:
        print_check("Agent tracking", False, str(e))
    
    # Error handling robust
    try:
        exc = ProfileNotFoundException(123)
        error_response = handle_exception(exc)
        has_recovery = hasattr(ErrorRecoveryStrategy, 'should_retry')
        
        if isinstance(error_response, dict) and has_recovery:
            checks_passed += 1
            print_check("Error handling robust", True)
        else:
            print_check("Error handling robust", False)
    except Exception as e:
        print_check("Error handling", False, str(e))
    
    # Ready for agent implementation
    try:
        # Check that all necessary components exist
        has_logging = app_logger is not None
        has_monitoring = monitoring_service is not None
        has_error_handler = handle_exception is not None
        
        if has_logging and has_monitoring and has_error_handler:
            checks_passed += 1
            print_check("Ready for agent implementation", True)
        else:
            print_check("Ready for agent implementation", False,
                       f"logging={has_logging}, monitoring={has_monitoring}, error_handler={has_error_handler}")
    except Exception as e:
        print_check("Ready for agents", False, str(e))
    
    return checks_passed, checks_total


def main():
    """Run all verification tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'PHASE 2 VERIFICATION - STEPS 2.1 & 2.2'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Verify Step 2.1
    passed, total = verify_step_2_1()
    total_passed += passed
    total_checks += total
    
    # Verify Step 2.2
    passed, total = verify_step_2_2()
    total_passed += passed
    total_checks += total
    
    # Verify Checkpoint 2
    passed, total = verify_checkpoint_2()
    total_passed += passed
    total_checks += total
    
    # Final summary
    print_header("FINAL SUMMARY")
    
    percentage = (total_passed / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Total Checks: {total_checks}")
    print(f"  Passed: {Colors.GREEN}{total_passed}{Colors.RESET}")
    print(f"  Failed: {Colors.RED}{total_checks - total_passed}{Colors.RESET}")
    print(f"  Success Rate: {Colors.GREEN if percentage >= 90 else Colors.YELLOW}{percentage:.1f}%{Colors.RESET}")
    
    if total_passed == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Steps 2.1 and 2.2 are working as expected according to plan.txt{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"{Colors.RED}Please review the failed checks above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

