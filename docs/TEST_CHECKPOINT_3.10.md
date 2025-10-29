# Testing Guide for Checkpoint 3.10 - Memory Profiles

## Prerequisites

1. Server is running on `http://localhost:8000`
2. You have a valid access token from login/signup
3. Supabase database is configured and accessible
4. mem0 is configured (with OpenAI API key)

## Getting an Access Token

First, login or signup to get an access token:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response. We'll use `<TOKEN>` as a placeholder in the examples below.

## Test Sequence

### 1. Get All Memory Profiles (Should return default profile from signup)

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "profile-uuid-1",
    "user_id": "user-uuid",
    "name": "Default",
    "description": "Your default memory profile",
    "is_default": true,
    "created_at": "2025-10-29T...",
    "updated_at": "2025-10-29T...",
    "memory_count": 0
  }
]
```

**Note:** The default profile was created during signup (Checkpoint 3.9).

### 2. Create a New Memory Profile - "Work"

```bash
curl -X POST http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work",
    "description": "Work-related conversations and projects",
    "is_default": false
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "profile-uuid-2",
  "user_id": "user-uuid",
  "name": "Work",
  "description": "Work-related conversations and projects",
  "is_default": false,
  "created_at": "2025-10-29T...",
  "updated_at": "2025-10-29T...",
  "memory_count": 0
}
```

Save the `id` for subsequent tests. We'll call it `<WORK_PROFILE_ID>`.

### 3. Create Another Profile - "Personal"

```bash
curl -X POST http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Personal",
    "description": "Personal conversations and interests"
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "profile-uuid-3",
  "user_id": "user-uuid",
  "name": "Personal",
  "description": "Personal conversations and interests",
  "is_default": false,
  "created_at": "2025-10-29T...",
  "updated_at": "2025-10-29T...",
  "memory_count": 0
}
```

Save this `id` as `<PERSONAL_PROFILE_ID>`.

### 4. Get All Profiles (Should now show 3 profiles)

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
Should return array with 3 profiles: Default (default=true), Work, Personal.

### 5. Get Specific Profile Details

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles/<WORK_PROFILE_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "id": "<WORK_PROFILE_ID>",
  "user_id": "user-uuid",
  "name": "Work",
  "description": "Work-related conversations and projects",
  "is_default": false,
  "created_at": "2025-10-29T...",
  "updated_at": "2025-10-29T...",
  "memory_count": 0
}
```

### 6. Update Profile Name and Description

```bash
curl -X PUT http://localhost:8000/api/v1/memory-profiles/<WORK_PROFILE_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work Projects",
    "description": "Professional projects and work discussions"
  }'
```

**Expected Response (200 OK):**
Profile with updated name and description.

### 7. Update Only Description (Partial Update)

```bash
curl -X PUT http://localhost:8000/api/v1/memory-profiles/<PERSONAL_PROFILE_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Personal life, hobbies, and interests"
  }'
```

**Expected Response (200 OK):**
Profile with updated description but same name.

### 8. Set Work Profile as Default

```bash
curl -X POST http://localhost:8000/api/v1/memory-profiles/<WORK_PROFILE_ID>/set-default \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "message": "Memory profile set as default successfully",
  "profile_id": "<WORK_PROFILE_ID>",
  "profile_name": "Work Projects"
}
```

### 9. Verify Default Changed

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Result:**
- Work Projects should have `is_default: true`
- Default profile should now have `is_default: false`
- Personal should have `is_default: false`

### 10. Get Memories for a Profile (Should be empty initially)

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles/<WORK_PROFILE_ID>/memories \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
[]
```

**Note:** Memories will be populated once chat endpoints are implemented and conversations occur.

### 11. Delete the Personal Profile

```bash
curl -X DELETE http://localhost:8000/api/v1/memory-profiles/<PERSONAL_PROFILE_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "message": "Memory profile deleted successfully",
  "profile_id": "<PERSONAL_PROFILE_ID>"
}
```

### 12. Verify Profile Deleted

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Result:**
Should only show 2 profiles now (Default and Work Projects).

## Error Case Tests

### 1. Try to Create Duplicate Profile Name

```bash
curl -X POST http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Default",
    "description": "This should fail"
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "A profile with the name 'Default' already exists"
}
```

### 2. Try to Access Non-existent Profile

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles/00000000-0000-0000-0000-000000000000 \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Memory profile not found"
}
```

### 3. Try to Delete When Only One Profile Remains

First, delete profiles until only one remains, then try to delete it:

```bash
curl -X DELETE http://localhost:8000/api/v1/memory-profiles/<LAST_PROFILE_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "Cannot delete the only memory profile. Create another profile first."
}
```

