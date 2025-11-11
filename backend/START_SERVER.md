# How to Run the Backend Server

This guide explains how to start the MemoryChat Multi-Agent API backend server.

## Prerequisites

1. **Python 3.8+ installed**
2. **Virtual environment created and activated**
3. **Dependencies installed**
4. **Database initialized**
5. **Environment variables configured**

---

## Quick Start

### Step 1: Navigate to Backend Directory
```bash
cd memorychat/backend
```

### Step 2: Activate Virtual Environment
```bash
# Linux/Mac:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### Step 3: Start the Server
```bash
python main.py
```

The server will start on **http://127.0.0.1:8000**

---

## Detailed Instructions

### 1. Check Prerequisites

**Check Python version:**
```bash
python3 --version
# Should be 3.8 or higher
```

**Check if virtual environment exists:**
```bash
cd memorychat/backend
ls -la .venv
# Should show .venv directory
```

**If virtual environment doesn't exist, create it:**
```bash
cd memorychat/backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

**If dependencies aren't installed:**
```bash
cd memorychat/backend
source .venv/bin/activate
pip install -r requirements.txt
pip install email-validator  # Required for EmailStr validation
```

### 3. Configure Environment

**Check if .env file exists:**
```bash
cd memorychat/backend
ls -la .env
```

**If .env doesn't exist, create it:**
```bash
cd memorychat/backend
cp .env.example .env  # If .env.example exists
# OR create manually:
cat > .env << EOF
OPENAI_API_KEY=your-api-key-here
ENVIRONMENT=development
LOG_LEVEL=DEBUG
SQLITE_DATABASE_PATH=../data/sqlite/memorychat.db
CHROMADB_PATH=../data/chromadb
API_HOST=127.0.0.1
API_PORT=8000
EOF
```

**Important:** Replace `your-api-key-here` with your actual OpenAI API key if you want to use LLM features.

### 4. Initialize Database

**If database doesn't exist:**
```bash
cd memorychat/backend
source .venv/bin/activate
python ../scripts/init_database.py
```

This will:
- Create the SQLite database
- Create all tables
- Create a default demo user
- Initialize ChromaDB

### 5. Start the Server

**Method 1: Using main.py (Recommended)**
```bash
cd memorychat/backend
source .venv/bin/activate
python main.py
```

**Method 2: Using uvicorn directly**
```bash
cd memorychat/backend
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Method 3: Run in background**
```bash
cd memorychat/backend
source .venv/bin/activate
nohup python main.py > server.log 2>&1 &
```

---

## Verify Server is Running

### Check Health Endpoint
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status":"healthy","service":"MemoryChat Multi-Agent API"}
```

### Check Root Endpoint
```bash
curl http://127.0.0.1:8000/
```

Expected response:
```json
{"message":"MemoryChat Multi-Agent API","status":"running"}
```

### Check API Documentation
Open in browser:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## Server Configuration

The server configuration is in `config/settings.py` and can be overridden with `.env`:

- **API_HOST:** Server host (default: 127.0.0.1)
- **API_PORT:** Server port (default: 8000)
- **LOG_LEVEL:** Logging level (default: DEBUG)
- **ENVIRONMENT:** Environment mode (default: development)

---

## Common Issues and Solutions

### Issue: Port Already in Use
**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process
kill <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# OR use a different port
uvicorn main:app --port 8001
```

### Issue: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install email-validator
```

### Issue: Database Not Found
**Error:** `Database file not found`

**Solution:**
```bash
python ../scripts/init_database.py
```

### Issue: Import Errors
**Error:** `ImportError` or `ModuleNotFoundError`

**Solution:**
1. Make sure virtual environment is activated
2. Check you're in the backend directory
3. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Issue: CORS Errors (when testing from browser)
**Error:** `CORS policy` errors

**Solution:**
- CORS is already configured in `main.py` for localhost
- Make sure you're accessing from http://127.0.0.1:8000 or http://localhost:8000
- Check CORS middleware configuration in `main.py`

---

## Server Logs

### View Logs in Real-Time
If running in foreground, logs appear in terminal.

### View Log Files
```bash
cd memorychat/backend
tail -f logs/app.log        # Application logs
tail -f logs/errors.log     # Error logs
tail -f logs/database.log   # Database logs
```

### Log Locations
- `logs/app.log` - General application logs
- `logs/errors.log` - Error logs only
- `logs/database.log` - Database operation logs
- `logs/agents/` - Agent-specific logs

---

## Stopping the Server

### If Running in Foreground
Press `Ctrl+C` to stop

### If Running in Background
```bash
# Find the process
ps aux | grep "python.*main.py"

# Kill the process
kill <PID>

# OR kill all Python processes (be careful!)
pkill -f "python.*main.py"
```

---

## Production Deployment

For production, use a production ASGI server:

```bash
# Install production server
pip install gunicorn

# Run with gunicorn + uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or use uvicorn with production settings:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Quick Reference

```bash
# Complete startup sequence
cd memorychat/backend
source .venv/bin/activate
python main.py

# In another terminal, test it:
curl http://127.0.0.1:8000/health

# Or open browser:
# http://127.0.0.1:8000/docs
```

---

## Next Steps

Once the server is running:

1. **Test the API:**
   - Open Swagger UI: http://127.0.0.1:8000/docs
   - Or run test script: `python test_step5_2_auto.py`

2. **Test the UI:**
   - Open test UI: http://127.0.0.1:8080/test-ui.html
   - (Requires frontend server running)

3. **Use the API:**
   - All endpoints are available at: http://127.0.0.1:8000/api
   - See API documentation at: http://127.0.0.1:8000/docs


