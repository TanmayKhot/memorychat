# Database Testing Scripts

This directory contains simple testing scripts to verify database connectivity and table accessibility.

## Test Scripts

### 1. `test_database.py` - Basic Connectivity Test
**Purpose**: Quick test to verify Supabase connection and table accessibility.

**What it tests**:
- ✅ Connection to Supabase
- ✅ All 5 tables are accessible (users, memory_profiles, chat_sessions, chat_messages, mem0_memories)

**Usage**:
```bash
source .venv/bin/activate
python test_database.py
```

**Expected Output**: All tables should show as accessible.

---

### 2. `test_database_schema.py` - Schema Verification Test
**Purpose**: Verify table structures and Row Level Security configuration.

**What it tests**:
- ✅ Table structure verification
- ✅ Row counts for each table
- ✅ RLS policies are configured (basic check)

**Usage**:
```bash
source .venv/bin/activate
python test_database_schema.py
```

**Expected Output**: All tables verified with row counts displayed.

---

### 3. `test_database_detailed.py` - Detailed Inspection Test
**Purpose**: Comprehensive database inspection with detailed information.

**What it tests**:
- ✅ Detailed table inspection (columns and data types)
- ✅ Basic SELECT operations on all tables
- ✅ Expected table relationships

**Usage**:
```bash
source .venv/bin/activate
python test_database_detailed.py
```

**Expected Output**: Detailed information about each table's structure and relationships.

---

## Prerequisites

1. **Completed Phase 2** (Database Setup) from the instructions
2. **Valid Supabase credentials** in `.env` file:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
3. **All required tables created**:
   - users
   - memory_profiles
   - chat_sessions
   - chat_messages
   - mem0_memories

## Database Tables (from Phase 2, Checkpoint 2.2)

### users
- id: uuid (PK)
- email: text (unique)
- created_at: timestamptz
- updated_at: timestamptz
- metadata: jsonb

### memory_profiles
- id: uuid (PK)
- user_id: uuid (FK → users.id)
- name: text
- description: text
- is_default: boolean
- created_at: timestamptz
- updated_at: timestamptz

### chat_sessions
- id: uuid (PK)
- user_id: uuid (FK → users.id)
- memory_profile_id: uuid (FK → memory_profiles.id)
- privacy_mode: text
- created_at: timestamptz
- updated_at: timestamptz

### chat_messages
- id: uuid (PK)
- session_id: uuid (FK → chat_sessions.id)
- role: text
- content: text
- created_at: timestamptz
- metadata: jsonb

### mem0_memories
- id: uuid (PK)
- user_id: uuid (FK → users.id)
- memory_profile_id: uuid (FK → memory_profiles.id)
- mem0_memory_id: text (unique)
- memory_content: text
- created_at: timestamptz
- updated_at: timestamptz

## Current Test Results

✅ **All tests passing!**
- Database connection: ✅ Working
- All tables accessible: ✅ Yes
- Table structures: ✅ Verified
- RLS policies: ✅ Configured
- Basic operations: ✅ Working

## Notes

- These are **simple connectivity tests** - they verify tables exist and are accessible
- No data insertion or deletion is performed
- Tests use the service key to bypass RLS for inspection
- All tables are currently empty (0 rows)
- For full integration testing, proceed to Phase 3 (Backend API Development)

