#!/bin/bash
# Startup script for MemoryChat Backend Server
# This script activates the virtual environment, sets environment variables,
# initializes the database if needed, and starts the FastAPI server.

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKEND_DIR="$MEMORYCHAT_ROOT/backend"
DATA_DIR="$MEMORYCHAT_ROOT/data"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "MemoryChat Backend Startup Script"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating it...${NC}"
    cd "$BACKEND_DIR"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$BACKEND_DIR/.venv/bin/activate"

# Check if .env file exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found in $BACKEND_DIR${NC}"
    echo "Creating .env file from defaults..."
    cat > "$BACKEND_DIR/.env" << EOF
OPENAI_API_KEY=your-api-key-here
ENVIRONMENT=development
LOG_LEVEL=DEBUG
SQLITE_DATABASE_PATH=../data/sqlite/memorychat.db
CHROMADB_PATH=../data/chromadb
API_HOST=127.0.0.1
API_PORT=8000
EOF
    echo -e "${YELLOW}Please update $BACKEND_DIR/.env with your OpenAI API key${NC}"
fi

# Check if database directory exists
if [ ! -d "$DATA_DIR/sqlite" ]; then
    echo "Creating database directory..."
    mkdir -p "$DATA_DIR/sqlite"
fi

# Check if database exists, initialize if needed
DB_PATH="$DATA_DIR/sqlite/memorychat.db"
if [ ! -f "$DB_PATH" ]; then
    echo ""
    echo -e "${YELLOW}Database not found. The database will be initialized on first server start.${NC}"
    echo "The database will be created automatically when the server starts."
fi

# Install/update dependencies
echo ""
echo "Checking dependencies..."
cd "$BACKEND_DIR"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies ready${NC}"

# Start the server
echo ""
echo "=========================================="
echo "Starting FastAPI server..."
echo "=========================================="
echo ""
echo -e "${GREEN}Server will start at: http://127.0.0.1:8000${NC}"
echo -e "${GREEN}API Documentation: http://127.0.0.1:8000/docs${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$BACKEND_DIR"
python main.py

