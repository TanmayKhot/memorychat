# Testing Guide for Checkpoint 3.11 - Chat Sessions

## Prerequisites

1. Server is running on `http://localhost:8000`
2. You have a valid access token from login/signup
3. You have at least one memory profile created
4. Supabase database is configured and accessible

## Getting Started

First, login and get your access token and profile IDs:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Get your memory profiles
curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>"
```

Save:
- `<TOKEN>` - Your access token
- `<DEFAULT_PROFILE_ID>` - Your default profile ID
- `<WORK_PROFILE_ID>` - Another profile ID (if you have one)

## Test Sequence

### 1. Create a Chat Session (Uses Default Profile)

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_mode": "normal"
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "session-uuid-1",
  "user_id": "user-uuid",
  "memory_profile_id": "<DEFAULT_PROFILE_ID>",
  "privacy_mode": "normal",
  "created_at": "2025-10-29T...",
  "updated_at": "2025-10-29T...",
  "message_count": 0
}
```

**Note:** Since no `memory_profile_id` was provided, it uses the default profile.

Save the session `id` as `<SESSION_1_ID>`.

### 2. Create Session with Specific Profile

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "memory_profile_id": "<WORK_PROFILE_ID>",
    "privacy_mode": "normal"
  }'
```

**Expected Response (201 Created):**
Session created with the specified profile.

Save as `<SESSION_2_ID>`.

### 3. Create Incognito Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_mode": "incognito"
  }'
```

**Expected Response (201 Created):**
Session created with incognito mode.

Save as `<SESSION_3_ID>`.

### 4. Create Session with Pause Memories Mode

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_mode": "pause_memories"
  }'
```

**Expected Response (201 Created):**
Session created with pause_memories mode.

### 5. Get All Sessions

```bash
curl -X GET http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "session-uuid-1",
    "user_id": "user-uuid",
    "memory_profile_id": "<DEFAULT_PROFILE_ID>",
    "privacy_mode": "normal",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "message_count": 0
  },
  {
    "id": "session-uuid-2",
    "user_id": "user-uuid",
    "memory_profile_id": "<WORK_PROFILE_ID>",
    "privacy_mode": "normal",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "message_count": 0
  },
  // ... more sessions
]
```

Should show all sessions created above.

### 6. Get Sessions with Pagination

```bash
# Get first 2 sessions
curl -X GET "http://localhost:8000/api/v1/sessions?limit=2&offset=0" \
  -H "Authorization: Bearer <TOKEN>"

# Get next 2 sessions
curl -X GET "http://localhost:8000/api/v1/sessions?limit=2&offset=2" \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Result:**
First request returns first 2 sessions, second request returns next 2.

### 7. Filter Sessions by Memory Profile

```bash
curl -X GET "http://localhost:8000/api/v1/sessions?memory_profile_id=<WORK_PROFILE_ID>" \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Result:**
Only returns sessions associated with the specified profile.

### 8. Get Specific Session Details

```bash
curl -X GET http://localhost:8000/api/v1/sessions/<SESSION_1_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "id": "<SESSION_1_ID>",
  "user_id": "user-uuid",
  "memory_profile_id": "<DEFAULT_PROFILE_ID>",
  "privacy_mode": "normal",
  "created_at": "2025-10-29T...",
  "updated_at": "2025-10-29T...",
  "message_count": 0
}
```

### 9. Update Session Privacy Mode

```bash
curl -X PUT http://localhost:8000/api/v1/sessions/<SESSION_1_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_mode": "incognito"
  }'
```

**Expected Response (200 OK):**
Session with `privacy_mode` changed to "incognito".

### 10. Update Session Memory Profile

```bash
curl -X PUT http://localhost:8000/api/v1/sessions/<SESSION_1_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "memory_profile_id": "<WORK_PROFILE_ID>"
  }'
```

**Expected Response (200 OK):**
Session with `memory_profile_id` changed to work profile.

### 11. Update Both Privacy Mode and Profile

```bash
curl -X PUT http://localhost:8000/api/v1/sessions/<SESSION_1_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_mode": "normal",
    "memory_profile_id": "<DEFAULT_PROFILE_ID>"
  }'
