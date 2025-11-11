#!/bin/bash
# Stop script for MemoryChat - Stops both backend and frontend processes
# This script finds and stops all running MemoryChat processes.

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# PID files
BACKEND_PID_FILE="$MEMORYCHAT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$MEMORYCHAT_ROOT/.frontend.pid"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "MemoryChat - Stopping All Services"
echo "=========================================="
echo ""

STOPPED=0

# Stop frontend
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 1
        if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend stopped${NC}"
            STOPPED=$((STOPPED + 1))
        else
            echo -e "${YELLOW}Force killing frontend...${NC}"
            kill -9 $FRONTEND_PID 2>/dev/null || true
            echo -e "${GREEN}✓ Frontend stopped${NC}"
            STOPPED=$((STOPPED + 1))
        fi
    fi
    rm -f "$FRONTEND_PID_FILE"
fi

# Stop backend
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        sleep 2
        if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend stopped${NC}"
            STOPPED=$((STOPPED + 1))
        else
            echo -e "${YELLOW}Force killing backend...${NC}"
            kill -9 $BACKEND_PID 2>/dev/null || true
            echo -e "${GREEN}✓ Backend stopped${NC}"
            STOPPED=$((STOPPED + 1))
        fi
    fi
    rm -f "$BACKEND_PID_FILE"
fi

# Also kill any processes by pattern (in case PID files are missing)
echo "Checking for remaining processes..."

# Kill backend processes
BACKEND_PROCESSES=$(pgrep -f "python.*main.py" 2>/dev/null || true)
if [ ! -z "$BACKEND_PROCESSES" ]; then
    echo "Found backend processes: $BACKEND_PROCESSES"
    pkill -f "python.*main.py" 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ Backend processes stopped${NC}"
    STOPPED=$((STOPPED + 1))
fi

# Kill frontend HTTP server processes
FRONTEND_PROCESSES=$(pgrep -f "python.*http.server" 2>/dev/null || true)
if [ ! -z "$FRONTEND_PROCESSES" ]; then
    echo "Found frontend processes: $FRONTEND_PROCESSES"
    pkill -f "python.*http.server" 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ Frontend processes stopped${NC}"
    STOPPED=$((STOPPED + 1))
fi

# Clean up log files
if [ -f "$MEMORYCHAT_ROOT/.backend.log" ]; then
    rm -f "$MEMORYCHAT_ROOT/.backend.log"
fi
if [ -f "$MEMORYCHAT_ROOT/.frontend.log" ]; then
    rm -f "$MEMORYCHAT_ROOT/.frontend.log"
fi

echo ""
if [ $STOPPED -eq 0 ]; then
    echo -e "${YELLOW}No running services found${NC}"
else
    echo -e "${GREEN}✓ All services stopped successfully${NC}"
fi
echo ""


