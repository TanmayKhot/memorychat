#!/usr/bin/env python3
"""
Database initialization script for MemoryChat Multi-Agent application.
Creates database tables, default user, and initializes ChromaDB.
"""
import sys
import os
import argparse
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory so .env file is found
os.chdir(backend_dir)

from database.database import (
    create_all_tables,
    drop_all_tables,
    SessionLocal,
    get_database_path
)
from services.database_service import DatabaseService
from services.vector_service import VectorService


def create_default_user(db_service: DatabaseService):
    """Create default demo user and memory profile."""
    try:
        # Check if demo user already exists
        demo_user = db_service.get_user_by_email("demo@local")
        
        if demo_user:
            print(f"  Demo user already exists (ID: {demo_user.id})")
            return demo_user
        
        # Create demo user
        demo_user = db_service.create_user(
            email="demo@local",
            username="demo"
        )
        print(f"  ✓ Created demo user: {demo_user.username} (ID: {demo_user.id})")
        
        # Create default memory profile
        default_profile = db_service.create_memory_profile(
            user_id=demo_user.id,
            name="Default Profile",
            description="Default memory profile for demo user",
            is_default=True,
            system_prompt="You are a helpful AI assistant with a good memory.",
            personality_traits={
                "tone": "friendly",
                "verbosity": "balanced",
                "formality": "casual"
            }
        )
        print(f"  ✓ Created default memory profile: {default_profile.name} (ID: {default_profile.id})")
        
        return demo_user
    
    except Exception as e:
        raise RuntimeError(f"Failed to create default user: {str(e)}") from e


def seed_sample_data(db_service: DatabaseService, user_id: int):
    """Seed sample data for testing."""
    try:
        print("\n  Seeding sample data...")
        
        # Get default profile
        default_profile = db_service.get_default_profile(user_id)
        if not default_profile:
            print("  ⚠ No default profile found, skipping seed data")
            return
        
        # Create a sample chat session
        session = db_service.create_session(
            user_id=user_id,
            memory_profile_id=default_profile.id,
            privacy_mode="normal",
            title="Sample Conversation"
        )
        print(f"  ✓ Created sample session (ID: {session.id})")
        
        # Add sample messages
        messages = [
            ("user", "Hello! I'm interested in learning Python."),
            ("assistant", "That's great! Python is an excellent programming language. What would you like to learn about Python?"),
            ("user", "I want to build web applications."),
            ("assistant", "Perfect! For web applications in Python, I'd recommend learning Flask or Django. Flask is great for beginners, while Django is more feature-rich."),
        ]
        
        for role, content in messages:
            db_service.create_message(
                session_id=session.id,
                role=role,
                content=content,
                agent_name="ConversationAgent" if role == "assistant" else None
            )
        
        print(f"  ✓ Added {len(messages)} sample messages")
        
        # Create sample memories
        sample_memories = [
            {
                "content": "User is interested in learning Python programming",
                "importance_score": 0.8,
                "memory_type": "preference",
                "tags": ["programming", "python", "learning"]
            },
            {
                "content": "User wants to build web applications",
                "importance_score": 0.7,
                "memory_type": "preference",
                "tags": ["web-development", "applications"]
            },
        ]
        
        vector_service = VectorService()
        for memory_data in sample_memories:
            memory = db_service.create_memory(
                user_id=user_id,
                profile_id=default_profile.id,
                **memory_data
            )
            
            # Add to vector database
            vector_service.add_memory_embedding(
                memory_id=memory.id,
                content=memory.content,
                metadata={
                    "memory_profile_id": str(default_profile.id),
                    "user_id": str(user_id),
                    "memory_type": memory.memory_type,
                    "importance_score": str(memory.importance_score)
                }
            )
        
        print(f"  ✓ Created {len(sample_memories)} sample memories")
        print("  ✓ Sample data seeded successfully")
    
    except Exception as e:
        print(f"  ⚠ Failed to seed sample data: {str(e)}")
        # Don't raise - seeding is optional


def initialize_chromadb():
    """Initialize ChromaDB vector database."""
    try:
        print("\n  Initializing ChromaDB...")
        vector_service = VectorService()
        info = vector_service.get_collection_info()
        print(f"  ✓ ChromaDB initialized: {info['collection_name']} ({info['count']} memories)")
        return True
    except Exception as e:
        print(f"  ⚠ ChromaDB initialization warning: {str(e)}")
        print("     (This is okay if OPENAI_API_KEY is not set)")
        return False


def main():
    """Main initialization function."""
    parser = argparse.ArgumentParser(
        description="Initialize MemoryChat database and tables"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables and recreate them"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Add sample data for testing"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MemoryChat Database Initialization")
    print("=" * 60)
    
    db = SessionLocal()
    db_service = DatabaseService(db)
    
    try:
        # Reset database if requested
        if args.reset:
            print("\n  Resetting database...")
            drop_all_tables()
            print("  ✓ All tables dropped")
        
        # Create database and tables
        print("\n  Creating database tables...")
        create_all_tables()
        print(f"  ✓ Database created at: {get_database_path()}")
        
        # Create default user and profile
        print("\n  Creating default user and profile...")
        demo_user = create_default_user(db_service)
        
        # Initialize ChromaDB
        chromadb_ok = initialize_chromadb()
        
        # Seed sample data if requested
        if args.seed:
            seed_sample_data(db_service, demo_user.id)
        
        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
        print(f"\n  Database: {get_database_path()}")
        print(f"  Demo User: demo@local (ID: {demo_user.id})")
        if chromadb_ok:
            print("  ChromaDB: Initialized")
        else:
            print("  ChromaDB: Not initialized (API key required)")
        print("\n  You can now start the application.")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

