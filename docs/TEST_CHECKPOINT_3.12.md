# Testing Guide for Checkpoint 3.12 - Chat API

## Prerequisites

1. Server is running on `http://localhost:8000`
2. You have a valid access token from login/signup
3. You have at least one chat session created
4. Supabase database is configured and accessible
5. LLM service (OpenAI) is configured with valid API key
6. mem0 service is configured

## Getting Started

First, set up authentication and create a test session:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Save the access token
TOKEN="<your-access-token>"

# Create a test session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_mode": "normal"
  }'

# Save the session ID
SESSION_ID="<your-session-id>"
```

## Test Sequence

### 1. Send a Basic Message

**Test:** Send a simple message and receive a response

```bash
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What is 2+2?",
    "stream": false
  }'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "content": "2+2 equals 4.",
  "session_id": "<session-uuid>",
  "privacy_mode": "normal",
  "memories_used": 0,
  "memories_extracted": false,
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens": {
      "prompt_tokens": 15,
      "completion_tokens": 8,
      "total_tokens": 23
    },
    "finish_reason": "stop"
  }
}
```

**Verify:**
- Response is relevant to the question
- `success` is `true`
- `session_id` matches your session
- `privacy_mode` is `normal`
- `metadata` contains token usage

### 2. Build Conversation Context

**Test:** Send multiple messages to build context and test memory

```bash
# Message 1: Introduce yourself
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Alice and I am a software engineer specializing in Python.",
    "stream": false
  }'

# Wait a moment for memory extraction
sleep 2

# Message 2: Share interest
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I love building web applications with FastAPI.",
    "stream": false
  }'

# Wait a moment for memory extraction
sleep 2

# Message 3: Test memory retrieval
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do you know about me?",
    "stream": false
  }'
```

**Expected for Message 3:**
- Response mentions "Alice"
- Response mentions "software engineer" or "Python"
- Response mentions "FastAPI" or "web applications"
- `memories_used` > 0
- `memories_extracted` is `true` (for messages 1 & 2)

### 3. Test Conversation History

**Test:** Verify conversation history is maintained

```bash
# Ask a follow-up question that requires previous context
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you recommend some Python libraries for my work?",
    "stream": false
  }'
```

**Expected:**
- Response is tailored to web development
- Might mention FastAPI-related libraries
- Shows awareness of previous conversation

### 4. Test Streaming Response

**Test:** Send a message and receive streaming response

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/$SESSION_ID/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me a short story about a programmer",
    "stream": true
  }'
```

**Expected Response (200 OK, text/event-stream):**
```
data: {"success": true, "type": "metadata", "session_id": "...", "privacy_mode": "normal", "memories_used": 2}

data: {"success": true, "type": "content", "content": "Once ", "done": false}

data: {"success": true, "type": "content", "content": "upon ", "done": false}

data: {"success": true, "type": "content", "content": "a ", "done": false}

... (more content chunks)

data: {"success": true, "type": "complete", "memories_extracted": true}

data: [DONE]
```

**Verify:**
- Stream starts immediately
- Content arrives in chunks
- Each chunk is valid JSON
- Metadata chunk comes first
- Complete chunk comes last
- Stream ends with `[DONE]`

### 5. Test Incognito Mode

**Test:** Chat in incognito mode (no memories)

```bash
# Create incognito session
INCOGNITO_SESSION=$(curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"privacy_mode": "incognito"}' \
  | jq -r '.id')

# Send messages in incognito
curl -X POST http://localhost:8000/api/v1/chat/$INCOGNITO_SESSION \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My secret is that I love pineapple on pizza.",
    "stream": false
  }'

# Try to recall (should not remember)
curl -X POST http://localhost:8000/api/v1/chat/$INCOGNITO_SESSION \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What secret did I just tell you?",
    "stream": false
  }'
```

**Expected:**
- `privacy_mode` is `incognito`
- `memories_used` is `0`
- `memories_extracted` is `false`
- AI might not recall the secret (no memory context)

### 6. Test Pause Memories Mode

