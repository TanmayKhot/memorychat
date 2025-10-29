# Testing Guide for Checkpoint 3.9

## Prerequisites

1. Ensure `.env` file is configured with all required variables:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
JWT_SECRET_KEY=your_jwt_secret
OPENAI_API_KEY=your_openai_key
```

2. Ensure Supabase database is set up with required tables:
   - `users`
   - `memory_profiles`
   - `chat_sessions`
   - `chat_messages`
   - `mem0_memories`

## Running the Server

From the `/backend` directory:

```bash
# Activate virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows

# Run the server
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server should start on `http://localhost:8000`

## Testing Endpoints

### 1. Check API is Running

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "MemoryChat API",
  "status": "running",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 2. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### 3. Test Signup (POST /api/v1/auth/signup)

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

Expected response (200/201):
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": "uuid-here",
    "email": "testuser@example.com",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "metadata": null
  }
}
```

### 4. Test Login (POST /api/v1/auth/login)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

Expected response (200):
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": "uuid-here",
    "email": "testuser@example.com",
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "metadata": null
  }
}
```

Save the `access_token` for subsequent requests.

### 5. Test Get Current User (GET /api/v1/auth/me)

```bash
# Replace <ACCESS_TOKEN> with the token from login/signup
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Expected response (200):
```json
{
  "id": "uuid-here",
  "email": "testuser@example.com",
  "created_at": "2025-10-29T...",
  "updated_at": "2025-10-29T...",
  "metadata": null
}
```

### 6. Test Logout (POST /api/v1/auth/logout)

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Expected response (200):
```json
{
  "message": "Successfully logged out"
}
```

## Error Cases to Test

### 1. Signup with Existing Email

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

Expected response (400):
```json
{
  "detail": "User registration failed. Email may already be in use."
}
```

### 2. Login with Wrong Password

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "wrongpassword"
  }'
```

Expected response (401):
```json
{
  "detail": "Invalid email or password"
}
```

### 3. Access Protected Endpoint Without Token

```bash
curl -X GET http://localhost:8000/api/v1/auth/me
```

Expected response (403):
```json
{
  "detail": "Not authenticated"
}
```

### 4. Access Protected Endpoint With Invalid Token

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer invalid_token_here"
```

Expected response (401):
```json
{
  "detail": "Invalid authentication credentials"
}
```

## Testing via Swagger UI

1. Open browser and navigate to: `http://localhost:8000/docs`
2. You'll see all endpoints documented with schemas
3. Test each endpoint interactively:
   - Click on an endpoint to expand it
   - Click "Try it out"
   - Fill in the request body
   - Click "Execute"
   - View the response

### Using Authorization in Swagger

1. After signup/login, copy the `access_token`
2. Click the "Authorize" button at the top right
3. Enter: `Bearer <your_access_token>`
4. Click "Authorize"
5. Now you can test protected endpoints

## Verifying Database Records

After signup, verify in Supabase dashboard:

1. **Check users table:**
   - Should have new user record with email
   - User ID should match the one from Supabase Auth

2. **Check memory_profiles table:**
   - Should have a default profile for the new user
   - Profile should be marked as `is_default = true`
   - Profile name should be "Default"

## Common Issues & Solutions

### Issue: "Module not found" errors
**Solution:** Ensure virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "SUPABASE_URL not found"
**Solution:** Create `.env` file in `/backend` directory with all required variables

### Issue: "Connection refused"
**Solution:** Check that Supabase URL is correct and accessible

### Issue: "Invalid token"
**Solution:** Ensure you're using the correct JWT_SECRET_KEY that matches Supabase project settings

### Issue: "User creation failed"
**Solution:** Check Supabase Auth settings - ensure email confirmation is disabled for testing

## Next Steps After Verification

Once all tests pass:

1. ✅ Checkpoint 3.9 is complete
2. Proceed to Checkpoint 3.10 (Memory Profiles endpoints)
3. Consider writing automated tests (pytest) for these endpoints
4. Document any issues or improvements needed

## Performance Considerations

- Signup may take 1-3 seconds (creates user + profile)
- Login should be < 1 second
- Token verification is fast (< 100ms)
- All operations are async for better performance

## Security Notes

- Passwords are handled by Supabase Auth (bcrypt hashing)
- Tokens are JWT signed by Supabase
- Service key is used only server-side
- CORS is configured for frontend origins
- Rate limiting configured but not yet enforced

