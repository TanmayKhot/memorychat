# Testing Guide for Step 5.2: API Endpoints

This guide provides multiple ways to test the API endpoints.

## Prerequisites

1. **Server must be running:**
   ```bash
   cd memorychat/backend
   source .venv/bin/activate
   python main.py
   ```

2. **Dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database initialized:**
   ```bash
   python ../scripts/init_database.py
   ```

---

## Method 1: Automated Test Script (Recommended)

The easiest way to test all endpoints automatically:

```bash
cd memorychat/backend
source .venv/bin/activate
python test_step5_2_auto.py
```

This will:
- ✅ Test all 26 endpoints
- ✅ Verify request validation
- ✅ Test error handling
- ✅ Provide a summary report

**Expected Output:**
```
✅ CHECKPOINT 5.2: ALL REQUIREMENTS MET
Total Tests: 23
Passed: 23
Failed: 0
```

---

## Method 2: Swagger UI (Interactive Testing)

FastAPI automatically generates interactive API documentation:

1. **Start the server:**
   ```bash
   cd memorychat/backend
   source .venv/bin/activate
   python main.py
   ```

2. **Open in browser:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

3. **Test endpoints:**
   - Click on any endpoint to expand it
   - Click "Try it out"
   - Fill in the parameters
   - Click "Execute"
   - See the response

**Example: Create a User**
1. Go to `POST /api/users`
2. Click "Try it out"
3. Enter:
   ```json
   {
     "email": "test@example.com",
     "username": "testuser"
   }
   ```
4. Click "Execute"
5. See the response with status 201 and user data

---

## Method 3: Using curl Commands

Test endpoints directly from the command line:

### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```

### 2. Create User
```bash
curl -X POST "http://127.0.0.1:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser"
  }'
```

### 3. Get User
```bash
curl http://127.0.0.1:8000/api/users/1
```

### 4. Get All Users
```bash
curl http://127.0.0.1:8000/api/users
```

### 5. Create Memory Profile
```bash
curl -X POST "http://127.0.0.1:8000/api/users/1/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work Profile",
    "description": "Professional conversations",
    "system_prompt": "You are a professional assistant."
  }'
```

### 6. Create Session
```bash
curl -X POST "http://127.0.0.1:8000/api/users/1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "memory_profile_id": 1,
    "privacy_mode": "normal"
  }'
```

### 7. Send Message
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "message": "Hello, how are you?"
  }'
```

### 8. Get Session Messages
```bash
curl "http://127.0.0.1:8000/api/sessions/1/messages?page=1&limit=10"
```

### 9. Get Session Analytics
```bash
curl http://127.0.0.1:8000/api/sessions/1/analytics
```

### 10. Search Memories
```bash
curl -X POST "http://127.0.0.1:8000/api/memories/search?profile_id=1&query=test&limit=10"
```

---

## Method 4: Python Requests Script

Create a simple Python script to test:

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# Create user
response = requests.post(
    f"{BASE_URL}/users",
    json={"email": "test@example.com", "username": "testuser"}
)
user_id = response.json()["id"]
print(f"Created user: {user_id}")

# Create profile
response = requests.post(
    f"{BASE_URL}/users/{user_id}/profiles",
    json={
        "name": "Test Profile",
        "description": "Test description"
    }
)
profile_id = response.json()["id"]
print(f"Created profile: {profile_id}")

# Create session
response = requests.post(
    f"{BASE_URL}/users/{user_id}/sessions",
    json={
        "memory_profile_id": profile_id,
        "privacy_mode": "normal"
    }
)
session_id = response.json()["id"]
print(f"Created session: {session_id}")

# Send message
response = requests.post(
    f"{BASE_URL}/chat/message",
    json={
        "session_id": session_id,
        "message": "Hello!"
    }
)
print(f"Response: {response.json()['message']}")
```

---

## Method 5: Testing Specific Features

### Test Request Validation

**Invalid Email:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-email", "username": "test"}'
```
Expected: 422 Validation Error

**Empty Username:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": ""}'
```
Expected: 422 Validation Error

### Test Error Handling

**Non-existent User:**
```bash
curl http://127.0.0.1:8000/api/users/99999
```
Expected: 404 Not Found

**Non-existent Session:**
```bash
curl http://127.0.0.1:8000/api/sessions/99999
```
Expected: 404 Not Found

### Test Privacy Modes

**Normal Mode:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users/1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"memory_profile_id": 1, "privacy_mode": "normal"}'
```

**Incognito Mode:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users/1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"memory_profile_id": 1, "privacy_mode": "incognito"}'
```

**Pause Memory Mode:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users/1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"memory_profile_id": 1, "privacy_mode": "pause_memory"}'
```

---

## Method 6: Complete Workflow Test

Test a complete user workflow:

```bash
#!/bin/bash

BASE_URL="http://127.0.0.1:8000/api"

# 1. Create user
echo "1. Creating user..."
USER_RESPONSE=$(curl -s -X POST "$BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d '{"email": "workflow@example.com", "username": "workflowuser"}')
USER_ID=$(echo $USER_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "   User ID: $USER_ID"

# 2. Create profile
echo "2. Creating profile..."
PROFILE_RESPONSE=$(curl -s -X POST "$BASE_URL/users/$USER_ID/profiles" \
  -H "Content-Type: application/json" \
  -d '{"name": "Workflow Profile", "description": "Test workflow"}')
PROFILE_ID=$(echo $PROFILE_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "   Profile ID: $PROFILE_ID"

# 3. Create session
echo "3. Creating session..."
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/users/$USER_ID/sessions" \
  -H "Content-Type: application/json" \
  -d "{\"memory_profile_id\": $PROFILE_ID, \"privacy_mode\": \"normal\"}")
SESSION_ID=$(echo $SESSION_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "   Session ID: $SESSION_ID"

# 4. Send message
echo "4. Sending message..."
MESSAGE_RESPONSE=$(curl -s -X POST "$BASE_URL/chat/message" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": $SESSION_ID, \"message\": \"Hello, this is a test!\"}")
echo "   Response received"

# 5. Get messages
echo "5. Getting messages..."
curl -s "$BASE_URL/sessions/$SESSION_ID/messages" | head -20

echo ""
echo "✅ Workflow test complete!"
```

---

## Verification Checklist

After testing, verify:

- [ ] All endpoints respond correctly
- [ ] Request validation works (invalid inputs rejected)
- [ ] Error handling works (404s, 400s, etc.)
- [ ] Response formats are correct
- [ ] Logging is working (check server logs)
- [ ] CORS is configured (if testing from browser)
- [ ] Database operations persist correctly

---

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Check .env file exists and has correct settings
- Check database is initialized

### Import errors
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Install email-validator: `pip install email-validator`

### Connection refused
- Make sure server is running
- Check server logs for errors
- Verify API_HOST and API_PORT in .env

### 500 Internal Server Error
- Check server logs for detailed error
- Verify database is initialized
- Check OpenAI API key if using LLM features

---

## Quick Start Commands

```bash
# 1. Start server
cd memorychat/backend
source .venv/bin/activate
python main.py

# 2. In another terminal, run tests
cd memorychat/backend
source .venv/bin/activate
python test_step5_2_auto.py

# 3. Or open browser
# http://127.0.0.1:8000/docs
```

---

## Expected Test Results

When all tests pass, you should see:

```
✅ CHECKPOINT 5.2: ALL REQUIREMENTS MET

Total Tests: 23
Passed: 23
Failed: 0

✓ All API endpoints implemented
✓ Request validation working
✓ Response formatting correct
✓ Error handling in place
✓ Logging integrated
```

