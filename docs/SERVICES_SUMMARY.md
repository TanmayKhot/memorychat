# Backend Services Summary

Quick reference guide for all implemented services.

---

## 1. SupabaseService ✅

**File**: `app/services/supabase_service.py`  
**Purpose**: Database operations through Supabase

### Key Methods:
- **Users**: `get_user_by_id()`, `create_user()`
- **Profiles**: `get_memory_profiles()`, `create_memory_profile()`, `update_memory_profile()`, `delete_memory_profile()`, `set_default_memory_profile()`
- **Sessions**: `create_chat_session()`, `get_chat_session()`, `update_chat_session()`, `delete_chat_session()`, `get_user_sessions()`
- **Messages**: `create_chat_message()`, `get_session_messages()`, `delete_session_messages()`
- **Memories**: `store_mem0_memory_reference()`, `get_mem0_memory_references()`, `delete_mem0_memory_reference()`

### Usage:
```python
from app.services.supabase_service import supabase_service

# Create memory profile
profile = await supabase_service.create_memory_profile(
    user_id="user-uuid",
    name="Work",
    description="Work-related memories"
)

# Create chat session
session = await supabase_service.create_chat_session(
    user_id="user-uuid",
    profile_id=profile["id"],
    privacy_mode="normal"
)
```

---

## 2. Mem0Service ✅

**File**: `app/services/mem0_service.py`  
**Purpose**: Memory operations using mem0 AI

### Key Methods:
- **Core**: `add_memory()`, `get_memories()`, `search_memories()`, `delete_memory()`, `update_memory()`
- **Extraction**: `extract_memories_from_conversation()`
- **Profile Management**: `delete_all_memories()`, `copy_memories_to_profile()`

### Memory Profile Isolation:
Uses `user_id:profile_id` namespace format for complete isolation.

### Usage:
```python
from app.services.mem0_service import mem0_service

# Search for relevant memories
memories = await mem0_service.search_memories(
    user_id="user-uuid",
    query="user preferences",
    memory_profile_id="profile-uuid",
    limit=5
)

# Extract memories from conversation
await mem0_service.extract_memories_from_conversation(
    messages=[
        {"role": "user", "content": "I love pizza"},
        {"role": "assistant", "content": "Great!"}
    ],
    user_id="user-uuid",
    memory_profile_id="profile-uuid"
)
```

---

## 3. LLMService ✅

**File**: `app/services/llm_service.py`  
**Purpose**: AI chat completions using OpenAI

### Key Methods:
- **Generation**: `generate_response()`, `stream_response()`
- **Context**: `_build_system_prompt()`, `_prepare_messages()`
- **Helpers**: `format_memory_context()`, `validate_messages()`, `count_tokens()`

### Features:
- Context injection (memories + system prompt)
- Exponential backoff retry logic
- Streaming support
- Error handling

### Usage:
```python
from app.services.llm_service import llm_service

# Generate response with context
response = await llm_service.generate_response(
    messages=[{"role": "user", "content": "Hello"}],
    context="User's name is Alice"
)

if response["success"]:
    print(response["content"])
    print(f"Tokens: {response['usage']['total_tokens']}")

# Stream response
async for chunk in llm_service.stream_response(messages, context):
    if chunk["success"]:
        print(chunk["content"], end="", flush=True)
```

---

## 4. ChatService ✅

**File**: `app/services/chat_service.py`  
**Purpose**: Orchestration layer integrating all services

### Key Methods:
- **Core**: `process_user_message()`, `stream_user_message()`
- **Session**: `create_new_session()`, `get_session_details()`, `change_session_privacy_mode()`, `delete_session()`
- **Helpers**: `get_conversation_summary()`, `validate_session_access()`

### Privacy Modes:
- **Normal**: Full memory operations (retrieve + save)
- **Incognito**: No memory operations
- **Pause Memories**: Read-only memories (retrieve only)