```

**Expected Response (200 OK):**
Both fields updated.

### 12. Get Session Messages (Empty Initially)

```bash
curl -X GET http://localhost:8000/api/v1/sessions/<SESSION_1_ID>/messages \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
[]
```

**Note:** Messages will be populated once chat endpoints are implemented (Checkpoint 3.12).

### 13. Get Messages with Pagination

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/<SESSION_1_ID>/messages?limit=50&offset=0" \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
Empty array (or subset of messages if any exist).

### 14. Delete a Session

```bash
curl -X DELETE http://localhost:8000/api/v1/sessions/<SESSION_3_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "message": "Chat session deleted successfully",
  "session_id": "<SESSION_3_ID>"
}
```

### 15. Verify Session Deleted

```bash
curl -X GET http://localhost:8000/api/v1/sessions/<SESSION_3_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Chat session not found"
}
```

## Error Case Tests

### 1. Create Session with Non-existent Profile

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "memory_profile_id": "00000000-0000-0000-0000-000000000000",
    "privacy_mode": "normal"
  }'
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Memory profile not found"
}
```

### 2. Access Non-existent Session

```bash
curl -X GET http://localhost:8000/api/v1/sessions/00000000-0000-0000-0000-000000000000 \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Chat session not found"
}
```

### 3. Access Without Authentication

```bash
curl -X GET http://localhost:8000/api/v1/sessions
```

**Expected Response (403 Forbidden):**
```json
{
  "detail": "Not authenticated"
}
```

### 4. Access with Invalid Token

```bash
curl -X GET http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 5. Update Session with Non-existent Profile

```bash
curl -X PUT http://localhost:8000/api/v1/sessions/<SESSION_1_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "memory_profile_id": "00000000-0000-0000-0000-000000000000"
  }'
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Memory profile not found"
}
```

### 6. Invalid Privacy Mode

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_mode": "invalid_mode"
  }'
```

**Expected Response (422 Unprocessable Entity):**
Validation error for invalid enum value.

## Testing via Swagger UI

1. Navigate to: `http://localhost:8000/docs`

2. Click "Authorize" button and enter: `Bearer <TOKEN>`

3. Test each endpoint:
   - **POST /sessions** - Create sessions with different modes
   - **GET /sessions** - List all sessions
   - **GET /sessions** (with query params) - Test pagination and filtering
   - **GET /sessions/{session_id}** - View session details
   - **PUT /sessions/{session_id}** - Update session
   - **DELETE /sessions/{session_id}** - Delete session
   - **GET /sessions/{session_id}/messages** - View messages

### Recommended Test Flow in Swagger

1. Create 3-4 sessions with different profiles and privacy modes
2. List all sessions - verify all are returned
3. Filter by profile - verify only matching sessions returned
4. Get specific session - verify details are correct
5. Update session - change privacy mode and/or profile
6. Get messages - verify empty array (until chat implemented)
7. Delete one session - verify success
8. Try to get deleted session - verify 404 error

## Database Verification

Check Supabase dashboard after operations:

### After Session Creation
```sql
SELECT * FROM chat_sessions WHERE user_id = '<your_user_id>' ORDER BY created_at DESC;
```

Should show all created sessions with correct:
- `memory_profile_id`
- `privacy_mode`
- Timestamps

### After Session Update
```sql
SELECT id, privacy_mode, memory_profile_id, updated_at 
FROM chat_sessions 
WHERE id = '<session_id>';
```

Should show updated fields and new `updated_at` timestamp.

### After Session Deletion
```sql
-- Check session is deleted
SELECT * FROM chat_sessions WHERE id = '<deleted_session_id>';

-- Check messages are deleted (if any existed)
SELECT * FROM chat_messages WHERE session_id = '<deleted_session_id>';
```

Both should return no results.

### Check Cascade Behavior
```sql
-- Create test messages (manually or via API when available)
INSERT INTO chat_messages (session_id, role, content) 
VALUES ('<session_id>', 'user', 'Test message');

-- Delete session
-- Then verify messages are gone
SELECT * FROM chat_messages WHERE session_id = '<session_id>';
```

Should return no results (cascade delete worked).

## Integration Testing Scenarios

### Scenario 1: Multi-Profile Session Management

1. Create 2 memory profiles (Work, Personal)
2. Create 3 sessions: 2 with Work, 1 with Personal
3. List all sessions - verify 3 sessions
4. Filter by Work profile - verify 2 sessions
5. Filter by Personal profile - verify 1 session
6. Switch one Work session to Personal profile
7. Filter by Personal - verify now shows 2 sessions

### Scenario 2: Privacy Mode Switching

1. Create session in normal mode
2. Verify privacy_mode is "normal"
3. Update to incognito mode
4. Verify privacy_mode changed to "incognito"
5. Update to pause_memories mode
6. Verify privacy_mode changed to "pause_memories"
7. Update back to normal mode

