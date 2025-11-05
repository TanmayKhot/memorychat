#!/usr/bin/env python3
"""
Interactive database inspector script for MemoryChat.
Allows you to view schemas, query data, and inspect the database.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory so .env file is found
os.chdir(backend_dir)

from database.database import SessionLocal, get_database_path
from services.database_service import DatabaseService
from database.models import User, MemoryProfile, ChatSession, ChatMessage, Memory, AgentLog
from sqlalchemy import inspect


def print_separator():
    """Print a separator line."""
    print("=" * 70)


def show_table_schema(db, table_name, model_class):
    """Show schema for a table."""
    print_separator()
    print(f"\nSchema for table: {table_name}")
    print_separator()
    
    inspector = inspect(db.bind)
    columns = inspector.get_columns(table_name)
    
    print(f"\n{'Column Name':<25} {'Type':<20} {'Nullable':<10} {'Default'}")
    print("-" * 70)
    
    for col in columns:
        nullable = "YES" if col.get('nullable', True) else "NO"
        default = str(col.get('default', ''))[:20] if col.get('default') else ''
        col_type = str(col['type'])
        print(f"{col['name']:<25} {col_type:<20} {nullable:<10} {default}")
    
    # Show indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print(f"\nIndexes:")
        for idx in indexes:
            cols = ', '.join(idx['column_names'])
            unique = "UNIQUE" if idx.get('unique') else ""
            print(f"  - {idx['name']}: ({cols}) {unique}")
    
    # Show foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print(f"\nForeign Keys:")
        for fk in fks:
            print(f"  - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")


def show_table_data(db, model_class, limit=10):
    """Show data from a table."""
    print_separator()
    print(f"\nData from table: {model_class.__tablename__}")
    print_separator()
    
    records = db.query(model_class).limit(limit).all()
    
    if not records:
        print("  (No records found)")
        return
    
    print(f"\nFound {len(records)} record(s):\n")
    
    for i, record in enumerate(records, 1):
        print(f"Record {i}:")
        record_dict = record.to_dict() if hasattr(record, 'to_dict') else {}
        for key, value in record_dict.items():
            if value is not None:
                if isinstance(value, str) and len(value) > 60:
                    value = value[:60] + "..."
                print(f"  {key}: {value}")
        print()


def show_table_counts(db):
    """Show record counts for all tables."""
    print_separator()
    print("\nRecord Counts")
    print_separator()
    
    tables = [
        ("users", User),
        ("memory_profiles", MemoryProfile),
        ("chat_sessions", ChatSession),
        ("chat_messages", ChatMessage),
        ("memories", Memory),
        ("agent_logs", AgentLog)
    ]
    
    print(f"\n{'Table':<25} {'Count':<10}")
    print("-" * 40)
    
    for table_name, model_class in tables:
        count = db.query(model_class).count()
        print(f"{table_name:<25} {count:<10}")


def show_relationships(db, service):
    """Show relationships between tables."""
    print_separator()
    print("\nRelationship Data")
    print_separator()
    
    # Get demo user
    user = service.get_user_by_email("demo@local")
    if not user:
        print("\n  Demo user not found. Run init_database.py first.")
        return
    
    print(f"\nUser: {user.username} (ID: {user.id})")
    
    # Get profiles
    profiles = service.get_memory_profiles_by_user(user.id)
    print(f"\n  Memory Profiles: {len(profiles)}")
    for profile in profiles:
        memories_count = db.query(Memory).filter(Memory.memory_profile_id == profile.id).count()
        print(f"    - {profile.name} (ID: {profile.id}, Default: {profile.is_default})")
        print(f"      Memories: {memories_count}")
    
    # Get sessions
    sessions = service.get_sessions_by_user(user.id)
    print(f"\n  Chat Sessions: {len(sessions)}")
    for session in sessions:
        messages_count = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count()
        logs_count = db.query(AgentLog).filter(AgentLog.session_id == session.id).count()
        print(f"    - Session {session.id}: {session.title or 'Untitled'}")
        print(f"      Privacy Mode: {session.privacy_mode}")
        print(f"      Messages: {messages_count}, Logs: {logs_count}")


def show_detailed_query(db, service):
    """Show detailed query results."""
    print_separator()
    print("\nDetailed Query Results")
    print_separator()
    
    user = service.get_user_by_email("demo@local")
    if not user:
        print("\n  Demo user not found.")
        return
    
    # Show complete conversation context
    sessions = service.get_sessions_by_user(user.id, limit=1)
    if sessions:
        session = sessions[0]
        print(f"\nSession: {session.title or 'Untitled'} (ID: {session.id})")
        print(f"Privacy Mode: {session.privacy_mode}")
        
        messages = service.get_messages_by_session(session.id)
        print(f"\nMessages ({len(messages)}):")
        for msg in messages:
            agent_info = f" [{msg.agent_name}]" if msg.agent_name else ""
            print(f"  [{msg.role}]{agent_info}: {msg.content[:80]}...")


def main():
    """Main menu."""
    db = SessionLocal()
    service = DatabaseService(db)
    
    print("\n" + "=" * 70)
    print("MemoryChat Database Inspector")
    print("=" * 70)
    print(f"\nDatabase: {get_database_path()}")
    
    while True:
        print("\n" + "=" * 70)
        print("Menu:")
        print("  1. Show table schemas")
        print("  2. Show table data")
        print("  3. Show record counts")
        print("  4. Show relationships")
        print("  5. Show detailed query")
        print("  6. Exit")
        print("=" * 70)
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            print("\nAvailable tables:")
            tables = [
                ("users", User),
                ("memory_profiles", MemoryProfile),
                ("chat_sessions", ChatSession),
                ("chat_messages", ChatMessage),
                ("memories", Memory),
                ("agent_logs", AgentLog)
            ]
            
            for i, (name, _) in enumerate(tables, 1):
                print(f"  {i}. {name}")
            
            table_choice = input("\nEnter table number (1-6) or 'all': ").strip().lower()
            
            if table_choice == "all":
                for name, model in tables:
                    show_table_schema(db, name, model)
            else:
                try:
                    idx = int(table_choice) - 1
                    if 0 <= idx < len(tables):
                        name, model = tables[idx]
                        show_table_schema(db, name, model)
                    else:
                        print("Invalid choice")
                except ValueError:
                    print("Invalid choice")
        
        elif choice == "2":
            print("\nAvailable tables:")
            tables = [
                ("users", User),
                ("memory_profiles", MemoryProfile),
                ("chat_sessions", ChatSession),
                ("chat_messages", ChatMessage),
                ("memories", Memory),
                ("agent_logs", AgentLog)
            ]
            
            for i, (name, _) in enumerate(tables, 1):
                print(f"  {i}. {name}")
            
            table_choice = input("\nEnter table number (1-6): ").strip()
            
            try:
                idx = int(table_choice) - 1
                if 0 <= idx < len(tables):
                    _, model = tables[idx]
                    limit = input("Limit (default 10): ").strip()
                    limit = int(limit) if limit else 10
                    show_table_data(db, model, limit)
                else:
                    print("Invalid choice")
            except ValueError:
                print("Invalid choice")
        
        elif choice == "3":
            show_table_counts(db)
        
        elif choice == "4":
            show_relationships(db, service)
        
        elif choice == "5":
            show_detailed_query(db, service)
        
        elif choice == "6":
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-6.")
    
    db.close()


if __name__ == "__main__":
    main()

