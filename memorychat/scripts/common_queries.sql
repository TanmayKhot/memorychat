-- Common SQL Queries for MemoryChat Database
-- Run these queries using: sqlite3 data/sqlite/memorychat.db < scripts/common_queries.sql
-- Or copy-paste individual queries into sqlite3 console

-- ============================================================================
-- SCHEMA INSPECTION
-- ============================================================================

-- List all tables
.tables

-- View schema for all tables
.schema

-- View schema for specific table
.schema users
.schema memory_profiles
.schema chat_sessions
.schema chat_messages
.schema memories
.schema agent_logs

-- Get column information
PRAGMA table_info(users);
PRAGMA table_info(memory_profiles);
PRAGMA table_info(chat_sessions);
PRAGMA table_info(chat_messages);
PRAGMA table_info(memories);
PRAGMA table_info(agent_logs);

-- List all indexes
SELECT name, tbl_name FROM sqlite_master WHERE type='index';

-- ============================================================================
-- BASIC QUERIES
-- ============================================================================

-- View all users
SELECT * FROM users;

-- View all memory profiles
SELECT * FROM memory_profiles;

-- View all chat sessions
SELECT * FROM chat_sessions;

-- View all messages
SELECT * FROM chat_messages;

-- View all memories
SELECT * FROM memories;

-- View all agent logs
SELECT * FROM agent_logs;

-- ============================================================================
-- RECORD COUNTS
-- ============================================================================

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

-- ============================================================================
-- RELATIONSHIP QUERIES
-- ============================================================================

-- Users with their profiles
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    mp.id as profile_id,
    mp.name as profile_name,
    mp.is_default,
    mp.created_at as profile_created
FROM users u
LEFT JOIN memory_profiles mp ON u.id = mp.user_id
ORDER BY u.id, mp.is_default DESC;

-- Sessions with user and profile info
SELECT 
    cs.id as session_id,
    u.username,
    mp.name as profile_name,
    cs.privacy_mode,
    cs.title,
    cs.created_at,
    (SELECT COUNT(*) FROM chat_messages WHERE session_id = cs.id) as message_count
FROM chat_sessions cs
JOIN users u ON cs.user_id = u.id
LEFT JOIN memory_profiles mp ON cs.memory_profile_id = mp.id
ORDER BY cs.created_at DESC;

-- Messages for a specific session
SELECT 
    cm.id,
    cm.role,
    SUBSTR(cm.content, 1, 100) as content_preview,
    cm.agent_name,
    cm.created_at
FROM chat_messages cm
WHERE cm.session_id = 1
ORDER BY cm.created_at ASC;

-- Memories with profile info
SELECT 
    m.id,
    m.content,
    m.memory_type,
    m.importance_score,
    m.mentioned_count,
    mp.name as profile_name,
    m.created_at
FROM memories m
JOIN memory_profiles mp ON m.memory_profile_id = mp.id
ORDER BY m.importance_score DESC, m.created_at DESC;

-- Agent logs for a session
SELECT 
    al.id,
    al.agent_name,
    al.action,
    al.status,
    al.execution_time_ms,
    al.error_message,
    al.created_at
FROM agent_logs al
WHERE al.session_id = 1
ORDER BY al.created_at DESC;

-- ============================================================================
-- DATA INTEGRITY CHECKS
-- ============================================================================

-- Check for orphaned sessions (sessions without valid user)
SELECT cs.id, cs.user_id
FROM chat_sessions cs
LEFT JOIN users u ON cs.user_id = u.id
WHERE u.id IS NULL;

-- Check for orphaned messages (messages without valid session)
SELECT cm.id, cm.session_id
FROM chat_messages cm
LEFT JOIN chat_sessions cs ON cm.session_id = cs.id
WHERE cs.id IS NULL;

-- Check for orphaned memories (memories without valid profile)
SELECT m.id, m.memory_profile_id
FROM memories m
LEFT JOIN memory_profiles mp ON m.memory_profile_id = mp.id
WHERE mp.id IS NULL;

-- Check for sessions without default profile set
SELECT cs.id, cs.user_id, u.username
FROM chat_sessions cs
JOIN users u ON cs.user_id = u.id
LEFT JOIN memory_profiles mp ON cs.memory_profile_id = mp.id
WHERE mp.id IS NULL;

