# Database Schema Documentation

This document describes the SQLite database schema for the MemoryChat Multi-Agent application.

## Overview

The database stores user data, memory profiles, chat sessions, messages, memories, and agent execution logs. All tables use SQLite with proper foreign key constraints and indexes for performance.

## Tables

### users

Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| email | TEXT | UNIQUE NOT NULL | User email address |
| username | TEXT | UNIQUE NOT NULL | Username |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### memory_profiles

Stores memory profiles for each user. Each user can have multiple profiles with different personalities and system prompts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique profile identifier |
| user_id | INTEGER | REFERENCES users(id) ON DELETE CASCADE | Owner of this profile |
| name | TEXT | NOT NULL | Profile name |
| description | TEXT | | Profile description |
| is_default | BOOLEAN | DEFAULT 0 | Whether this is the default profile |
| personality_traits | TEXT | | JSON string of personality traits |
| system_prompt | TEXT | | Custom system prompt for this profile |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Profile creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Unique Constraint:** (user_id, name) - Each user can have unique profile names.

### chat_sessions

Stores chat session information. Each session belongs to a user and uses a specific memory profile.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique session identifier |
| user_id | INTEGER | REFERENCES users(id) ON DELETE CASCADE | Owner of this session |
| memory_profile_id | INTEGER | REFERENCES memory_profiles(id) ON DELETE SET NULL | Profile used in this session |
| privacy_mode | TEXT | CHECK(privacy_mode IN ('normal', 'incognito', 'pause_memory')) DEFAULT 'normal' | Privacy mode for this session |
| title | TEXT | | Session title |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Session creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Privacy Modes:**
- `normal`: Full memory storage and retrieval
- `incognito`: No memory storage, no memory retrieval
- `pause_memory`: Memory retrieval allowed, but no new memory storage

### chat_messages

Stores individual messages within chat sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique message identifier |
| session_id | INTEGER | REFERENCES chat_sessions(id) ON DELETE CASCADE | Session this message belongs to |
| role | TEXT | CHECK(role IN ('user', 'assistant', 'system')) NOT NULL | Message role |
| content | TEXT | NOT NULL | Message content |
| agent_name | TEXT | | Which agent generated this message (for assistant messages) |
| metadata | TEXT | | JSON string for additional information |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Message creation timestamp |

**Roles:**
- `user`: User message
- `assistant`: AI assistant response
- `system`: System message

### memories

Stores extracted memories from conversations. Memories are associated with a user and a memory profile.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique memory identifier |
| user_id | INTEGER | REFERENCES users(id) ON DELETE CASCADE | Owner of this memory |
| memory_profile_id | INTEGER | REFERENCES memory_profiles(id) ON DELETE CASCADE | Profile this memory belongs to |
| content | TEXT | NOT NULL | Memory content |
| importance_score | REAL | DEFAULT 0.5 | Importance score (0.0 to 1.0) |
| memory_type | TEXT | | Type: fact, preference, event, relationship, etc. |
| tags | TEXT | | JSON array of tags as string |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Memory creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| mentioned_count | INTEGER | DEFAULT 1 | Number of times this memory has been referenced |

### agent_logs

Stores execution logs for agent operations. Used for debugging and monitoring.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique log identifier |
| session_id | INTEGER | REFERENCES chat_sessions(id) | Session this log belongs to |
| agent_name | TEXT | NOT NULL | Name of the agent |
| action | TEXT | NOT NULL | Action performed |
| input_data | TEXT | | JSON string of input data |
| output_data | TEXT | | JSON string of output data |
| execution_time_ms | INTEGER | | Execution time in milliseconds |
| status | TEXT | | Status: success, error, warning |
| error_message | TEXT | | Error message if status is error |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Log creation timestamp |

## Indexes

The following indexes are created for performance optimization:

1. **idx_sessions_user_id** on `chat_sessions(user_id)` - Fast lookup of sessions by user
2. **idx_messages_session_id** on `chat_messages(session_id)` - Fast lookup of messages by session
3. **idx_memories_profile_id** on `memories(memory_profile_id)` - Fast lookup of memories by profile
4. **idx_agent_logs_session_id** on `agent_logs(session_id)` - Fast lookup of logs by session

## Relationships

- Users can have multiple Memory Profiles (one-to-many)
- Users can have multiple Chat Sessions (one-to-many)
- Memory Profiles can have multiple Memories (one-to-many)
- Chat Sessions can have multiple Chat Messages (one-to-many)
- Chat Sessions can have multiple Agent Logs (one-to-many)
- Each Chat Session uses one Memory Profile (many-to-one)
- Each Memory belongs to one User and one Memory Profile (many-to-one)

## Notes

- All timestamps use SQLite's CURRENT_TIMESTAMP
- JSON data is stored as TEXT and should be parsed/validated in application code
- Foreign key constraints ensure referential integrity
- CASCADE deletes ensure data consistency when users or profiles are deleted

