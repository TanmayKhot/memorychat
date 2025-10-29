# MemoryChat API Endpoints Summary

**Last Updated:** October 29, 2025  
**Implemented Checkpoints:** 3.9, 3.10, 3.11

## Base URL
`http://localhost:8000/api/v1`

## Authentication
All endpoints except `/auth/signup` and `/auth/login` require authentication via Bearer token:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints (`/auth`)

### 1. POST `/auth/signup`
**Create a new user account**

- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:** `201 Created`
  ```json
  {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 604800,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "created_at": "2025-10-29T...",
      "updated_at": "2025-10-29T...",
      "metadata": null
    }
  }
  ```
- **Side Effects:**
  - Creates user in Supabase Auth
  - Creates user record in database
  - Creates default memory profile

### 2. POST `/auth/login`
**Authenticate existing user**

- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:** `200 OK`
  ```json
  {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 604800,
    "user": { ... }
  }
  ```

### 3. POST `/auth/logout`
**Log out current user**

- **Authentication:** Required
- **Request Body:** None
- **Response:** `200 OK`
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

### 4. GET `/auth/me`
**Get current user information**

- **Authentication:** Required
- **Response:** `200 OK`
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "metadata": null
  }
  ```

---

## Memory Profile Endpoints (`/memory-profiles`)

### 1. GET `/memory-profiles`
**Get all memory profiles for current user**

- **Authentication:** Required
- **Response:** `200 OK`
  ```json
  [
    {
      "id": "profile-uuid",
      "user_id": "user-uuid",
      "name": "Default",
      "description": "Your default memory profile",
      "is_default": true,
      "created_at": "2025-10-29T...",
      "updated_at": "2025-10-29T...",
      "memory_count": 42
    }
  ]
  ```

### 2. POST `/memory-profiles`
**Create a new memory profile**

- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "name": "Work",
    "description": "Work-related conversations",
    "is_default": false
  }
  ```
- **Response:** `201 Created`
  ```json
  {
    "id": "new-profile-uuid",
    "user_id": "user-uuid",
    "name": "Work",
    "description": "Work-related conversations",
    "is_default": false,
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "memory_count": 0
  }
  ```
- **Notes:**
  - If this is user's first profile, automatically set as default
  - Profile names must be unique per user

### 3. GET `/memory-profiles/{profile_id}`
**Get specific memory profile details**

- **Authentication:** Required
- **URL Parameters:**
  - `profile_id` (required): Profile UUID
- **Response:** `200 OK`
  ```json
  {
    "id": "profile-uuid",
    "user_id": "user-uuid",
    "name": "Work",
    "description": "Work-related conversations",
    "is_default": false,
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "memory_count": 15
  }
  ```

### 4. PUT `/memory-profiles/{profile_id}`
**Update a memory profile**

- **Authentication:** Required
- **URL Parameters:**
  - `profile_id` (required): Profile UUID
- **Request Body:** (all fields optional)
  ```json
  {
    "name": "Personal Projects",
    "description": "Updated description",
    "is_default": true
  }
  ```
- **Response:** `200 OK`
  ```json
  {
    "id": "profile-uuid",
    "user_id": "user-uuid",
    "name": "Personal Projects",
    "description": "Updated description",
    "is_default": true,
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "memory_count": 15
  }
  ```
- **Notes:**
  - Only provided fields are updated
  - Setting `is_default: true` automatically unsets other defaults

### 5. DELETE `/memory-profiles/{profile_id}`
**Delete a memory profile**

- **Authentication:** Required
- **URL Parameters:**
  - `profile_id` (required): Profile UUID
- **Response:** `200 OK`
  ```json
  {
    "message": "Memory profile deleted successfully",
    "profile_id": "profile-uuid"
  }
  ```
- **Side Effects:**
  - Deletes all memories from mem0 for this profile
  - Cascades delete to `mem0_memories` table
  - Cascades update to `chat_sessions` (sets memory_profile_id to NULL)
- **Restrictions:**
  - Cannot delete if it's the user's only profile

### 6. POST `/memory-profiles/{profile_id}/set-default`
**Set a profile as default**

- **Authentication:** Required
- **URL Parameters:**
  - `profile_id` (required): Profile UUID
- **Response:** `200 OK`
  ```json
  {
    "message": "Memory profile set as default successfully",
    "profile_id": "profile-uuid",
    "profile_name": "Work"
  }
  ```
- **Side Effects:**
  - Automatically unsets previous default profile
  - Only one profile can be default at a time

