# How to Run MemoryChat Application

This guide provides step-by-step instructions to run both the backend API server and frontend web interface.

---

## Prerequisites

1. **Python 3.8+** installed
2. **Virtual environment** created (if not exists)
3. **Dependencies** installed
4. **Database** initialized
5. **Environment variables** configured

---

## Part 1: Start Backend Server

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

### Step 3: Verify Environment Setup
```bash
# Check if .env file exists
ls -la .env

# If .env doesn't exist, create it:
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

**Note:** Replace `your-api-key-here` with your actual OpenAI API key if you want to use LLM features.

### Step 4: Initialize Database (if needed)
```bash
# Only run this if database doesn't exist
python ../scripts/init_database.py
```

### Step 5: Start Backend Server

**Option A: Using main.py (Recommended)**
```bash
python main.py
```

**Option B: Using uvicorn directly**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Option C: Run in background**
```bash
nohup python main.py > server.log 2>&1 &
```

### Step 6: Verify Backend is Running
```bash
# In another terminal, test the health endpoint:
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"healthy","service":"MemoryChat Multi-Agent API"}
```

**Backend will be available at:** http://127.0.0.1:8000

**API Documentation:**
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Part 2: Start Frontend Server

### Option A: Using Python HTTP Server (Recommended)

**Step 1: Navigate to Frontend Directory**
```bash
cd memorychat/frontend
```

**Step 2: Start HTTP Server**
```bash
# Python 3:
python3 -m http.server 8080

# Or Python 2:
python -m SimpleHTTPServer 8080
```

**Step 3: Open in Browser**
Open your browser and navigate to:
- **Main Application:** http://127.0.0.1:8080/index.html
- **Test Interface:** http://127.0.0.1:8080/test.html

### Option B: Using Node.js HTTP Server

If you have Node.js installed:
```bash
cd memorychat/frontend
npx http-server -p 8080
```

### Option C: Open Directly in Browser

You can also open the HTML files directly:
```bash
# Linux/Mac:
open memorychat/frontend/index.html
# Or:
xdg-open memorychat/frontend/index.html

# Windows:
start memorychat/frontend/index.html
```

**Note:** Opening directly may have CORS limitations. Using an HTTP server is recommended.

---

## Quick Start Script

Create a script to start both servers:

### Linux/Mac: `start_all.sh`
```bash
#!/bin/bash

# Start backend in background
cd memorychat/backend
source .venv/bin/activate
python main.py > ../server.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
sleep 3

# Start frontend
cd ../frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "Servers are running!"
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://127.0.0.1:8080/index.html"
echo "API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "To stop servers, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "=========================================="
```

Make it executable:
```bash
chmod +x start_all.sh
./start_all.sh
```

### Windows: `start_all.bat`
```batch
@echo off

REM Start backend
cd memorychat\backend
call .venv\Scripts\activate
start "Backend Server" python main.py

REM Wait for backend
timeout /t 3

REM Start frontend
cd ..\frontend
start "Frontend Server" python -m http.server 8080

echo.
echo ==========================================
echo Servers are running!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:8080/index.html
echo API Docs: http://127.0.0.1:8000/docs
echo ==========================================
pause
```

---

## Stopping Servers

### Stop Backend Server

**If running in foreground:**
- Press `Ctrl+C`

**If running in background:**
```bash
# Find the process
ps aux | grep "python.*main.py"

# Kill the process
kill <PID>

# Or kill all Python processes (be careful!)
pkill -f "python.*main.py"
```

**Kill by port:**
```bash
# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Stop Frontend Server

**If running in foreground:**
- Press `Ctrl+C`

**If running in background:**
```bash
# Find the process
ps aux | grep "http.server"

# Kill the process
kill <PID>

# Or kill by port:
lsof -ti:8080 | xargs kill -9
```

### Stop All Servers
```bash
# Kill all server processes
pkill -f "python.*main.py"
pkill -f "uvicorn"
pkill -f "http.server"

# Or kill by ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

---

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use` or `Port 8000 is already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process
kill <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or use different port
# Edit .env file: API_PORT=8001
# Or: uvicorn main:app --port 8001
```

### Backend Not Starting

**Check:**
1. Virtual environment is activated
2. Dependencies are installed: `pip install -r requirements.txt`
3. Database exists: `python ../scripts/init_database.py`
4. .env file exists and is configured

### Frontend Can't Connect to Backend

**Check:**
1. Backend is running: `curl http://127.0.0.1:8000/health`
2. CORS is configured (already done in main.py)
3. API URL in `js/config.js` matches backend URL
4. No firewall blocking connections

### CORS Errors in Browser

**Solution:**
- Make sure you're accessing frontend via HTTP server (not file://)
- Check CORS configuration in `backend/main.py`
- Verify API_BASE_URL in `frontend/js/config.js`

---

## Development Workflow

### Typical Development Session

1. **Start Backend:**
   ```bash
   cd memorychat/backend
   source .venv/bin/activate
   python main.py
   ```

2. **Start Frontend (in another terminal):**
   ```bash
   cd memorychat/frontend
   python3 -m http.server 8080
   ```

3. **Open Browser:**
   - Frontend: http://127.0.0.1:8080/index.html
   - API Docs: http://127.0.0.1:8000/docs

4. **Make Changes:**
   - Backend: Auto-reloads (if using --reload)
   - Frontend: Refresh browser

5. **Stop Servers:**
   - Press `Ctrl+C` in each terminal

---

## Production Deployment

For production, use proper web servers:

**Backend:**
```bash
# Using gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
- Use nginx, Apache, or any static file server
- Or deploy to services like Netlify, Vercel, GitHub Pages

---

## Summary

**Backend:**
- Location: `memorychat/backend`
- Command: `python main.py`
- URL: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

**Frontend:**
- Location: `memorychat/frontend`
- Command: `python3 -m http.server 8080`
- URL: http://127.0.0.1:8080/index.html

**Both servers must be running for the application to work!**