### 4. Try to Access Without Authentication

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles
```

**Expected Response (403 Forbidden):**
```json
{
  "detail": "Not authenticated"
}
```

### 5. Try to Access with Invalid Token

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 6. Try to Update with Duplicate Name

```bash
curl -X PUT http://localhost:8000/api/v1/memory-profiles/<WORK_PROFILE_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Default"
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "A profile with the name 'Default' already exists"
}
```

## Testing via Swagger UI

1. Navigate to: `http://localhost:8000/docs`

2. Click "Authorize" button (top right)

3. Enter: `Bearer <your_access_token>`

4. Click "Authorize" then "Close"

5. Test each endpoint:
   - Expand endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - View response

### Recommended Test Flow in Swagger

1. **GET /memory-profiles** - See initial profiles
2. **POST /memory-profiles** - Create "Test Profile"
3. **GET /memory-profiles/{profile_id}** - View created profile
4. **PUT /memory-profiles/{profile_id}** - Update it
5. **POST /memory-profiles/{profile_id}/set-default** - Set as default
6. **GET /memory-profiles/{profile_id}/memories** - View memories (empty)
7. **DELETE /memory-profiles/{profile_id}** - Delete it

## Database Verification

Check Supabase dashboard after operations:

### After Profile Creation
```sql
SELECT * FROM memory_profiles WHERE user_id = '<your_user_id>';
```

Should show all created profiles.

### After Set Default
```sql
SELECT name, is_default FROM memory_profiles 
WHERE user_id = '<your_user_id>' 
ORDER BY is_default DESC;
```

Should show only one profile with `is_default = true`.

### After Profile Deletion
```sql
SELECT * FROM memory_profiles WHERE id = '<deleted_profile_id>';
```

Should return no results.

### Check Cascade Deletion
```sql
-- Check if associated memories were deleted
SELECT * FROM mem0_memories WHERE memory_profile_id = '<deleted_profile_id>';

-- Check if associated sessions were updated
SELECT * FROM chat_sessions WHERE memory_profile_id = '<deleted_profile_id>';
```

Both should return no results (or sessions should have NULL memory_profile_id).

## Performance Testing

### Create Multiple Profiles

Create 10 profiles and measure response time:

```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/memory-profiles \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Profile $i\", \"description\": \"Test profile $i\"}" \
    -w "\nTime: %{time_total}s\n"
done
```

### Get All Profiles Performance

```bash
curl -X GET http://localhost:8000/api/v1/memory-profiles \
  -H "Authorization: Bearer <TOKEN>" \
  -w "\nTime: %{time_total}s\n"
```

**Expected:** Should be fast even with 10+ profiles (< 1 second).

## Integration Testing Scenarios

### Scenario 1: New User Workflow

1. Signup new user → Should auto-create "Default" profile
2. Login as new user
3. Get profiles → Should see 1 profile (Default, is_default=true)
4. Create "Work" profile
5. Get profiles → Should see 2 profiles
6. Set "Work" as default
7. Verify Default profile is no longer default

### Scenario 2: Profile Management

1. Create multiple profiles (Work, Personal, Study)
2. Update each profile's description
3. Set different profiles as default one by one
4. Delete one profile
5. Verify remaining profiles are intact

### Scenario 3: Memory Integration (After Chat Implementation)

1. Create profile "Test"
2. Create chat session with "Test" profile
3. Have conversation that generates memories
4. Get profile details → memory_count should be > 0
5. Get profile memories → should return actual memories
6. Delete profile → verify memories are deleted from mem0

## Expected API Response Times

- **GET /memory-profiles**: < 500ms
- **POST /memory-profiles**: < 1s
- **GET /memory-profiles/{id}**: < 500ms
- **PUT /memory-profiles/{id}**: < 1s
- **DELETE /memory-profiles/{id}**: < 2s (includes mem0 cleanup)
- **POST /set-default**: < 1s
- **GET /memories**: < 1s (depends on number of memories)

## Common Issues & Solutions

### Issue: "Memory profile not found" when accessing profile
**Solution:** Verify the profile_id is correct and belongs to the authenticated user.

### Issue: Slow memory count retrieval
**Solution:** This is expected if there are many memories. Consider implementing caching in the future.

### Issue: Cannot delete profile
**Solution:** Check if it's the user's only profile. Create another one first.

### Issue: Profile name already exists
**Solution:** Each user can only have one profile with a given name. Use a different name or update the existing profile.

## Success Criteria

✅ All 7 endpoints return expected responses  
✅ Authentication required for all endpoints  
✅ Authorization prevents accessing other users' profiles  
✅ Cannot delete only profile  
✅ Only one default profile at a time  
✅ Profile deletion cascades to memories and sessions  
✅ Memory counts are accurate  
✅ Partial updates work correctly  
✅ Error messages are clear and helpful  

## Next Steps

After verifying all tests pass:
1. ✅ Checkpoint 3.10 is complete
2. Proceed to Checkpoint 3.11 (Chat Sessions endpoints)
3. Note that memories will only appear after chat implementation
4. Consider adding automated tests (pytest) for regression testing