### 7. GET `/memory-profiles/{profile_id}/memories`
**Get all memories for a profile**

- **Authentication:** Required
- **URL Parameters:**
  - `profile_id` (required): Profile UUID
- **Response:** `200 OK`
  ```json
  [
    {
      "id": "memory-id",
      "memory": "User prefers Python over JavaScript",
      "created_at": "2025-10-29T...",
      "updated_at": "2025-10-29T...",
      "user_id": "user-uuid",
      "metadata": {
        "memory_profile_id": "profile-uuid",
        "confidence": 0.95
      }
    }
  ]
  ```
- **Notes:**
  - Returns memories from mem0
  - Empty array if no memories yet
  - Memories are created through chat conversations

---

## Chat Session Endpoints (`/sessions`)

### 1. GET `/sessions`
**Get all chat sessions for current user**

- **Authentication:** Required
- **Query Parameters:**
  - `memory_profile_id` (optional): Filter by memory profile UUID
  - `limit` (optional, 1-100, default 50): Max sessions to return
  - `offset` (optional, default 0): Number of sessions to skip
- **Response:** `200 OK`
  ```json
  [
    {
      "id": "session-uuid",
      "user_id": "user-uuid",
      "memory_profile_id": "profile-uuid",
      "privacy_mode": "normal",
      "created_at": "2025-10-29T...",
      "updated_at": "2025-10-29T...",
      "message_count": 15
    }
  ]
  ```
- **Notes:**
  - Supports pagination and filtering
  - Message counts fetched in real-time

### 2. POST `/sessions`
**Create a new chat session**

- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "memory_profile_id": "profile-uuid",  // optional
    "privacy_mode": "normal"  // normal, incognito, pause_memories
  }
  ```
- **Response:** `201 Created`
  ```json
  {
    "id": "new-session-uuid",
    "user_id": "user-uuid",
    "memory_profile_id": "profile-uuid",
    "privacy_mode": "normal",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "message_count": 0
  }
  ```
- **Notes:**
  - If no profile provided, uses user's default profile
  - Profile must exist and belong to user

### 3. GET `/sessions/{session_id}`
**Get specific session details**

- **Authentication:** Required
- **URL Parameters:**
  - `session_id` (required): Session UUID
- **Response:** `200 OK`
  ```json
  {
    "id": "session-uuid",
    "user_id": "user-uuid",
    "memory_profile_id": "profile-uuid",
    "privacy_mode": "normal",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "message_count": 15
  }
  ```

### 4. PUT `/sessions/{session_id}`
**Update a session**

- **Authentication:** Required
- **URL Parameters:**
  - `session_id` (required): Session UUID
- **Request Body:** (all fields optional)
  ```json
  {
    "privacy_mode": "incognito",  // optional
    "memory_profile_id": "new-profile-uuid"  // optional
  }
  ```
- **Response:** `200 OK`
  ```json
  {
    "id": "session-uuid",
    "user_id": "user-uuid",
    "memory_profile_id": "new-profile-uuid",
    "privacy_mode": "incognito",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "message_count": 15
  }
  ```
- **Notes:**
  - Only provided fields are updated
  - Useful for switching privacy modes mid-conversation

### 5. DELETE `/sessions/{session_id}`
**Delete a session**

- **Authentication:** Required
- **URL Parameters:**
  - `session_id` (required): Session UUID
- **Response:** `200 OK`
  ```json
  {
    "message": "Chat session deleted successfully",
    "session_id": "session-uuid"
  }
  ```
- **Side Effects:**
  - Deletes all messages in the session (cascade)
  - Action is irreversible

### 6. GET `/sessions/{session_id}/messages`
**Get all messages for a session**

- **Authentication:** Required
- **URL Parameters:**
  - `session_id` (required): Session UUID
- **Query Parameters:**
  - `limit` (optional, 1-500, default 100): Max messages to return
  - `offset` (optional, default 0): Number of messages to skip
- **Response:** `200 OK`
  ```json
  [
    {
      "id": "message-uuid",
      "session_id": "session-uuid",
      "role": "user",
      "content": "What is Python?",
      "created_at": "2025-10-29T...",
      "metadata": {}
    },
    {
      "id": "message-uuid-2",
      "session_id": "session-uuid",
      "role": "assistant",
      "content": "Python is a high-level programming language...",
      "created_at": "2025-10-29T...",
      "metadata": {"model": "gpt-4o-mini", "tokens": 150}
    }
  ]
  ```
- **Notes:**
  - Messages ordered by creation time (oldest first)
  - Supports pagination for long conversations

---

## Common Response Codes

### Success Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully

### Client Error Codes
- `400 Bad Request` - Invalid request data or business logic violation
- `401 Unauthorized` - Invalid or missing authentication token
- `403 Forbidden` - Valid auth but insufficient permissions
- `404 Not Found` - Requested resource doesn't exist

### Server Error Codes
- `500 Internal Server Error` - Server-side error occurred

---

## Error Response Format

All error responses follow this format:
```json
{
  "detail": "Error message description"
}
```

### Example Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Not authorized to access this resource"
}
```

