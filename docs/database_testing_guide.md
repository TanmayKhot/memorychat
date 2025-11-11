# Database Testing and Querying Guide

This guide shows you how to test, query, and inspect the MemoryChat database.

## Quick Start

### 1. Initialize the Database

First, make sure the database is initialized:

```bash
cd memorychat
backend/.venv/bin/python scripts/init_database.py --seed
```

## Method 1: Using SQLite Command Line

### Install SQLite3 (if not already installed)

```bash
# Ubuntu/Debian
sudo apt install sqlite3

# macOS (usually pre-installed)
# Or: brew install sqlite3
```

### Connect to the Database

```bash
cd memorychat
sqlite3 data/sqlite/memorychat.db
```

### View Table Schema

```sql
-- List all tables
.tables

-- View schema for a specific table
.schema users
.schema memory_profiles
.schema chat_sessions
.schema chat_messages
.schema memories
.schema agent_logs

-- View schema for all tables
.schema
```

### View Table Structure (Column Info)

```sql
-- Show column information for a table
PRAGMA table_info(users);
PRAGMA table_info(memory_profiles);
PRAGMA table_info(chat_sessions);
PRAGMA table_info(chat_messages);
PRAGMA table_info(memories);
PRAGMA table_info(agent_logs);
```

### Query Data

```sql
-- View all users
SELECT * FROM users;

-- View all memory profiles
SELECT * FROM memory_profiles;

-- View all chat sessions
SELECT * FROM chat_sessions;

-- View all messages for a session
SELECT * FROM chat_messages WHERE session_id = 1;

-- View all memories for a profile
SELECT * FROM memories WHERE memory_profile_id = 1;

-- View all agent logs
SELECT * FROM agent_logs;

-- Count records in each table
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'memory_profiles', COUNT(*) FROM memory_profiles
UNION ALL
SELECT 'chat_sessions', COUNT(*) FROM chat_sessions
UNION ALL
SELECT 'chat_messages', COUNT(*) FROM chat_messages
UNION ALL
SELECT 'memories', COUNT(*) FROM memories
UNION ALL
SELECT 'agent_logs', COUNT(*) FROM agent_logs;
```

### Useful Queries

```sql
-- Get user with their profiles
SELECT u.id, u.username, u.email, mp.name as profile_name, mp.is_default
FROM users u
LEFT JOIN memory_profiles mp ON u.id = mp.user_id;

-- Get session with user and profile info
SELECT cs.id, u.username, mp.name as profile_name, cs.privacy_mode, cs.title, cs.created_at
FROM chat_sessions cs
JOIN users u ON cs.user_id = u.id
LEFT JOIN memory_profiles mp ON cs.memory_profile_id = mp.id;

-- Get messages for a session with formatting
SELECT 
    cm.id,
    cm.role,
    SUBSTR(cm.content, 1, 50) as content_preview,
    cm.agent_name,
    cm.created_at
FROM chat_messages cm
WHERE cm.session_id = 1
ORDER BY cm.created_at ASC;

-- Get memories with profile info
SELECT 
    m.id,
    m.content,
    m.memory_type,
    m.importance_score,
    m.mentioned_count,
    mp.name as profile_name
FROM memories m
JOIN memory_profiles mp ON m.memory_profile_id = mp.id
ORDER BY m.importance_score DESC;

-- Get agent logs for a session
SELECT 
    al.agent_name,
    al.action,
    al.status,
    al.execution_time_ms,
    al.created_at
FROM agent_logs al
WHERE al.session_id = 1
ORDER BY al.created_at DESC;
```

### Exit SQLite

```sql
.quit
```

## Method 2: Using Python Script

### Run the Database Inspector Script

```bash
cd memorychat
backend/.venv/bin/python scripts/inspect_database.py
```

This script provides an interactive menu to:
- View table schemas
- Query data
- Count records
- View relationships

## Method 3: Using Python Interactively

### Open Python REPL

```bash
cd memorychat/backend
source .venv/bin/activate  # or: .venv/bin/python
python
```

### Query Using SQLAlchemy

