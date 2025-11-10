#!/bin/bash
# Test runner script for Step 7.2 End-to-End Testing
# Checks if backend is running and runs the comprehensive test suite

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKEND_DIR="$MEMORYCHAT_ROOT/backend"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Step 7.2 End-to-End Test Runner"
echo "=========================================="
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
    BACKEND_RUNNING=true
else
    echo -e "${YELLOW}⚠ Backend is not running${NC}"
    echo ""
    echo "The backend server must be running for Step 7.2 tests."
    echo ""
    echo "To start the backend, run in another terminal:"
    echo "  cd memorychat"
    echo "  ./scripts/start_backend.sh"
    echo ""
    echo "Or manually:"
    echo "  cd memorychat/backend"
    echo "  source .venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo -e "${YELLOW}Once the backend is running, run this test script again.${NC}"
    echo ""
    exit 1
fi

# Run the tests
echo ""
echo "Running end-to-end tests..."
echo ""

cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    exit 1
fi
source .venv/bin/activate
python test_step7_2_end_to_end.py

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests completed successfully!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $EXIT_CODE

