#!/bin/bash
# Startup script for MemoryChat - Starts both backend and frontend
# This script starts the backend in the background, waits for it to be ready,
# then starts the frontend and displays URLs.

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKEND_DIR="$MEMORYCHAT_ROOT/backend"
FRONTEND_DIR="$MEMORYCHAT_ROOT/frontend"

# Default ports
BACKEND_PORT=8000
FRONTEND_PORT=${FRONTEND_PORT:-8080}

# PID files for cleanup
BACKEND_PID_FILE="$MEMORYCHAT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$MEMORYCHAT_ROOT/.frontend.pid"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # Also kill any remaining processes
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "python.*http.server.*$FRONTEND_PORT" 2>/dev/null || true
    
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

# Set trap for cleanup on exit
trap cleanup EXIT INT TERM

echo "=========================================="
echo "MemoryChat - Starting All Services"
echo "=========================================="
echo ""

# Check if backend is already running
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Warning: Backend is already running on port $BACKEND_PORT${NC}"
    echo "Skipping backend startup..."
else
    echo "Starting backend server..."
    cd "$BACKEND_DIR"
    source .venv/bin/activate
    python main.py > "$MEMORYCHAT_ROOT/.backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
    
    # Wait for backend to be ready
    echo "Waiting for backend to be ready..."
    MAX_WAIT=30
    WAIT_COUNT=0
    while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
        if curl -s "http://127.0.0.1:$BACKEND_PORT/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend is ready!${NC}"
            break
        fi
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
        echo -n "."
    done
    echo ""
    
    if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
        echo -e "${RED}Error: Backend did not start within $MAX_WAIT seconds${NC}"
        echo "Check logs at: $MEMORYCHAT_ROOT/.backend.log"
        exit 1
    fi
fi

# Start frontend
echo ""
echo "Starting frontend server..."
cd "$FRONTEND_DIR"
python3 -m http.server $FRONTEND_PORT > "$MEMORYCHAT_ROOT/.frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait a moment for frontend to start
sleep 2

# Display URLs
echo ""
echo "=========================================="
echo -e "${GREEN}✓ All services are running!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Backend API:${NC}"
echo "  URL: http://127.0.0.1:$BACKEND_PORT"
echo "  Docs: http://127.0.0.1:$BACKEND_PORT/docs"
echo "  Health: http://127.0.0.1:$BACKEND_PORT/health"
echo ""
echo -e "${BLUE}Frontend:${NC}"
echo "  URL: http://127.0.0.1:$FRONTEND_PORT/index.html"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  Backend: $MEMORYCHAT_ROOT/.backend.log"
echo "  Frontend: $MEMORYCHAT_ROOT/.frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Try to open browser
if command -v xdg-open &> /dev/null; then
    # Linux
    sleep 1 && xdg-open "http://127.0.0.1:$FRONTEND_PORT/index.html" > /dev/null 2>&1 &
elif command -v open &> /dev/null; then
    # macOS
    sleep 1 && open "http://127.0.0.1:$FRONTEND_PORT/index.html" > /dev/null 2>&1 &
fi

# Wait for user interrupt
wait