```python
from database.database import SessionLocal
from services.database_service import DatabaseService
from database.models import User, MemoryProfile, ChatSession, ChatMessage, Memory, AgentLog

# Create session
db = SessionLocal()
service = DatabaseService(db)

# Get all users
users = db.query(User).all()
for user in users:
    print(f"User: {user.username} ({user.email})")

# Get user with profiles
user = service.get_user_by_email("demo@local")
profiles = service.get_memory_profiles_by_user(user.id)
print(f"\nProfiles for {user.username}:")
for profile in profiles:
    print(f"  - {profile.name} (default: {profile.is_default})")

# Get sessions
sessions = service.get_sessions_by_user(user.id)
print(f"\nSessions: {len(sessions)}")
for session in sessions:
    messages = service.get_messages_by_session(session.id)
    print(f"  Session {session.id}: {len(messages)} messages")

# Get memories
profile = service.get_default_profile(user.id)
memories = service.get_memories_by_profile(profile.id)
print(f"\nMemories: {len(memories)}")
for memory in memories:
    print(f"  - {memory.content[:50]}... (score: {memory.importance_score})")

db.close()
```

## Method 4: View Database File Info

### Check Database File

```bash
cd memorychat
ls -lh data/sqlite/memorychat.db
file data/sqlite/memorychat.db
```

### Database Integrity Check

```bash
sqlite3 data/sqlite/memorychat.db "PRAGMA integrity_check;"
```

### View Indexes

```sql
-- In SQLite console
.indexes

-- Or with query
SELECT name, tbl_name FROM sqlite_master WHERE type='index';
```

## Method 5: Export Data

### Export to CSV

```bash
sqlite3 -header -csv data/sqlite/memorychat.db "SELECT * FROM users;" > users.csv
sqlite3 -header -csv data/sqlite/memorychat.db "SELECT * FROM memory_profiles;" > profiles.csv
```

### Export Schema

```bash
sqlite3 data/sqlite/memorychat.db .schema > schema.sql
```

## Common Testing Scenarios

### Test 1: Verify Default User

```sql
SELECT * FROM users WHERE email = 'demo@local';
-- Should return 1 row
```

### Test 2: Verify Default Profile

```sql
SELECT * FROM memory_profiles WHERE is_default = 1;
-- Should return 1 row
```

### Test 3: Verify Foreign Key Relationships

```sql
-- Check if all sessions have valid user_id
SELECT cs.id, cs.user_id, u.id as user_exists
FROM chat_sessions cs
LEFT JOIN users u ON cs.user_id = u.id
WHERE u.id IS NULL;
-- Should return 0 rows

-- Check if all messages have valid session_id
SELECT cm.id, cm.session_id, cs.id as session_exists
FROM chat_messages cm
LEFT JOIN chat_sessions cs ON cm.session_id = cs.id
WHERE cs.id IS NULL;
-- Should return 0 rows
```

### Test 4: Verify Data Consistency

```sql
-- Check memory profile isolation
SELECT memory_profile_id, COUNT(*) as memory_count
FROM memories
GROUP BY memory_profile_id;

-- Check session message counts
SELECT session_id, COUNT(*) as message_count
FROM chat_messages
GROUP BY session_id;
```

## Troubleshooting

### Database Locked Error

If you get a "database is locked" error:
- Make sure no other process is using the database
- Close any open database connections
- Restart the application if running

### Reset Database

```bash
cd memorychat
rm data/sqlite/memorychat.db
backend/.venv/bin/python scripts/init_database.py --reset --seed
```

## Advanced Queries

### Complex Join Query

```sql
-- Get complete conversation context
SELECT 
    u.username,
    mp.name as profile_name,
    cs.title as session_title,
    cs.privacy_mode,
    cm.role,
    cm.content,
    cm.agent_name,
    cm.created_at
FROM chat_messages cm
JOIN chat_sessions cs ON cm.session_id = cs.id
JOIN users u ON cs.user_id = u.id
LEFT JOIN memory_profiles mp ON cs.memory_profile_id = mp.id
WHERE cs.id = 1
ORDER BY cm.created_at ASC;
```

### Memory Analysis

```sql
-- Analyze memory distribution
SELECT 
    memory_type,
    COUNT(*) as count,
    AVG(importance_score) as avg_importance,
    AVG(mentioned_count) as avg_mentions
FROM memories
GROUP BY memory_type;
```

### Agent Performance

```sql
-- Analyze agent execution times
SELECT 
    agent_name,
    COUNT(*) as execution_count,
    AVG(execution_time_ms) as avg_time_ms,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
FROM agent_logs
GROUP BY agent_name;
```