**Test:** Chat with pause_memories (retrieves but doesn't update)

```bash
# Create pause_memories session
PAUSE_SESSION=$(curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"privacy_mode": "pause_memories"}' \
  | jq -r '.id')

# Send message
curl -X POST http://localhost:8000/api/v1/chat/$PAUSE_SESSION \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am learning Go programming now.",
    "stream": false
  }'
```

**Expected:**
- `privacy_mode` is `pause_memories`
- `memories_used` >= 0 (can use existing memories)
- `memories_extracted` is `false` (no new memories saved)

### 7. Test Message Persistence

**Test:** Verify messages are saved to database

```bash
# Send a unique message
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message 12345 for persistence check",
    "stream": false
  }'

# Retrieve messages from session
curl -X GET http://localhost:8000/api/v1/sessions/$SESSION_ID/messages \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
- Messages array contains your test message (role: "user")
- Immediately followed by assistant response (role: "assistant")
- Both have correct `session_id`
- Both have `created_at` timestamps
- Message order is chronological

### 8. Test Long Message

**Test:** Send a reasonably long message

```bash
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Please explain in detail how to build a REST API with FastAPI, including all the steps from installation to deployment. Cover topics like routing, dependency injection, database integration, authentication, testing, and best practices. Also discuss how to handle errors, validate input, and structure a large application.",
    "stream": false
  }'
```

**Expected:**
- Response is comprehensive and detailed
- Processing completes successfully (may take longer)
- Token usage in metadata reflects longer message

### 9. Test Special Characters

**Test:** Send message with special characters

```bash
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain this code: `def hello(): print(\"Hello! 👋 🌍\")` and tell me about emojis in Python?",
    "stream": false
  }'
```

**Expected:**
- Special characters handled correctly
- Code blocks preserved
- Emojis displayed properly
- Response addresses the code

### 10. Test Rapid Messages

**Test:** Send multiple messages quickly

```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Quick question $i\", \"stream\": false}" &
done
wait
```

**Expected:**
- All messages process successfully
- No race conditions or errors
- Responses are coherent
- Message order preserved in database

## Error Case Tests

### Error Test 1: Invalid Session

```bash
curl -X POST http://localhost:8000/api/v1/chat/00000000-0000-0000-0000-000000000000 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test",
    "stream": false
  }'
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Chat session not found"
}
```

### Error Test 2: No Authentication

```bash
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test",
    "stream": false
  }'
```

**Expected Response (403 Forbidden):**
```json
{
  "detail": "Not authenticated"
}
```

### Error Test 3: Invalid Token

```bash
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer invalid_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test",
    "stream": false
  }'
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Invalid authentication credentials"
}
```

### Error Test 4: Empty Message

```bash
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "",
    "stream": false
  }'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Error Test 5: Message Too Long

```bash
# Create a message > 10,000 characters
LONG_MSG=$(python3 -c "print('a' * 10001)")

curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$LONG_MSG\", \"stream\": false}"
```

**Expected Response (422 Unprocessable Entity):**
Validation error for max_length

### Error Test 6: Another User's Session

**Test:** Try accessing session from different user

```bash
# Login as different user
TOKEN2=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "other@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

# Try to use first user's session
curl -X POST http://localhost:8000/api/v1/chat/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test",
    "stream": false
  }'
```

**Expected Response (403 Forbidden):**
```json
{
  "detail": "Access denied"
}
```

## Integration Testing

### Scenario 1: Complete Conversation Flow

1. Create new session
2. Send introduction message
3. Wait for memory extraction
4. Send follow-up question
5. Verify AI uses memories
6. Check messages persisted
7. Verify conversation history

### Scenario 2: Privacy Mode Switching

1. Start in normal mode
2. Send some messages
3. Update session to incognito
4. Send private messages
5. Update back to normal
6. Verify memories from step 2 still available
7. Verify messages from step 4 not remembered

### Scenario 3: Multi-Session Context

1. Create session A with profile 1
2. Create session B with profile 2
3. Send different info in each session
4. Verify memories are profile-scoped
5. Switch profiles mid-session
6. Verify context changes appropriately

### Scenario 4: Streaming vs. Standard

1. Send same message twice
2. Once with streaming
3. Once without streaming
4. Compare responses
5. Verify both saved to database
6. Check response consistency

## Testing via Swagger UI

1. Navigate to: `http://localhost:8000/docs`

2. Click "Authorize" and enter: `Bearer <TOKEN>`

3. Test endpoints:
   - **POST /chat/{session_id}** - Standard chat
   - **POST /chat/{session_id}/stream** - Streaming (note: may not display properly in Swagger)

4. Use "Try it out" for each endpoint

5. Verify responses match expected schemas

## Automated Testing

Run the comprehensive test suite:

```bash
cd /path/to/backend
source .venv/bin/activate
python test_chat_comprehensive.py
```