-- ============================================================================
-- STATISTICS AND ANALYTICS
-- ============================================================================

-- Memory distribution by type
SELECT 
    memory_type,
    COUNT(*) as count,
    ROUND(AVG(importance_score), 2) as avg_importance,
    ROUND(AVG(mentioned_count), 2) as avg_mentions,
    MAX(importance_score) as max_importance
FROM memories
GROUP BY memory_type
ORDER BY count DESC;

-- Session activity by user
SELECT 
    u.username,
    COUNT(DISTINCT cs.id) as session_count,
    COUNT(cm.id) as total_messages,
    COUNT(DISTINCT cs.memory_profile_id) as profiles_used
FROM users u
LEFT JOIN chat_sessions cs ON u.id = cs.user_id
LEFT JOIN chat_messages cm ON cs.id = cm.session_id
GROUP BY u.id, u.username;

-- Agent performance statistics
SELECT 
    agent_name,
    COUNT(*) as execution_count,
    ROUND(AVG(execution_time_ms), 2) as avg_time_ms,
    MIN(execution_time_ms) as min_time_ms,
    MAX(execution_time_ms) as max_time_ms,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
FROM agent_logs
GROUP BY agent_name
ORDER BY execution_count DESC;

-- Profile usage statistics
SELECT 
    mp.name as profile_name,
    COUNT(DISTINCT cs.id) as session_count,
    COUNT(DISTINCT m.id) as memory_count,
    COUNT(DISTINCT cm.id) as message_count
FROM memory_profiles mp
LEFT JOIN chat_sessions cs ON mp.id = cs.memory_profile_id
LEFT JOIN memories m ON mp.id = m.memory_profile_id
LEFT JOIN chat_messages cm ON cs.id = cm.session_id
GROUP BY mp.id, mp.name
ORDER BY session_count DESC;

-- ============================================================================
-- COMPLEX QUERIES
-- ============================================================================

-- Complete conversation context with all details
SELECT 
    u.username,
    mp.name as profile_name,
    cs.title as session_title,
    cs.privacy_mode,
    cm.role,
    cm.content,
    cm.agent_name,
    cm.created_at as message_time
FROM chat_messages cm
JOIN chat_sessions cs ON cm.session_id = cs.id
JOIN users u ON cs.user_id = u.id
LEFT JOIN memory_profiles mp ON cs.memory_profile_id = mp.id
WHERE cs.id = 1
ORDER BY cm.created_at ASC;

-- User's complete profile with memories and sessions
SELECT 
    u.username,
    u.email,
    mp.name as profile_name,
    COUNT(DISTINCT cs.id) as session_count,
    COUNT(DISTINCT m.id) as memory_count,
    ROUND(AVG(m.importance_score), 2) as avg_memory_importance
FROM users u
JOIN memory_profiles mp ON u.id = mp.user_id
LEFT JOIN chat_sessions cs ON mp.id = cs.memory_profile_id
LEFT JOIN memories m ON mp.id = m.memory_profile_id
GROUP BY u.id, u.username, u.email, mp.id, mp.name;

-- Recent activity summary
SELECT 
    'Users' as category,
    COUNT(*) as count,
    MAX(created_at) as last_created
FROM users
UNION ALL
SELECT 
    'Sessions',
    COUNT(*),
    MAX(created_at)
FROM chat_sessions
UNION ALL
SELECT 
    'Messages',
    COUNT(*),
    MAX(created_at)
FROM chat_messages
UNION ALL
SELECT 
    'Memories',
    COUNT(*),
    MAX(created_at)
FROM memories;

-- ============================================================================
-- DATA EXPORT QUERIES
-- ============================================================================

-- Export users to CSV format (run with: sqlite3 -header -csv database.db "SELECT * FROM users;")
-- Or use:
.mode csv
.headers on
SELECT * FROM users;
SELECT * FROM memory_profiles;
SELECT * FROM chat_sessions;
SELECT * FROM chat_messages;
SELECT * FROM memories;
SELECT * FROM agent_logs;

-- Export formatted (run with: sqlite3 -header database.db)
.mode column
.headers on
SELECT * FROM users;
SELECT * FROM memory_profiles;

