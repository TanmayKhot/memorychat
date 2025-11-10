#!/bin/bash
# Startup script for MemoryChat Frontend
# This script starts a simple HTTP server for the HTML/JS frontend
# and optionally opens the browser.

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
FRONTEND_DIR="$MEMORYCHAT_ROOT/frontend"

# Default port for frontend
FRONTEND_PORT=${FRONTEND_PORT:-8080}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "MemoryChat Frontend Startup Script"
echo "=========================================="
echo ""

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found at $FRONTEND_DIR${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Check if port is already in use
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Warning: Port $FRONTEND_PORT is already in use${NC}"
    echo "Trying to find an available port..."
    for port in 8081 8082 8083 8084 8085; do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            FRONTEND_PORT=$port
            echo -e "${GREEN}Using port $FRONTEND_PORT instead${NC}"
            break
        fi
    done
fi

# Start HTTP server
echo "Starting HTTP server on port $FRONTEND_PORT..."
echo ""
echo -e "${GREEN}Frontend will be available at: http://127.0.0.1:$FRONTEND_PORT${NC}"
echo -e "${GREEN}Main page: http://127.0.0.1:$FRONTEND_PORT/index.html${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$FRONTEND_DIR"

# Try to open browser (non-blocking)
if command -v xdg-open &> /dev/null; then
    # Linux
    (sleep 2 && xdg-open "http://127.0.0.1:$FRONTEND_PORT/index.html" > /dev/null 2>&1) &
elif command -v open &> /dev/null; then
    # macOS
    (sleep 2 && open "http://127.0.0.1:$FRONTEND_PORT/index.html" > /dev/null 2>&1) &
fi

# Start Python HTTP server
python3 -m http.server $FRONTEND_PORT