**404 Not Found:**
```json
{
  "detail": "Memory profile not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Cannot delete the only memory profile. Create another profile first."
}
```

---

## Data Models

### User
```typescript
{
  id: string;                    // UUID
  email: string;                 // Email address
  created_at: datetime;          // ISO 8601 timestamp
  updated_at: datetime;          // ISO 8601 timestamp
  metadata?: object;             // Optional additional data
}
```

### MemoryProfile
```typescript
{
  id: string;                    // UUID
  user_id: string;               // Owner UUID
  name: string;                  // Profile name (unique per user)
  description?: string;          // Optional description
  is_default: boolean;           // Default profile flag
  created_at: datetime;          // ISO 8601 timestamp
  updated_at: datetime;          // ISO 8601 timestamp
  memory_count?: number;         // Number of memories (computed)
}
```

### Memory
```typescript
{
  id: string;                    // Memory ID from mem0
  memory: string;                // Memory content/text
  created_at?: datetime;         // ISO 8601 timestamp
  updated_at?: datetime;         // ISO 8601 timestamp
  user_id?: string;              // Owner UUID
  metadata?: object;             // Additional metadata
}
```

### TokenResponse
```typescript
{
  access_token: string;          // JWT token
  token_type: string;            // Always "bearer"
  expires_in: number;            // Seconds until expiration
  user: User;                    // User object
}
```

### ChatSession
```typescript
{
  id: string;                    // UUID
  user_id: string;               // Owner UUID
  memory_profile_id?: string;    // Memory profile UUID (optional)
  privacy_mode: string;          // normal, incognito, pause_memories
  created_at: datetime;          // ISO 8601 timestamp
  updated_at: datetime;          // ISO 8601 timestamp
  message_count?: number;        // Number of messages (computed)
}
```

### ChatMessage
```typescript
{
  id: string;                    // UUID
  session_id: string;            // Session UUID
  role: string;                  // user, assistant, system
  content: string;               // Message content/text
  created_at: datetime;          // ISO 8601 timestamp
  metadata?: object;             // Additional metadata (model, tokens, etc.)
}
```

---

## Rate Limiting

Rate limiting is configured but not yet enforced:
- Limit: 60 requests per minute (configurable)
- Will be implemented in future updates

---

## CORS Configuration

Allowed origins:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (Alternative frontend)
- `http://localhost:8000` (Backend itself)

All methods and headers are allowed for development.

---

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Quick Start Example

### 1. Create Account
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Save Token and List Profiles
```bash
TOKEN="<access_token_from_signup>"

curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Create Work Profile
```bash
curl -X POST http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work", "description": "Work-related chats"}'
```

---

## Implementation Status

### ✅ Completed (Checkpoints 3.9, 3.10, 3.11)
- Authentication endpoints (signup, login, logout, get user)
- Memory profile CRUD operations
- Memory profile default management
- Profile memory retrieval
- Chat session CRUD operations
- Session message retrieval
- Session pagination and filtering
- Privacy mode support

### ⏳ Pending (Next Checkpoints)
- Chat message endpoints (3.12)
- Streaming support
- Frontend implementation (Phase 4)

---

## Notes

- All timestamps are in ISO 8601 format
- All IDs are UUIDs (version 4)
- Profile names are case-sensitive
- Memories are stored in mem0 with profile-namespaced user identifiers
- Database uses Row Level Security (RLS) for additional security
- Passwords are handled by Supabase Auth (bcrypt hashing)
- JWTs are signed and verified by Supabase

---

## Support & Testing

For detailed testing instructions, see:
- `TEST_CHECKPOINT_3.9.md` - Auth endpoint testing
- `TEST_CHECKPOINT_3.10.md` - Memory profile testing
- `TEST_CHECKPOINT_3.11.md` - Chat session testing

For implementation details, see:
- `CHECKPOINT_3.9.md` - Auth implementation
- `CHECKPOINT_3.10.md` - Memory profile implementation
- `CHECKPOINT_3.11.md` - Chat session implementation

