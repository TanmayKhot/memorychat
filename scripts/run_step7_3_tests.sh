#!/bin/bash
# Test runner script for Step 7.3 Agent Testing
# Runs comprehensive agent tests

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
echo "Step 7.3 Agent Test Runner"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    cd "$BACKEND_DIR"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Run the tests
echo "Running agent tests..."
echo ""
echo -e "${YELLOW}Note: Some tests may require OpenAI API key for full functionality${NC}"
echo ""

cd "$BACKEND_DIR"
source .venv/bin/activate
python test_step7_3_agent_testing.py

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests completed!${NC}"
    echo ""
    echo -e "${YELLOW}Note: Some tests may show failures if OpenAI API key is not configured.${NC}"
    echo -e "${YELLOW}This is expected and does not indicate a problem with the test suite.${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $EXIT_CODE