### Scenario 3: Pagination Testing

1. Create 15 sessions
2. Get sessions with limit=5, offset=0 → get first 5
3. Get sessions with limit=5, offset=5 → get next 5
4. Get sessions with limit=5, offset=10 → get last 5
5. Get sessions with limit=5, offset=15 → get empty array

### Scenario 4: Session Lifecycle

1. Create session
2. Get session details - verify exists
3. Update session multiple times
4. Verify each update reflects correctly
5. Delete session
6. Try to get session - verify 404
7. Try to update deleted session - verify 404

## Performance Testing

### Create Multiple Sessions

Create 50 sessions and measure time:

```bash
for i in {1..50}; do
  curl -X POST http://localhost:8000/api/v1/sessions \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"privacy_mode": "normal"}' \
    -w "\nTime: %{time_total}s\n"
done
```

### List Sessions Performance

```bash
curl -X GET http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -w "\nTime: %{time_total}s\n"
```

**Expected:** Should be reasonably fast even with 50+ sessions (< 2 seconds).

### Pagination Performance

```bash
# First page
curl -X GET "http://localhost:8000/api/v1/sessions?limit=50&offset=0" \
  -H "Authorization: Bearer <TOKEN>" \
  -w "\nTime: %{time_total}s\n"

# Second page
curl -X GET "http://localhost:8000/api/v1/sessions?limit=50&offset=50" \
  -H "Authorization: Bearer <TOKEN>" \
  -w "\nTime: %{time_total}s\n"
```

## Expected API Response Times

- **GET /sessions**: < 1s (depends on message count calculation)
- **POST /sessions**: < 500ms
- **GET /sessions/{id}**: < 500ms
- **PUT /sessions/{id}**: < 500ms
- **DELETE /sessions/{id}**: < 1s
- **GET /sessions/{id}/messages**: < 500ms (depends on message count)

## Common Issues & Solutions

### Issue: "Chat session not found"
**Solution:** Verify the session_id is correct and belongs to the authenticated user.

### Issue: "Memory profile not found"
**Solution:** Verify the profile_id exists and belongs to the authenticated user.

### Issue: Slow session listing
**Solution:** This is expected with many sessions as message counts are fetched individually. Will be optimized in future.

### Issue: Can't create session without profile
**Solution:** Either provide a memory_profile_id or ensure your user has a default profile.

### Issue: Privacy mode validation error
**Solution:** Use only valid privacy modes: "normal", "incognito", or "pause_memories".

## Feature Verification

### Privacy Modes
✅ Can create session with normal mode  
✅ Can create session with incognito mode  
✅ Can create session with pause_memories mode  
✅ Can switch privacy modes mid-session  

### Memory Profiles
✅ Can create session with specific profile  
✅ Can create session without profile (uses default)  
✅ Can switch memory profile mid-session  
✅ Cannot use non-existent profile  
✅ Cannot use another user's profile  

### CRUD Operations
✅ Can create sessions  
✅ Can read single session  
✅ Can list all sessions  
✅ Can update sessions  
✅ Can delete sessions  

### Pagination & Filtering
✅ Pagination works for session list  
✅ Pagination works for messages  
✅ Can filter sessions by profile  
✅ Limit and offset parameters work correctly  

### Authorization
✅ All endpoints require authentication  
✅ Can only access own sessions  
✅ Can only use own memory profiles  
✅ Cannot access other users' sessions  

### Data Integrity
✅ Session deletion cascades to messages  
✅ Message counts are accurate  
✅ Timestamps are set correctly  
✅ Updated_at changes on updates  

## Success Criteria

✅ All 6 endpoints return expected responses  
✅ Authentication required for all endpoints  
✅ Authorization prevents accessing other users' data  
✅ Pagination works correctly  
✅ Profile filtering works correctly  
✅ Privacy modes work correctly  
✅ Session deletion cascades properly  
✅ Message counts are accurate  
✅ Partial updates work correctly  
✅ Error messages are clear and helpful  

## Next Steps

After verifying all tests pass:
1. ✅ Checkpoint 3.11 is complete
2. Proceed to Checkpoint 3.12 (Chat endpoints)
3. Messages will be created via chat endpoint
4. Session message counts will populate as conversations occur
5. Consider adding automated tests (pytest) for regression testing

## Notes on Checkpoint 3.12

Once chat endpoints are implemented:
- Messages will be created automatically during conversations
- Message counts will reflect actual conversation length
- GET /sessions/{id}/messages will return real messages
- Privacy modes will affect memory creation/retrieval behavior