This automated suite tests:
- ✅ Basic message sending
- ✅ Context building across messages
- ✅ Incognito mode
- ✅ Streaming responses
- ✅ Error handling (invalid session, no auth, empty message)
- ✅ Message persistence
- ✅ Long message handling

## Performance Benchmarks

### Expected Response Times

- **Simple question:** 1-3 seconds
- **Complex question:** 3-10 seconds
- **With memory search:** +0.5 seconds
- **First streaming chunk:** < 2 seconds
- **Streaming completion:** Variable (based on response length)

### Token Usage Examples

- **Simple Q&A:** 50-200 tokens
- **Detailed explanation:** 200-1000 tokens
- **With memories:** +50-100 tokens
- **Long conversation:** 500-2000 tokens

## Database Verification

After sending messages, check Supabase:

### Verify Messages Saved

```sql
SELECT * FROM chat_messages 
WHERE session_id = '<your_session_id>' 
ORDER BY created_at DESC 
LIMIT 10;
```

Should show both user and assistant messages.

### Verify Memory Extraction

```sql
SELECT * FROM mem0_memories 
WHERE user_id = '<your_user_id>' 
ORDER BY created_at DESC 
LIMIT 5;
```

Should show memories extracted from conversations (if privacy mode was normal).

### Check Session Activity

```sql
SELECT 
  cs.id,
  cs.privacy_mode,
  COUNT(cm.id) as message_count,
  MAX(cm.created_at) as last_message
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.id = cm.session_id
WHERE cs.user_id = '<your_user_id>'
GROUP BY cs.id, cs.privacy_mode
ORDER BY last_message DESC;
```

Shows session activity and message counts.

## Feature Verification Checklist

### Core Features
- ✅ Send message and receive response
- ✅ Conversation history maintained
- ✅ Memory retrieval works
- ✅ Memory extraction works
- ✅ Streaming responses work
- ✅ Messages persisted to database

### Privacy Modes
- ✅ Normal mode: memories used and extracted
- ✅ Incognito mode: no memories
- ✅ Pause memories: retrieval only, no extraction

### Error Handling
- ✅ Invalid session returns 404
- ✅ No auth returns 403
- ✅ Invalid token returns 401
- ✅ Empty message returns 422
- ✅ Cross-user access returns 403

### Response Metadata
- ✅ Success flag included
- ✅ Content included
- ✅ Session ID included
- ✅ Privacy mode included
- ✅ Memory counts included
- ✅ LLM metadata included (model, tokens, etc.)

### Integration
- ✅ Works with all session types
- ✅ Works with all memory profiles
- ✅ Works with all privacy modes
- ✅ Integrates with auth system
- ✅ Integrates with database
- ✅ Integrates with mem0
- ✅ Integrates with LLM service

## Success Criteria

✅ All basic chat tests pass  
✅ All privacy mode tests pass  
✅ Streaming works correctly  
✅ All error cases handled properly  
✅ Messages persisted correctly  
✅ Memories working as expected  
✅ Response times acceptable  
✅ No server errors or crashes  
✅ Token usage reasonable  
✅ Database state consistent  

## Troubleshooting

### Issue: No response or timeout
**Solution:** 
- Check LLM API key is valid
- Check network connectivity
- Increase timeout duration
- Check LLM service rate limits

### Issue: Memories not working
**Solution:**
- Verify mem0 API key
- Check privacy mode is "normal"
- Wait a few seconds after sending message
- Check mem0 service status

### Issue: Streaming not displaying
**Solution:**
- Use curl with `-N` flag
- Don't use Swagger UI for streaming (limitation)
- Check for buffering proxies
- Verify content-type is text/event-stream

### Issue: Messages not persisting
**Solution:**
- Check database connection
- Verify Supabase credentials
- Check RLS policies
- Look for database errors in logs

### Issue: Slow responses
**Solution:**
- Check LLM service latency
- Reduce conversation history limit
- Optimize memory search
- Check database query performance

## Next Steps

After successful testing:
1. ✅ Checkpoint 3.12 verified as working
2. Document any issues found
3. Proceed to Checkpoint 3.13 (Main Application)
4. Prepare for frontend integration (Phase 4)
5. Plan end-to-end testing (Phase 5)

## Notes

- Test in development environment first
- Use different users for cross-user tests
- Monitor token usage to avoid excessive costs
- Keep test sessions for debugging
- Document any unexpected behavior
- Report performance bottlenecks

