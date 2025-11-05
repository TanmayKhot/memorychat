#!/usr/bin/env python3
"""
Comprehensive verification script for Phase 1 Checkpoint 1.
Tests all database functionality as specified in the plan.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory so .env file is found
os.chdir(backend_dir)

from database.database import (
    SessionLocal,
    create_all_tables,
    get_database_path,
    engine
)
from services.database_service import DatabaseService
from services.vector_service import VectorService
from database.models import (
    User, MemoryProfile, ChatSession, ChatMessage, Memory, AgentLog
)
from sqlalchemy import inspect, text


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_test(name, passed=True, details=""):
    """Print test result."""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} {name}")
    if details:
        print(f"      {details}")


def verify_sqlite_database():
    """Verify SQLite database is working."""
    print_header("1. SQLite Database Working")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1.1: Database file exists
    tests_total += 1
    db_path = get_database_path()
    if os.path.exists(db_path):
        print_test("Database file exists", True, f"Path: {db_path}")
        tests_passed += 1
    else:
        print_test("Database file exists", False, f"Path: {db_path}")
    
    # Test 1.2: Can connect to database
    tests_total += 1
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print_test("Can connect to database", True)
        tests_passed += 1
    except Exception as e:
        print_test("Can connect to database", False, str(e))
    
    # Test 1.3: Database integrity check
    tests_total += 1
    try:
        db = SessionLocal()
        result = db.execute(text("PRAGMA integrity_check"))
        integrity = result.scalar()
        db.close()
        if integrity == "ok":
            print_test("Database integrity check", True)
            tests_passed += 1
        else:
            print_test("Database integrity check", False, integrity)
    except Exception as e:
        print_test("Database integrity check", False, str(e))
    
    return tests_passed, tests_total


def verify_all_tables_created():
    """Verify all tables are created."""
    print_header("2. All Tables Created")
    
    tests_passed = 0
    tests_total = 0
    
    expected_tables = [
        "users",
        "memory_profiles",
        "chat_sessions",
        "chat_messages",
        "memories",
        "agent_logs"
    ]
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        for table in expected_tables:
            tests_total += 1
            if table in existing_tables:
                print_test(f"Table '{table}' exists", True)
                tests_passed += 1
            else:
                print_test(f"Table '{table}' exists", False)
        
        # Check for unexpected tables
        unexpected = [t for t in existing_tables if t not in expected_tables and not t.startswith("sqlite_")]
        if unexpected:
            print(f"  {Colors.YELLOW}⚠ Note: Unexpected tables found: {unexpected}{Colors.RESET}")
    
    except Exception as e:
        print_test("Table inspection", False, str(e))
    
    return tests_passed, tests_total


def verify_crud_operations():
    """Verify CRUD operations are functional."""
    print_header("3. CRUD Operations Functional")
    
    tests_passed = 0
    tests_total = 0
    db = SessionLocal()
    service = DatabaseService(db)
    
    try:
        # Test CREATE operations
        print(f"\n  {Colors.BOLD}CREATE Operations:{Colors.RESET}")
        
        # Create test user
        tests_total += 1
        try:
            test_user = service.create_user(
                email="test_verify@example.com",
                username="test_verify_user"
            )
            print_test("Create user", True, f"User ID: {test_user.id}")
            tests_passed += 1
        except Exception as e:
            print_test("Create user", False, str(e))
            test_user = None
        
        if test_user:
            # Create memory profile
            tests_total += 1
            try:
                test_profile = service.create_memory_profile(
                    user_id=test_user.id,
                    name="Test Profile",
                    description="Test profile for verification",
                    is_default=True
                )
                print_test("Create memory profile", True, f"Profile ID: {test_profile.id}")
                tests_passed += 1
            except Exception as e:
                print_test("Create memory profile", False, str(e))
                test_profile = None
            
            if test_profile:
                # Create session
                tests_total += 1
                try:
                    test_session = service.create_session(
                        user_id=test_user.id,
                        memory_profile_id=test_profile.id,
                        privacy_mode="normal",
                        title="Test Session"
                    )
                    print_test("Create session", True, f"Session ID: {test_session.id}")
                    tests_passed += 1
                except Exception as e:
                    print_test("Create session", False, str(e))
                    test_session = None
                
                if test_session:
                    # Create message
                    tests_total += 1
                    try:
                        test_message = service.create_message(
                            session_id=test_session.id,
                            role="user",
                            content="Test message for verification",
                            metadata={"test": True}
                        )
                        print_test("Create message", True, f"Message ID: {test_message.id}")
                        tests_passed += 1
                    except Exception as e:
                        print_test("Create message", False, str(e))
                        test_message = None
                    
                    # Create memory
                    tests_total += 1
                    try:
                        test_memory = service.create_memory(
                            user_id=test_user.id,
                            profile_id=test_profile.id,
                            content="Test memory for verification",
                            importance_score=0.7,
                            memory_type="fact",
                            tags=["test", "verification"]
                        )
                        print_test("Create memory", True, f"Memory ID: {test_memory.id}")
                        tests_passed += 1
                    except Exception as e:
                        print_test("Create memory", False, str(e))
                        test_memory = None
                    
                    # Create agent log
                    tests_total += 1
                    try:
                        test_log = service.log_agent_action(
                            session_id=test_session.id,
                            agent_name="TestAgent",
                            action="verify",
                            input_data={"test": True},
                            output_data={"result": "success"},
                            execution_time_ms=50,
                            status="success"
                        )
                        print_test("Create agent log", True, f"Log ID: {test_log.id}")
                        tests_passed += 1
                    except Exception as e:
                        print_test("Create agent log", False, str(e))
        
        # Test READ operations
        print(f"\n  {Colors.BOLD}READ Operations:{Colors.RESET}")
        
        tests_total += 1
        try:
            user = service.get_user_by_email("test_verify@example.com")
            if user:
                print_test("Read user by email", True, f"Found: {user.username}")
                tests_passed += 1
            else:
                print_test("Read user by email", False)
        except Exception as e:
            print_test("Read user by email", False, str(e))
        
        if test_user:
            tests_total += 1
            try:
                profiles = service.get_memory_profiles_by_user(test_user.id)
                print_test("Read memory profiles by user", True, f"Found {len(profiles)} profiles")
                tests_passed += 1
            except Exception as e:
                print_test("Read memory profiles by user", False, str(e))
            
            tests_total += 1
            try:
                sessions = service.get_sessions_by_user(test_user.id)
                print_test("Read sessions by user", True, f"Found {len(sessions)} sessions")
                tests_passed += 1
            except Exception as e:
                print_test("Read sessions by user", False, str(e))
        
        # Test UPDATE operations
        print(f"\n  {Colors.BOLD}UPDATE Operations:{Colors.RESET}")
        
        if test_user:
            tests_total += 1
            try:
                updated = service.update_user(test_user.id, username="updated_verify_user")
                if updated and updated.username == "updated_verify_user":
                    print_test("Update user", True)
                    tests_passed += 1
                else:
                    print_test("Update user", False)
            except Exception as e:
                print_test("Update user", False, str(e))
        
        if test_profile:
            tests_total += 1
            try:
                updated = service.update_memory_profile(test_profile.id, description="Updated description")
                if updated:
                    print_test("Update memory profile", True)
                    tests_passed += 1
                else:
                    print_test("Update memory profile", False)
            except Exception as e:
                print_test("Update memory profile", False, str(e))
        
        # Test DELETE operations
        print(f"\n  {Colors.BOLD}DELETE Operations:{Colors.RESET}")
        
        if test_memory:
            tests_total += 1
            try:
                deleted = service.delete_memory(test_memory.id)
                if deleted:
                    print_test("Delete memory", True)
                    tests_passed += 1
                else:
                    print_test("Delete memory", False)
            except Exception as e:
                print_test("Delete memory", False, str(e))
        
        # Cleanup test data
        if test_session:
            try:
                service.delete_session(test_session.id)
            except:
                pass
        
        if test_profile:
            try:
                # Need to create another profile first to delete test profile
                another_profile = service.create_memory_profile(
                    user_id=test_user.id,
                    name="Another Profile",
                    is_default=False
                )
                service.delete_memory_profile(test_profile.id)
            except:
                pass
        
        if test_user:
            try:
                db.query(User).filter(User.id == test_user.id).delete()
                db.commit()
            except:
                pass
    
    finally:
        db.close()
    
    return tests_passed, tests_total


def verify_chromadb_integration():
    """Verify ChromaDB integration."""
    print_header("4. ChromaDB Integrated")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 4.1: ChromaDB initialization
    tests_total += 1
    try:
        vector_service = VectorService()
        info = vector_service.get_collection_info()
        print_test("ChromaDB initialization", True, f"Collection: {info['collection_name']}")
        tests_passed += 1
    except Exception as e:
        if "OPENAI_API_KEY" in str(e):
            print_test("ChromaDB initialization", False, "API key not configured (expected if not set)")
        else:
            print_test("ChromaDB initialization", False, str(e))
        return tests_passed, tests_total
    
    # Test 4.2: Can add embeddings
    tests_total += 1
    try:
        success = vector_service.add_memory_embedding(
            memory_id=99999,
            content="Test memory for ChromaDB verification",
            metadata={
                "memory_profile_id": "1",
                "user_id": "1",
                "test": "true"
            }
        )
        if success:
            print_test("Add memory embedding", True)
            tests_passed += 1
        else:
            print_test("Add memory embedding", False)
    except Exception as e:
        print_test("Add memory embedding", False, str(e))
    
    # Test 4.3: Can search embeddings
    tests_total += 1
    try:
        results = vector_service.search_similar_memories(
            query="test memory",
            profile_id=1,
            n_results=5
        )
        print_test("Search similar memories", True, f"Found {len(results)} results")
        tests_passed += 1
    except Exception as e:
        print_test("Search similar memories", False, str(e))
    
    # Test 4.4: Can get by ID
    tests_total += 1
    try:
        memory = vector_service.get_memory_by_id(99999)
        if memory:
            print_test("Get memory by ID", True)
            tests_passed += 1
        else:
            print_test("Get memory by ID", False)
    except Exception as e:
        print_test("Get memory by ID", False, str(e))
    
    # Test 4.5: Can delete embeddings
    tests_total += 1
    try:
        success = vector_service.delete_memory_embedding(99999)
        if success:
            print_test("Delete memory embedding", True)
            tests_passed += 1
        else:
            print_test("Delete memory embedding", False)
    except Exception as e:
        print_test("Delete memory embedding", False, str(e))
    
    return tests_passed, tests_total


def verify_data_storage_retrieval():
    """Verify can store and retrieve data."""
    print_header("5. Can Store and Retrieve Data")
    
    tests_passed = 0
    tests_total = 0
    db = SessionLocal()
    service = DatabaseService(db)
    
    try:
        # Test data persistence
        tests_total += 1
        try:
            # Clean up any existing test data first
            existing_user = service.get_user_by_email("persist_test@example.com")
            if existing_user:
                # Delete existing user and related data
                profiles = service.get_memory_profiles_by_user(existing_user.id)
                for p in profiles:
                    try:
                        if len(profiles) > 1:
                            service.delete_memory_profile(p.id)
                        else:
                            # Create temp profile to allow deletion
                            temp = service.create_memory_profile(
                                user_id=existing_user.id,
                                name="Temp",
                                is_default=False
                            )
                            service.delete_memory_profile(p.id)
                    except:
                        pass
                db.query(User).filter(User.id == existing_user.id).delete()
                db.commit()
            
            # Create data
            user = service.create_user(
                email="persist_test@example.com",
                username="persist_user"
            )
            user_id = user.id  # Store ID before closing
            
            profile = service.create_memory_profile(
                user_id=user_id,
                name="Persist Profile",
                is_default=True
            )
            profile_id = profile.id if profile else None
            
            # Close and reopen connection
            db.close()
            db = SessionLocal()
            service = DatabaseService(db)
            
            # Retrieve data
            retrieved_user = service.get_user_by_email("persist_test@example.com")
            if retrieved_user and retrieved_user.id == user_id:
                print_test("Data persistence", True, "Data persists across connections")
                tests_passed += 1
            else:
                print_test("Data persistence", False)
            
            # Cleanup
            if profile_id:
                try:
                    another = service.create_memory_profile(
                        user_id=user_id,
                        name="Temp",
                        is_default=False
                    )
                    service.delete_memory_profile(profile_id)
                except:
                    pass
            
            db.query(User).filter(User.id == user_id).delete()
            db.commit()
        
        except Exception as e:
            print_test("Data persistence", False, str(e))
        
        # Test foreign key relationships
        tests_total += 1
        try:
            user = service.get_user_by_email("demo@local")
            if user:
                profiles = service.get_memory_profiles_by_user(user.id)
                sessions = service.get_sessions_by_user(user.id)
                
                if profiles or sessions:
                    print_test("Foreign key relationships", True, 
                              f"User has {len(profiles)} profiles, {len(sessions)} sessions")
                    tests_passed += 1
                else:
                    print_test("Foreign key relationships", False, "No relationships found")
            else:
                print_test("Foreign key relationships", False, "Demo user not found")
        except Exception as e:
            print_test("Foreign key relationships", False, str(e))
        
        # Test data retrieval with filters
        tests_total += 1
        try:
            user = service.get_user_by_email("demo@local")
            if user:
                default_profile = service.get_default_profile(user.id)
                if default_profile:
                    memories = service.get_memories_by_profile(default_profile.id)
                    print_test("Filtered data retrieval", True, 
                              f"Found {len(memories)} memories for profile")
                    tests_passed += 1
                else:
                    print_test("Filtered data retrieval", False, "No default profile")
            else:
                print_test("Filtered data retrieval", False, "Demo user not found")
        except Exception as e:
            print_test("Filtered data retrieval", False, str(e))
    
    finally:
        db.close()
    
    return tests_passed, tests_total


def verify_ready_for_agent_layer():
    """Verify ready for agent layer."""
    print_header("6. Ready for Agent Layer")
    
    tests_passed = 0
    tests_total = 0
    
    # Test that all required models exist
    tests_total += 1
    try:
        models = [User, MemoryProfile, ChatSession, ChatMessage, Memory, AgentLog]
        all_exist = all(model is not None for model in models)
        if all_exist:
            print_test("All models available", True, f"{len(models)} models")
            tests_passed += 1
        else:
            print_test("All models available", False)
    except Exception as e:
        print_test("All models available", False, str(e))
    
    # Test that database service has all methods
    tests_total += 1
    try:
        required_methods = [
            'create_user', 'get_user_by_id',
            'create_memory_profile', 'get_memory_profiles_by_user',
            'create_session', 'get_session_by_id',
            'create_message', 'get_messages_by_session',
            'create_memory', 'get_memories_by_profile',
            'log_agent_action', 'get_logs_by_session'
        ]
        db = SessionLocal()
        service = DatabaseService(db)
        
        missing = [m for m in required_methods if not hasattr(service, m)]
        if not missing:
            print_test("DatabaseService has all required methods", True, 
                      f"{len(required_methods)} methods")
            tests_passed += 1
        else:
            print_test("DatabaseService has all required methods", False, 
                      f"Missing: {missing}")
        db.close()
    except Exception as e:
        print_test("DatabaseService has all required methods", False, str(e))
    
    return tests_passed, tests_total


def main():
    """Run all verification tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("PHASE 1 CHECKPOINT 1 VERIFICATION".center(70))
    print("=" * 70)
    print(f"{Colors.RESET}")
    
    total_passed = 0
    total_tests = 0
    
    # Run all verification tests
    passed, total = verify_sqlite_database()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_all_tables_created()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_crud_operations()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_chromadb_integration()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_data_storage_retrieval()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_ready_for_agent_layer()
    total_passed += passed
    total_tests += total
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"  Tests Passed: {Colors.GREEN}{total_passed}{Colors.RESET} / {total_tests}")
    print(f"  Success Rate: {Colors.GREEN}{percentage:.1f}%{Colors.RESET}")
    
    if total_passed == total_tests:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED - CHECKPOINT 1 VERIFIED{Colors.RESET}")
    else:
        print(f"\n  {Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED - REVIEW OUTPUT ABOVE{Colors.RESET}")
    
    print()


if __name__ == "__main__":
    main()

