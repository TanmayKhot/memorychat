-- MemoryChat Multi-Agent Database Schema
-- SQLite Database Schema for Local Storage

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- TABLE: users
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: memory_profiles
-- ============================================================================
CREATE TABLE IF NOT EXISTS memory_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT 0,
    personality_traits TEXT,
    system_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);

-- ============================================================================
-- TABLE: chat_sessions
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    memory_profile_id INTEGER,
    privacy_mode TEXT CHECK(privacy_mode IN ('normal', 'incognito', 'pause_memory')) DEFAULT 'normal',
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (memory_profile_id) REFERENCES memory_profiles(id) ON DELETE SET NULL
);

-- ============================================================================
-- TABLE: chat_messages
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT CHECK(role IN ('user', 'assistant', 'system')) NOT NULL,
    content TEXT NOT NULL,
    agent_name TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: memories
-- ============================================================================
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    memory_profile_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    importance_score REAL DEFAULT 0.5,
    memory_type TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mentioned_count INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (memory_profile_id) REFERENCES memory_profiles(id) ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: agent_logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    execution_time_ms INTEGER,
    status TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Index for fast lookup of sessions by user
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON chat_sessions(user_id);

-- Index for fast lookup of messages by session
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON chat_messages(session_id);

-- Index for fast lookup of memories by profile
CREATE INDEX IF NOT EXISTS idx_memories_profile_id ON memories(memory_profile_id);

-- Index for fast lookup of agent logs by session
CREATE INDEX IF NOT EXISTS idx_agent_logs_session_id ON agent_logs(session_id);