### Usage:
```python
from app.services.chat_service import chat_service

# Process user message
result = await chat_service.process_user_message(
    session_id="session-uuid",
    user_message="Hello!"
)

print(result["content"])  # AI response
print(f"Memories used: {result['memories_used']}")

# Stream response in real-time
async for chunk in chat_service.stream_user_message(
    session_id="session-uuid",
    user_message="Tell me a story"
):
    if chunk["type"] == "content":
        print(chunk["content"], end="", flush=True)
```

---

## Service Integration Pattern

### Using ChatService (Recommended)

The ChatService handles all orchestration automatically:

```python
from app.services.chat_service import chat_service

# Simple chat - everything handled automatically
result = await chat_service.process_user_message(
    session_id="session-uuid",
    user_message="What's my favorite color?"
)

# ChatService automatically:
# 1. Gets session details (privacy mode, profile)
# 2. Retrieves relevant memories (if applicable)
# 3. Formats context for AI
# 4. Generates AI response with context
# 5. Saves both messages to database
# 6. Extracts and saves new memories (if applicable)

print(result["content"])  # AI response
```

### Manual Service Coordination (Advanced)

For custom workflows, services can be used individually:

```python
# 1. Database operations
session = await supabase_service.get_chat_session(session_id)

# 2. Memory operations
memories = await mem0_service.search_memories(user_id, query, profile_id)

# 3. AI operations
context = await llm_service.format_memory_context(memories)
response = await llm_service.generate_response(messages, context)

# 4. Save results
await supabase_service.create_chat_message(session_id, "user", message)
await mem0_service.extract_memories_from_conversation(messages, user_id, profile_id)
```

---

## Configuration

All services use settings from `app/core/config.py`:

```python
from app.core.config import settings

# Supabase
settings.SUPABASE_URL
settings.SUPABASE_KEY
settings.SUPABASE_SERVICE_KEY

# OpenAI
settings.OPENAI_API_KEY
settings.OPENAI_MODEL  # Default: gpt-4o-mini
settings.OPENAI_TEMPERATURE  # Default: 0.7
settings.OPENAI_MAX_TOKENS  # Default: 1000

# JWT
settings.JWT_SECRET_KEY
settings.JWT_ALGORITHM
```

---

## Privacy Modes

### Normal Mode
- Memories are retrieved and used for context
- New memories are extracted and saved
- Full personalization

### Incognito Mode
- No memories retrieved
- No memories saved
- Temporary conversation only

### Pause Memories Mode
- Memories are retrieved and used
- No new memories saved
- Read-only memory access

---

## Error Handling

All services implement comprehensive error handling:

### SupabaseService
- Database operation failures
- Returns `None` or empty list on error
- Prints error messages

### Mem0Service
- Memory operation failures
- Returns success/failure status
- Graceful degradation

### LLMService
- API timeout/connection errors (retried)
- Rate limit errors (retried with backoff)
- Auth/validation errors (not retried)
- Returns success/failure in response

---

## Testing

Each service has a test file:
- `test_supabase_service.py`
- `test_mem0_service.py`
- `test_llm_service.py`

Run tests:
```bash
source .venv/bin/activate
python3 test_supabase_service.py
python3 test_mem0_service.py
python3 test_llm_service.py
```

---

## Next Steps

### Checkpoint 3.7: Authentication & Security
JWT verification, CORS, rate limiting.

### Checkpoint 3.8: Pydantic Schemas
Request/response validation schemas.

### Checkpoint 3.9-3.12: API Endpoints
REST API endpoints for auth, profiles, sessions, and chat.

### Checkpoint 3.13: Main Application
FastAPI app initialization and configuration.

---

## Status: 6/13 Checkpoints Complete (46%)

🎉 **ALL SERVICE LAYERS COMPLETE!**

The complete four-layer architecture is implemented:
1. ✅ SupabaseService (20 methods) - Data Layer
2. ✅ Mem0Service (9 methods) - Memory Layer
3. ✅ LLMService (8 methods) - AI Layer
4. ✅ ChatService (8 methods) - Orchestration Layer

Ready for API endpoint implementation!

