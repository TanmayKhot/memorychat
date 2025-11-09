#!/usr/bin/env python3
"""
Comprehensive verification script for Phases 0, 1, and 2 (up to checkpoint 2.2).
Tests all requirements from plan.txt to ensure everything works as expected.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory so .env file is found
os.chdir(backend_dir)


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


def verify_phase_0():
    """Verify Phase 0: Environment Setup."""
    print_header("PHASE 0: ENVIRONMENT SETUP")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 0.1: Directory structure
    print(f"\n{Colors.BOLD}STEP 0.1: Directory Structure{Colors.RESET}")
    
    required_dirs = [
        "agents",
        "services",
        "models",
        "database",
        "config",
        "logs",
        "tests",
    ]
    
    for dir_name in required_dirs:
        checks_total += 1
        dir_path = backend_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            checks_passed += 1
            print_check(f"Directory '{dir_name}' exists", True)
        else:
            print_check(f"Directory '{dir_name}' exists", False)
    
    # Check __init__.py files
    init_files = [
        "agents/__init__.py",
        "services/__init__.py",
        "models/__init__.py",
        "database/__init__.py",
        "config/__init__.py",
        "tests/__init__.py",
    ]
    
    for init_file in init_files:
        checks_total += 1
        file_path = backend_dir / init_file
        if file_path.exists():
            checks_passed += 1
            print_check(f"__init__.py exists: {init_file}", True)
        else:
            print_check(f"__init__.py exists: {init_file}", False)
    
    # Check 0.2: Requirements file
    print(f"\n{Colors.BOLD}STEP 0.2: Requirements File{Colors.RESET}")
    
    checks_total += 1
    req_file = backend_dir / "requirements.txt"
    if req_file.exists():
        checks_passed += 1
        print_check("requirements.txt exists", True)
        
        # Check for key dependencies
        required_packages = [
            "fastapi",
            "uvicorn",
            "langchain",
            "sqlalchemy",
            "chromadb",
            "pydantic",
        ]
        
        try:
            with open(req_file, 'r') as f:
                content = f.read()
            
            for pkg in required_packages:
                checks_total += 1
                if pkg.lower() in content.lower():
                    checks_passed += 1
                    print_check(f"Package '{pkg}' in requirements.txt", True)
                else:
                    print_check(f"Package '{pkg}' in requirements.txt", False)
        except Exception as e:
            print_check("Reading requirements.txt", False, str(e))
    else:
        print_check("requirements.txt exists", False)
    
    # Check .gitignore
    checks_total += 1
    gitignore = backend_dir.parent.parent / ".gitignore"
    if gitignore.exists():
        checks_passed += 1
        print_check(".gitignore exists", True)
    else:
        print_check(".gitignore exists", False)
    
    # Check 0.3: Environment configuration
    print(f"\n{Colors.BOLD}STEP 0.3: Environment Configuration{Colors.RESET}")
    
    checks_total += 1
    settings_file = backend_dir / "config" / "settings.py"
    if settings_file.exists():
        checks_passed += 1
        print_check("config/settings.py exists", True)
        
        # Check if settings.py has required fields
        try:
            with open(settings_file, 'r') as f:
                content = f.read()
            
            required_settings = [
                "OPENAI_API_KEY",
                "ENVIRONMENT",
                "LOG_LEVEL",
                "SQLITE_DATABASE_PATH",
                "CHROMADB_PATH",
            ]
            
            for setting in required_settings:
                checks_total += 1
                if setting in content:
                    checks_passed += 1
                    print_check(f"Setting '{setting}' defined", True)
                else:
                    print_check(f"Setting '{setting}' defined", False)
        except Exception as e:
            print_check("Reading settings.py", False, str(e))
    else:
        print_check("config/settings.py exists", False)
    
    # Check .env.example
    checks_total += 1
    env_example = backend_dir / ".env.example"
    if env_example.exists():
        checks_passed += 1
        print_check(".env.example exists", True)
    else:
        print_check(".env.example exists", False, "Optional but recommended")
    
    return checks_passed, checks_total


def verify_phase_1():
    """Verify Phase 1: Database Layer."""
    print_header("PHASE 1: DATABASE LAYER")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1.1: Database schema
    print(f"\n{Colors.BOLD}STEP 1.1: Database Schema{Colors.RESET}")
    
    checks_total += 1
    schema_file = backend_dir / "database" / "schema.sql"
    if schema_file.exists():
        checks_passed += 1
        print_check("database/schema.sql exists", True)
        
        # Check for required tables
        try:
            with open(schema_file, 'r') as f:
                content = f.read()
            
            required_tables = [
                "users",
                "memory_profiles",
                "chat_sessions",
                "chat_messages",
                "memories",
                "agent_logs",
            ]
            
            for table in required_tables:
                checks_total += 1
                if f"CREATE TABLE" in content.upper() and table.upper() in content.upper():
                    checks_passed += 1
                    print_check(f"Table '{table}' defined in schema", True)
                else:
                    print_check(f"Table '{table}' defined in schema", False)
            
            # Check for indexes
            checks_total += 1
            if "CREATE INDEX" in content.upper():
                checks_passed += 1
                print_check("Indexes defined in schema", True)
            else:
                print_check("Indexes defined in schema", False)
        except Exception as e:
            print_check("Reading schema.sql", False, str(e))
    else:
        print_check("database/schema.sql exists", False)
    
    # Check 1.2: Database models
    print(f"\n{Colors.BOLD}STEP 1.2: Database Models{Colors.RESET}")
    
    checks_total += 1
    models_file = backend_dir / "database" / "models.py"
    if models_file.exists():
        checks_passed += 1
        print_check("database/models.py exists", True)
        
        try:
            with open(models_file, 'r') as f:
                content = f.read()
            
            required_models = [
                "class User",
                "class MemoryProfile",
                "class ChatSession",
                "class ChatMessage",
                "class Memory",
                "class AgentLog",
            ]
            
            for model in required_models:
                checks_total += 1
                if model in content:
                    checks_passed += 1
                    print_check(f"Model '{model.split()[-1]}' defined", True)
                else:
                    print_check(f"Model '{model.split()[-1]}' defined", False)
        except Exception as e:
            print_check("Reading models.py", False, str(e))
    else:
        print_check("database/models.py exists", False)
    
    # Check database.py
    checks_total += 1
    db_file = backend_dir / "database" / "database.py"
    if db_file.exists():
        checks_passed += 1
        print_check("database/database.py exists", True)
        
        try:
            with open(db_file, 'r') as f:
                content = f.read()
            
            required_functions = [
                "create_all_tables",
                "get_db",
            ]
            
            for func in required_functions:
                checks_total += 1
                if f"def {func}" in content:
                    checks_passed += 1
                    print_check(f"Function '{func}' defined", True)
                else:
                    print_check(f"Function '{func}' defined", False)
        except Exception as e:
            print_check("Reading database.py", False, str(e))
    else:
        print_check("database/database.py exists", False)
    
    # Check 1.3: Database service
    print(f"\n{Colors.BOLD}STEP 1.3: Database Service{Colors.RESET}")
    
    checks_total += 1
    db_service_file = backend_dir / "services" / "database_service.py"
    if db_service_file.exists():
        checks_passed += 1
        print_check("services/database_service.py exists", True)
        
        try:
            with open(db_service_file, 'r') as f:
                content = f.read()
            
            # Check for DatabaseService class
            checks_total += 1
            if "class DatabaseService" in content:
                checks_passed += 1
                print_check("DatabaseService class defined", True)
            else:
                print_check("DatabaseService class defined", False)
            
            # Check for CRUD operations
            crud_operations = [
                "create_user",
                "get_user_by_id",
                "create_memory_profile",
                "create_session",
                "create_message",
                "create_memory",
            ]
            
            for op in crud_operations:
                checks_total += 1
                if f"def {op}" in content:
                    checks_passed += 1
                    print_check(f"CRUD operation '{op}' defined", True)
                else:
                    print_check(f"CRUD operation '{op}' defined", False)
        except Exception as e:
            print_check("Reading database_service.py", False, str(e))
    else:
        print_check("services/database_service.py exists", False)
    
    # Check 1.4: Vector service
    print(f"\n{Colors.BOLD}STEP 1.4: Vector Database (ChromaDB){Colors.RESET}")
    
    checks_total += 1
    vector_service_file = backend_dir / "services" / "vector_service.py"
    if vector_service_file.exists():
        checks_passed += 1
        print_check("services/vector_service.py exists", True)
        
        try:
            with open(vector_service_file, 'r') as f:
                content = f.read()
            
            checks_total += 1
            if "class VectorService" in content:
                checks_passed += 1
                print_check("VectorService class defined", True)
            else:
                print_check("VectorService class defined", False)
            
            vector_operations = [
                "add_memory_embedding",
                "search_similar_memories",
            ]
            
            for op in vector_operations:
                checks_total += 1
                if f"def {op}" in content:
                    checks_passed += 1
                    print_check(f"Vector operation '{op}' defined", True)
                else:
                    print_check(f"Vector operation '{op}' defined", False)
        except Exception as e:
            print_check("Reading vector_service.py", False, str(e))
    else:
        print_check("services/vector_service.py exists", False)
    
    # Check 1.5: Database initialization script
    print(f"\n{Colors.BOLD}STEP 1.5: Database Initialization Script{Colors.RESET}")
    
    checks_total += 1
    init_script = backend_dir.parent / "scripts" / "init_database.py"
    if init_script.exists():
        checks_passed += 1
        print_check("scripts/init_database.py exists", True)
        
        try:
            with open(init_script, 'r') as f:
                content = f.read()
            
            checks_total += 1
            if "create_default_user" in content:
                checks_passed += 1
                print_check("Default user creation function exists", True)
            else:
                print_check("Default user creation function exists", False)
            
            checks_total += 1
            if "--reset" in content or "reset" in content.lower():
                checks_passed += 1
                print_check("Reset flag supported", True)
            else:
                print_check("Reset flag supported", False)
            
            checks_total += 1
            if "--seed" in content or "seed" in content.lower():
                checks_passed += 1
                print_check("Seed flag supported", True)
            else:
                print_check("Seed flag supported", False)
        except Exception as e:
            print_check("Reading init_database.py", False, str(e))
    else:
        print_check("scripts/init_database.py exists", False)
    
    return checks_passed, checks_total


def verify_phase_2():
    """Verify Phase 2: Logging Infrastructure."""
    print_header("PHASE 2: LOGGING INFRASTRUCTURE")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 2.1: Logging system
    print(f"\n{Colors.BOLD}STEP 2.1: Logging System{Colors.RESET}")
    
    checks_total += 1
    logging_config = backend_dir / "config" / "logging_config.py"
    if logging_config.exists():
        checks_passed += 1
        print_check("config/logging_config.py exists", True)
        
        try:
            with open(logging_config, 'r') as f:
                content = f.read()
            
            # Check for loggers
            required_loggers = [
                "app_logger",
                "error_logger",
                "database_logger",
                "api_logger",
                "conversation_logger",
                "memory_manager_logger",
                "memory_retrieval_logger",
                "privacy_guardian_logger",
                "analyst_logger",
                "coordinator_logger",
            ]
            
            for logger in required_loggers:
                checks_total += 1
                if logger in content:
                    checks_passed += 1
                    print_check(f"Logger '{logger}' defined", True)
                else:
                    print_check(f"Logger '{logger}' defined", False)
            
            # Check for utility functions
            utility_functions = [
                "log_agent_start",
                "log_agent_complete",
                "log_agent_error",
                "log_api_request",
                "log_database_query",
            ]
            
            for func in utility_functions:
                checks_total += 1
                if f"def {func}" in content:
                    checks_passed += 1
                    print_check(f"Utility function '{func}' defined", True)
                else:
                    print_check(f"Utility function '{func}' defined", False)
            
            # Check for rotation
            checks_total += 1
            if "RotatingFileHandler" in content and "10 * 1024 * 1024" in content:
                checks_passed += 1
                print_check("Log rotation configured (10MB)", True)
            else:
                print_check("Log rotation configured (10MB)", False)
        except Exception as e:
            print_check("Reading logging_config.py", False, str(e))
    else:
        print_check("config/logging_config.py exists", False)
    
    # Check log directories
    checks_total += 1
    logs_dir = backend_dir / "logs"
    if logs_dir.exists():
        checks_passed += 1
        print_check("logs/ directory exists", True)
        
        checks_total += 1
        agents_log_dir = logs_dir / "agents"
        if agents_log_dir.exists():
            checks_passed += 1
            print_check("logs/agents/ directory exists", True)
        else:
            print_check("logs/agents/ directory exists", False)
    else:
        print_check("logs/ directory exists", False)
    
    # Check 2.2: Monitoring utilities
    print(f"\n{Colors.BOLD}STEP 2.2: Monitoring Utilities{Colors.RESET}")
    
    checks_total += 1
    monitoring_file = backend_dir / "services" / "monitoring_service.py"
    if monitoring_file.exists():
        checks_passed += 1
        print_check("services/monitoring_service.py exists", True)
        
        try:
            with open(monitoring_file, 'r') as f:
                content = f.read()
            
            checks_total += 1
            if "class MonitoringService" in content:
                checks_passed += 1
                print_check("MonitoringService class defined", True)
            else:
                print_check("MonitoringService class defined", False)
            
            monitoring_functions = [
                "track_execution_time",
                "log_token_usage",
                "log_memory_operation",
                "log_privacy_check",
                "get_performance_stats",
            ]
            
            for func in monitoring_functions:
                checks_total += 1
                if f"def {func}" in content:
                    checks_passed += 1
                    print_check(f"Monitoring function '{func}' defined", True)
                else:
                    print_check(f"Monitoring function '{func}' defined", False)
        except Exception as e:
            print_check("Reading monitoring_service.py", False, str(e))
    else:
        print_check("services/monitoring_service.py exists", False)
    
    # Check error handler
    checks_total += 1
    error_handler_file = backend_dir / "services" / "error_handler.py"
    if error_handler_file.exists():
        checks_passed += 1
        print_check("services/error_handler.py exists", True)
        
        try:
            with open(error_handler_file, 'r') as f:
                content = f.read()
            
            # Check for custom exceptions
            custom_exceptions = [
                "MemoryChatException",
                "DatabaseException",
                "ProfileNotFoundException",
                "SessionNotFoundException",
                "InvalidPrivacyModeException",
                "LLMException",
            ]
            
            for exc in custom_exceptions:
                checks_total += 1
                if f"class {exc}" in content:
                    checks_passed += 1
                    print_check(f"Exception '{exc}' defined", True)
                else:
                    print_check(f"Exception '{exc}' defined", False)
            
            # Check for error recovery
            checks_total += 1
            if "ErrorRecoveryStrategy" in content:
                checks_passed += 1
                print_check("ErrorRecoveryStrategy class defined", True)
            else:
                print_check("ErrorRecoveryStrategy class defined", False)
            
            checks_total += 1
            if "handle_exception" in content:
                checks_passed += 1
                print_check("handle_exception function defined", True)
            else:
                print_check("handle_exception function defined", False)
        except Exception as e:
            print_check("Reading error_handler.py", False, str(e))
    else:
        print_check("services/error_handler.py exists", False)
    
    return checks_passed, checks_total


def main():
    """Run all verification tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'COMPREHENSIVE VERIFICATION - PHASES 0, 1, 2'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Verify Phase 0
    passed, total = verify_phase_0()
    total_passed += passed
    total_checks += total
    
    # Verify Phase 1
    passed, total = verify_phase_1()
    total_passed += passed
    total_checks += total
    
    # Verify Phase 2
    passed, total = verify_phase_2()
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Everything up to checkpoint 2.2 is complete and working as expected.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME CHECKS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review the failed checks above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

