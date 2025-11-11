"""
Database connection and session management for MemoryChat Multi-Agent application.
"""
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config.settings import settings
from database.models import Base


# Get database path from settings
def get_database_path() -> str:
    """Get the absolute path to the SQLite database file."""
    db_path = settings.SQLITE_DATABASE_PATH
    
    # Handle relative paths
    if not os.path.isabs(db_path):
        # Get the backend directory (parent of database directory)
        backend_dir = Path(__file__).parent.parent
        db_path = backend_dir / db_path
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    return str(db_path)


# Create database engine
# SQLite requires special configuration for foreign keys and connection pooling
database_url = f"sqlite:///{get_database_path()}"
engine = create_engine(
    database_url,
    connect_args={
        "check_same_thread": False,  # Needed for SQLite with multiple threads
    },
    poolclass=StaticPool,  # SQLite doesn't support connection pooling, use StaticPool
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_all_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database tables created at: {get_database_path()}")


def drop_all_tables():
    """Drop all database tables. Use with caution!"""
    Base.metadata.drop_all(bind=engine)
    print("✓ All database tables dropped")


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for getting database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_indexes():
    """Create database indexes for performance optimization."""
    from sqlalchemy import text
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON chat_sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_messages_session_id ON chat_messages(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_memories_profile_id ON memories(memory_profile_id)",
        "CREATE INDEX IF NOT EXISTS idx_agent_logs_session_id ON agent_logs(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON chat_messages(created_at)",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
            except Exception as e:
                print(f"Warning: Failed to create index: {e}")
    
    print("✓ Database indexes created")


def init_db():
    """Initialize the database by creating all tables and indexes."""
    create_all_tables()
    create_indexes()
    print("✓ Database initialized successfully")

