"""
Simple database connectivity and table accessibility test script.
Run this after completing Phase 2 (Database Setup) to verify all tables are accessible.

Usage: python test_database.py
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Tables to test (from Phase 2, Checkpoint 2.2)
TABLES = [
    "users",
    "memory_profiles",
    "chat_sessions",
    "chat_messages",
    "mem0_memories"
]


def test_connection():
    """Test basic connection to Supabase."""
    print("\n=== Testing Supabase Connection ===")
    try:
        if not SUPABASE_URL or SUPABASE_URL == "your_supabase_url_here":
            print("❌ SUPABASE_URL not configured in .env file")
            return None
        
        if not SUPABASE_KEY or SUPABASE_KEY == "your_supabase_service_key_here":
            print("❌ SUPABASE_SERVICE_KEY not configured in .env file")
            return None
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Connected to Supabase at {SUPABASE_URL}")
        return supabase
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return None


def test_table_access(supabase: Client, table_name: str):
    """Test if a table is accessible by attempting to read from it."""
    try:
        # Attempt to select from table (limit 0 to just test access)
        response = supabase.table(table_name).select("*").limit(0).execute()
        print(f"✅ Table '{table_name}' is accessible")
        return True
    except Exception as e:
        print(f"❌ Table '{table_name}' access failed: {str(e)}")
        return False


def test_all_tables(supabase: Client):
    """Test access to all required tables."""
    print("\n=== Testing Table Accessibility ===")
    results = {}
    
    for table in TABLES:
        results[table] = test_table_access(supabase, table)
    
    return results


def print_summary(results: dict):
    """Print test summary."""
    print("\n=== Test Summary ===")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total tables tested: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\nFailed tables:")
        for table, result in results.items():
            if not result:
                print(f"  - {table}")
    
    if passed == total:
        print("\n🎉 All database tables are accessible!")
    else:
        print("\n⚠️  Some tables are not accessible. Please check:")
        print("  1. Have you completed Phase 2 (Database Setup)?")
        print("  2. Have you created all required tables in Supabase?")
        print("  3. Are your Supabase credentials correct in .env?")


def main():
    """Main test function."""
    print("=" * 50)
    print("DATABASE CONNECTIVITY TEST")
    print("=" * 50)
    
    # Test connection
    supabase = test_connection()
    if not supabase:
        print("\n❌ Cannot proceed with tests - connection failed")
        print("\nPlease ensure:")
        print("  1. You have completed Phase 2, Checkpoint 2.1")
        print("  2. Your .env file has valid SUPABASE_URL and SUPABASE_SERVICE_KEY")
        return
    
    # Test all tables
    results = test_all_tables(supabase)
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()

