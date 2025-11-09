# Frontend Testing Guide

## Current Status

**Phase 6 (Frontend) has not been implemented yet.** However, you can test the API using:

1. **Swagger UI** (Built-in API documentation)
2. **Test UI** (Simple HTML test page provided)
3. **curl commands** (Command-line testing)

---

## Method 1: Test UI (Simple HTML Page)

A simple HTML test page is provided to test all API endpoints.

### How to Use:

1. **Start the backend server:**
   ```bash
   cd memorychat/backend
   source .venv/bin/activate
   python main.py
   ```

2. **Open the test UI:**
   - **Option A:** Open `test-ui.html` directly in your browser
     ```bash
     # On Linux/Mac:
     open memorychat/frontend/test-ui.html
     # Or:
     xdg-open memorychat/frontend/test-ui.html
     
     # On Windows:
     start memorychat/frontend/test-ui.html
     ```
   
   - **Option B:** Serve it with a simple HTTP server:
     ```bash
     cd memorychat/frontend
     python3 -m http.server 8080
     # Then open: http://127.0.0.1:8080/test-ui.html
     ```

3. **Test the endpoints:**
   - The page will automatically check server connection
   - Fill in the forms and click buttons to test endpoints
   - Responses will appear below each section

### Features:
- ✅ Test all user endpoints
- ✅ Test memory profile endpoints
- ✅ Test session endpoints
- ✅ Test chat endpoints
- ✅ Quick workflow test (creates user → profile → session → sends message)
- ✅ Visual feedback for success/error
- ✅ JSON response viewer

---

## Method 2: Swagger UI (Recommended)

FastAPI automatically generates interactive API documentation.

### How to Use:

1. **Start the backend server:**
   ```bash
   cd memorychat/backend
   source .venv/bin/activate
   python main.py
   ```

2. **Open Swagger UI:**
   - Go to: http://127.0.0.1:8000/docs
   - Or ReDoc: http://127.0.0.1:8000/redoc

3. **Test endpoints:**
   - Click on any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - See the response

### Advantages:
- ✅ All endpoints documented
- ✅ Request/response schemas visible
- ✅ Can test directly in browser
- ✅ No code required

---

## Method 3: Browser Developer Console

You can also test directly from browser console:

1. Open browser console (F12)
2. Run JavaScript commands:

```javascript
// Test health check
fetch('http://127.0.0.1:8000/health')
  .then(r => r.json())
  .then(console.log);

// Create user
fetch('http://127.0.0.1:8000/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    username: 'testuser'
  })
})
  .then(r => r.json())
  .then(console.log);

// Get all users
fetch('http://127.0.0.1:8000/api/users')
  .then(r => r.json())
  .then(console.log);
```

---

## Method 4: Postman/Insomnia

Use API testing tools:

1. **Import OpenAPI spec:**
   - Go to: http://127.0.0.1:8000/openapi.json
   - Copy the JSON
   - Import into Postman/Insomnia

2. **Test endpoints:**
   - All endpoints will be available
   - Fill in parameters
   - Send requests
   - View responses

---

## Testing Checklist

When testing the UI/API, verify:

- [ ] Server is running and accessible
- [ ] Health check returns 200 OK
- [ ] Can create users
- [ ] Can create memory profiles
- [ ] Can create sessions
- [ ] Can send messages
- [ ] Can retrieve messages
- [ ] Error handling works (404s, validation errors)
- [ ] CORS is configured (if testing from browser)
- [ ] Responses are formatted correctly

---

## Troubleshooting

### CORS Errors
If you see CORS errors in browser console:
- Make sure backend CORS is configured (already done in main.py)
- Check that you're accessing from allowed origins

### Connection Refused
- Make sure backend server is running
- Check port 8000 is not blocked
- Verify API_BASE URL matches server address

### 404 Errors
- Check endpoint URLs are correct
- Verify resource IDs exist
- Check server logs for details

### 422 Validation Errors
- Check request body format
- Verify required fields are provided
- Check data types match schema

---

## Next Steps

Once Phase 6 is implemented, you'll have:
- Full-featured chat interface
- User/profile management UI
- Session management
- Memory viewing/editing
- Analytics dashboard

For now, use the test UI or Swagger UI to test all API functionality.

