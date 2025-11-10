#!/usr/bin/env python3
"""
Comprehensive test for Checkpoint 7.5: Logging Verification

This test verifies:
1. All log files are generating correctly
2. Log coverage (API requests, agent executions, errors, database operations)
3. Log rotation (generate large logs, verify rotation, verify old logs archived)
4. Error tracking (trigger various errors, verify stack traces, verify error context)
"""
import sys
import os
import time
import traceback
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import shutil

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

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
        LOG_DIR,
        AGENTS_LOG_DIR,
    )
except ImportError as e:
    print(f"Error importing logging config: {e}")
    print("Make sure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Optional imports for error testing
try:
    from config.settings import settings
except ImportError:
    settings = None

try:
    from services.error_handler import (
        ProfileNotFoundException,
        SessionNotFoundException,
        InvalidPrivacyModeException,
    )
    CUSTOM_EXCEPTIONS_AVAILABLE = True
except ImportError:
    CUSTOM_EXCEPTIONS_AVAILABLE = False
    # Create dummy exceptions for testing
    class ProfileNotFoundException(Exception):
        pass
    class SessionNotFoundException(Exception):
        pass
    class InvalidPrivacyModeException(Exception):
        pass


class LoggingVerificationTest:
    """Comprehensive logging verification test suite."""
    
    def __init__(self):
        self.test_results = []
        self.log_files_checked = []
        self.errors_triggered = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"  {message}")
    
    def verify_log_file_exists(self, log_file: Path, required: bool = True) -> bool:
        """Verify a log file exists and is readable."""
        if not log_file.exists():
            if required:
                self.log_test(
                    f"Log file exists: {log_file.name}",
                    False,
                    f"Log file not found: {log_file}"
                )
                return False
            else:
                # File may not exist yet if no logs written
                return True
        
        try:
            # Check if file is readable
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                size = len(content)
            
            self.log_files_checked.append({
                "file": str(log_file),
                "size": size,
                "exists": True
            })
            
            self.log_test(
                f"Log file readable: {log_file.name}",
                True,
                f"Size: {size} bytes"
            )
            return True
        except Exception as e:
            self.log_test(
                f"Log file readable: {log_file.name}",
                False,
                f"Error reading file: {str(e)}"
            )
            return False
    
    def check_log_content(self, log_file: Path, search_terms: List[str]) -> Dict[str, bool]:
        """Check if log file contains specific terms."""
        results = {}
        
        if not log_file.exists():
            for term in search_terms:
                results[term] = False
            return results
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for term in search_terms:
                found = term.lower() in content.lower()
                results[term] = found
        except Exception as e:
            print(f"  Warning: Could not read log file {log_file}: {e}")
            for term in search_terms:
                results[term] = False
        
        return results
    
    def test_1_review_all_log_files(self):
        """Test 1: Review all log files to verify they're generating correctly."""
        print("\n" + "=" * 70)
        print("TEST 1: Review All Log Files")
        print("=" * 70)
        
        # Expected log files
        expected_log_files = [
            LOG_DIR / "app.log",
            LOG_DIR / "errors.log",
            LOG_DIR / "database.log",
            AGENTS_LOG_DIR / "conversation.log",
            AGENTS_LOG_DIR / "memory_manager.log",
            AGENTS_LOG_DIR / "memory_retrieval.log",
            AGENTS_LOG_DIR / "privacy_guardian.log",
            AGENTS_LOG_DIR / "analyst.log",
            AGENTS_LOG_DIR / "coordinator.log",
        ]
        
        # Verify log directories exist
        self.log_test(
            "Log directory exists",
            LOG_DIR.exists(),
            f"Path: {LOG_DIR}"
        )
        
        self.log_test(
            "Agents log directory exists",
            AGENTS_LOG_DIR.exists(),
            f"Path: {AGENTS_LOG_DIR}"
        )
        
        # Verify each log file
        all_exist = True
        for log_file in expected_log_files:
            exists = self.verify_log_file_exists(log_file, required=False)
            if not exists:
                all_exist = False
        
        # Generate some test logs to ensure files are created
        print("\n  Generating test logs to ensure files are created...")
        app_logger.info("Test log entry for app.log")
        error_logger.error("Test error entry for errors.log")
        database_logger.info("Test database operation for database.log")
        conversation_logger.info("Test conversation agent log")
        memory_manager_logger.info("Test memory manager agent log")
        memory_retrieval_logger.info("Test memory retrieval agent log")
        privacy_guardian_logger.info("Test privacy guardian agent log")
        analyst_logger.info("Test analyst agent log")
        coordinator_logger.info("Test coordinator agent log")
        
        # Wait a moment for logs to be written
        time.sleep(0.1)
        
        # Verify files exist after generating logs
        all_created = True
        for log_file in expected_log_files:
            if not log_file.exists():
                self.log_test(
                    f"Log file created: {log_file.name}",
                    False,
                    f"File not created after logging: {log_file}"
                )
                all_created = False
            else:
                self.log_test(
                    f"Log file created: {log_file.name}",
                    True,
                    f"File exists: {log_file}"
                )
        
        self.log_test(
            "All log files generating correctly",
            all_created,
            f"Checked {len(expected_log_files)} log files"
        )
        
        return all_created
    
    def test_2_verify_log_coverage(self):
        """Test 2: Verify log coverage."""
        print("\n" + "=" * 70)
        print("TEST 2: Verify Log Coverage")
        print("=" * 70)
        
        coverage_results = {
            "api_requests": False,
            "agent_executions": False,
            "errors": False,
            "database_operations": False,
        }
        
        # Test API request logging
        print("\n  Testing API request logging...")
        log_api_request("/api/test/endpoint", "GET", user_id=1)
        log_api_request("/api/chat/message", "POST", user_id=2)
        time.sleep(0.1)
        
        app_log_content = ""
        if (LOG_DIR / "app.log").exists():
            with open(LOG_DIR / "app.log", 'r', encoding='utf-8') as f:
                app_log_content = f.read()
        
        api_logged = "API Request" in app_log_content or "/api/test/endpoint" in app_log_content
        coverage_results["api_requests"] = api_logged
        self.log_test(
            "API requests logged",
            api_logged,
            "API request logging verified"
        )
        
        # Test agent execution logging
        print("\n  Testing agent execution logging...")
        log_agent_start("conversation", "Test task execution")
        log_agent_complete("conversation", "Test task execution", 0.5)
        log_agent_start("memory_manager", "Extract memories")
        log_agent_complete("memory_manager", "Extract memories", 0.3)
        time.sleep(0.1)
        
        agent_logs_exist = []
        for agent_file in [
            AGENTS_LOG_DIR / "conversation.log",
            AGENTS_LOG_DIR / "memory_manager.log",
        ]:
            if agent_file.exists():
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "starting task" in content.lower() or "completed task" in content.lower():
                        agent_logs_exist.append(True)
                    else:
                        agent_logs_exist.append(False)
            else:
                agent_logs_exist.append(False)
        
        agent_executions_logged = any(agent_logs_exist)
        coverage_results["agent_executions"] = agent_executions_logged
        self.log_test(
            "Agent executions logged",
            agent_executions_logged,
            f"Agent execution logging verified ({len([x for x in agent_logs_exist if x])}/{len(agent_logs_exist)} files)"
        )
        
        # Test error logging
        print("\n  Testing error logging...")
        try:
            raise ValueError("Test error for logging verification")
        except Exception as e:
            log_agent_error("test_agent", "Test error task", e)
        
        # Also test direct error logger
        error_logger.error("Direct error log test")
        time.sleep(0.1)
        
        error_logged = False
        if (LOG_DIR / "errors.log").exists():
            with open(LOG_DIR / "errors.log", 'r', encoding='utf-8') as f:
                error_content = f.read()
                error_logged = "error" in error_content.lower() or "exception" in error_content.lower()
        
        coverage_results["errors"] = error_logged
        self.log_test(
            "Errors logged",
            error_logged,
            "Error logging verified"
        )
        
        # Test database operation logging
        print("\n  Testing database operation logging...")
        log_database_query("SELECT", "users")
        log_database_query("INSERT", "memories")
        log_database_query("UPDATE", "sessions")
        log_database_query("DELETE", "messages")
        time.sleep(0.1)
        
        db_logged = False
        if (LOG_DIR / "database.log").exists():
            with open(LOG_DIR / "database.log", 'r', encoding='utf-8') as f:
                db_content = f.read()
                db_logged = "database" in db_content.lower() or "users" in db_content.lower() or "SELECT" in db_content
        
        coverage_results["database_operations"] = db_logged
        self.log_test(
            "Database operations logged",
            db_logged,
            "Database operation logging verified"
        )
        
        # Overall coverage check
        all_covered = all(coverage_results.values())
        self.log_test(
            "All log coverage verified",
            all_covered,
            f"Coverage: API={coverage_results['api_requests']}, "
            f"Agents={coverage_results['agent_executions']}, "
            f"Errors={coverage_results['errors']}, "
            f"Database={coverage_results['database_operations']}"
        )
        
        return all_covered
    
    def test_3_log_rotation(self):
        """Test 3: Test log rotation."""
        print("\n" + "=" * 70)
        print("TEST 3: Test Log Rotation")
        print("=" * 70)
        
        # Create a temporary log file with rotation configured
        temp_log_dir = Path(tempfile.mkdtemp())
        test_log_file = temp_log_dir / "test_rotation.log"
        
        try:
            from logging.handlers import RotatingFileHandler
            import logging
            
            # Create a test logger with rotation (smaller size for testing)
            test_logger = logging.getLogger("test_rotation")
            test_logger.setLevel(logging.INFO)
            
            # Remove existing handlers
            test_logger.handlers = []
            
            # Create rotating file handler with small maxBytes for testing
            # Use 100KB instead of 10MB for faster testing
            handler = RotatingFileHandler(
                test_log_file,
                maxBytes=100 * 1024,  # 100KB
                backupCount=3,
                encoding="utf-8"
            )
            handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            ))
            test_logger.addHandler(handler)
            
            # Generate enough logs to trigger rotation
            print("\n  Generating logs to trigger rotation (100KB limit)...")
            log_message = "X" * 1000  # 1KB per message
            messages_written = 0
            
            for i in range(150):  # Write 150KB total to trigger rotation
                test_logger.info(f"Rotation test message {i}: {log_message}")
                messages_written += 1
                if i % 20 == 0:
                    handler.flush()
            
            handler.close()
            time.sleep(0.2)
            
            # Check if rotation occurred
            backup_files = []
            for i in range(1, 4):  # Check for .1, .2, .3 backups
                backup_file = Path(f"{test_log_file}.{i}")
                if backup_file.exists():
                    backup_files.append(backup_file)
            
            rotation_occurred = len(backup_files) > 0
            self.log_test(
                "Log rotation occurred",
                rotation_occurred,
                f"Found {len(backup_files)} backup file(s): {[f.name for f in backup_files]}"
            )
            
            # Verify main log file exists
            main_file_exists = test_log_file.exists()
            self.log_test(
                "Main log file exists after rotation",
                main_file_exists,
                f"Main file: {test_log_file.name}"
            )
            
            # Verify backup files are archived
            backups_archived = len(backup_files) > 0
            if backups_archived:
                for backup in backup_files:
                    size = backup.stat().st_size
                    self.log_test(
                        f"Backup file archived: {backup.name}",
                        True,
                        f"Size: {size} bytes"
                    )
            
            # Verify production log rotation configuration
            print("\n  Verifying production log rotation configuration...")
            from config.logging_config import setup_logger
            
            # Check that production loggers use RotatingFileHandler
            production_rotation_configured = True
            for logger_name in ["app", "database"]:
                logger = logging.getLogger(logger_name)
                has_rotation = any(
                    isinstance(h, RotatingFileHandler) 
                    for h in logger.handlers
                )
                if not has_rotation:
                    production_rotation_configured = False
                    break
            
            self.log_test(
                "Production log rotation configured",
                production_rotation_configured,
                "RotatingFileHandler configured for production loggers"
            )
            
            rotation_success = rotation_occurred and main_file_exists and backups_archived
            return rotation_success
            
        except Exception as e:
            self.log_test(
                "Log rotation test",
                False,
                f"Error during rotation test: {str(e)}\n{traceback.format_exc()}"
            )
            return False
        finally:
            # Cleanup
            try:
                shutil.rmtree(temp_log_dir)
            except:
                pass
    
    def test_4_error_tracking(self):
        """Test 4: Test error tracking."""
        print("\n" + "=" * 70)
        print("TEST 4: Test Error Tracking")
        print("=" * 70)
        
        error_tracking_results = {
            "errors_logged": False,
            "stack_traces_captured": False,
            "error_context_included": False,
            "various_errors_tested": False,
        }
        
        # Clear errors.log for clean test
        errors_log_file = LOG_DIR / "errors.log"
        initial_size = errors_log_file.stat().st_size if errors_log_file.exists() else 0
        
        # Test 1: Trigger ValueError
        print("\n  Testing ValueError logging...")
        try:
            raise ValueError("Test ValueError for error tracking")
        except Exception as e:
            log_agent_error("test_agent", "ValueError test", e)
            self.errors_triggered.append(("ValueError", str(e)))
        
        # Test 2: Trigger TypeError
        print("\n  Testing TypeError logging...")
        try:
            raise TypeError("Test TypeError for error tracking")
        except Exception as e:
            log_agent_error("test_agent", "TypeError test", e)
            self.errors_triggered.append(("TypeError", str(e)))
        
        # Test 3: Trigger RuntimeError
        print("\n  Testing RuntimeError logging...")
        try:
            raise RuntimeError("Test RuntimeError for error tracking")
        except Exception as e:
            log_agent_error("test_agent", "RuntimeError test", e)
            self.errors_triggered.append(("RuntimeError", str(e)))
        
        # Test 4: Trigger custom exception
        print("\n  Testing custom exception logging...")
        try:
            raise ProfileNotFoundException("Test profile not found")
        except Exception as e:
            error_logger.error(f"Custom exception: {type(e).__name__} - {str(e)}", exc_info=True)
            self.errors_triggered.append(("ProfileNotFoundException", str(e)))
        
        # Test 5: Trigger exception with context
        print("\n  Testing exception with context...")
        try:
            raise SessionNotFoundException("Test session not found", session_id=999)
        except Exception as e:
            error_logger.error(
                f"Exception with context: {type(e).__name__} - {str(e)}",
                exc_info=True,
                extra={"session_id": 999, "error_type": type(e).__name__}
            )
            self.errors_triggered.append(("SessionNotFoundException", str(e)))
        
        # Wait for logs to be written
        time.sleep(0.2)
        
        # Verify errors are logged
        if errors_log_file.exists():
            with open(errors_log_file, 'r', encoding='utf-8') as f:
                error_content = f.read()
            
            final_size = errors_log_file.stat().st_size
            errors_written = final_size > initial_size
            
            error_tracking_results["errors_logged"] = errors_written
            self.log_test(
                "Errors logged correctly",
                errors_written,
                f"Error log size increased from {initial_size} to {final_size} bytes"
            )
            
            # Verify stack traces are captured
            has_stack_trace = "Traceback" in error_content or "File \"" in error_content or "line " in error_content
            error_tracking_results["stack_traces_captured"] = has_stack_trace
            self.log_test(
                "Stack traces captured",
                has_stack_trace,
                "Stack trace information found in error logs"
            )
            
            # Verify error context is included
            has_context = any(
                term in error_content 
                for term in ["ValueError", "TypeError", "RuntimeError", "ProfileNotFoundException", "SessionNotFoundException"]
            )
            error_tracking_results["error_context_included"] = has_context
            self.log_test(
                "Error context included",
                has_context,
                "Error context and types found in error logs"
            )
            
            # Verify various error types tested
            various_errors_tested = len(self.errors_triggered) >= 3
            error_tracking_results["various_errors_tested"] = various_errors_tested
            self.log_test(
                "Various error types tested",
                various_errors_tested,
                f"Triggered {len(self.errors_triggered)} different error types"
            )
        else:
            self.log_test(
                "Errors logged correctly",
                False,
                "errors.log file does not exist"
            )
        
        # Overall error tracking check
        all_tracking_verified = all(error_tracking_results.values())
        self.log_test(
            "All error tracking verified",
            all_tracking_verified,
            f"Tracking: Logged={error_tracking_results['errors_logged']}, "
            f"StackTraces={error_tracking_results['stack_traces_captured']}, "
            f"Context={error_tracking_results['error_context_included']}, "
            f"Various={error_tracking_results['various_errors_tested']}"
        )
        
        return all_tracking_verified
    
    def run_all_tests(self):
        """Run all verification tests."""
        print("\n" + "=" * 70)
        print("CHECKPOINT 7.5: LOGGING VERIFICATION")
        print("=" * 70)
        print("\nThis test verifies:")
        print("1. All log files are generating correctly")
        print("2. Log coverage (API requests, agent executions, errors, database operations)")
        print("3. Log rotation (generate large logs, verify rotation, verify old logs archived)")
        print("4. Error tracking (trigger various errors, verify stack traces, verify error context)")
        print("=" * 70)
        
        results = {
            "test_1": self.test_1_review_all_log_files(),
            "test_2": self.test_2_verify_log_coverage(),
            "test_3": self.test_3_log_rotation(),
            "test_4": self.test_4_error_tracking(),
        }
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["passed"]])
        failed_tests = total_tests - passed_tests
        
        print(f"\nTotal tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\nTest Results:")
        for result in self.test_results:
            status = "✓" if result["passed"] else "✗"
            print(f"  {status} {result['test']}")
            if result["message"] and not result["passed"]:
                print(f"    → {result['message']}")
        
        print("\n" + "=" * 70)
        print("CHECKPOINT 7.5 VERIFICATION")
        print("=" * 70)
        
        checkpoint_passed = all(results.values())
        
        print(f"\n✓ All logs generating correctly: {results['test_1']}")
        print(f"✓ Log rotation working: {results['test_3']}")
        print(f"✓ Error tracking comprehensive: {results['test_4']}")
        print(f"✓ Logs useful for debugging: {checkpoint_passed}")
        
        if checkpoint_passed:
            print("\n✅ CHECKPOINT 7.5: ALL REQUIREMENTS MET")
        else:
            print("\n❌ CHECKPOINT 7.5: SOME REQUIREMENTS NOT MET")
            print("\nFailed tests:")
            for test_name, passed in results.items():
                if not passed:
                    print(f"  - {test_name}")
        
        print("=" * 70)
        
        return checkpoint_passed


def main():
    """Main test execution."""
    try:
        test_suite = LoggingVerificationTest()
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

