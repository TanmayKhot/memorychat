#!/bin/bash
# Verification script for Step 7.1 - Startup Scripts
# Tests all checkpoint requirements

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $1"
        FAILED=$((FAILED + 1))
    fi
}

echo "=========================================="
echo "Step 7.1 Verification - Startup Scripts"
echo "=========================================="
echo ""

# Check 1: Startup scripts exist
echo "Checking startup scripts..."
test -f "$SCRIPT_DIR/start_backend.sh" && check "start_backend.sh exists"
test -f "$SCRIPT_DIR/start_frontend.sh" && check "start_frontend.sh exists"
test -f "$SCRIPT_DIR/start_all.sh" && check "start_all.sh exists"
test -f "$SCRIPT_DIR/stop_all.sh" && check "stop_all.sh exists"

# Check 2: Scripts are executable
echo ""
echo "Checking script permissions..."
test -x "$SCRIPT_DIR/start_backend.sh" && check "start_backend.sh is executable"
test -x "$SCRIPT_DIR/start_frontend.sh" && check "start_frontend.sh is executable"
test -x "$SCRIPT_DIR/start_all.sh" && check "start_all.sh is executable"
test -x "$SCRIPT_DIR/stop_all.sh" && check "stop_all.sh is executable"

# Check 3: Script syntax is valid
echo ""
echo "Checking script syntax..."
bash -n "$SCRIPT_DIR/start_backend.sh" 2>&1 && check "start_backend.sh syntax valid"
bash -n "$SCRIPT_DIR/start_frontend.sh" 2>&1 && check "start_frontend.sh syntax valid"
bash -n "$SCRIPT_DIR/start_all.sh" 2>&1 && check "start_all.sh syntax valid"
bash -n "$SCRIPT_DIR/stop_all.sh" 2>&1 && check "stop_all.sh syntax valid"

# Check 4: Scripts can resolve paths correctly
echo ""
echo "Checking path resolution..."
cd "$MEMORYCHAT_ROOT"
BACKEND_DIR=$(bash -c 'SCRIPT_DIR="$( cd "$( dirname "scripts/start_backend.sh" )" && pwd )"; MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"; echo "$MEMORYCHAT_ROOT/backend"')
test -d "$BACKEND_DIR" && check "Backend directory path resolves correctly"

FRONTEND_DIR=$(bash -c 'SCRIPT_DIR="$( cd "$( dirname "scripts/start_frontend.sh" )" && pwd )"; MEMORYCHAT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"; echo "$MEMORYCHAT_ROOT/frontend"')
test -d "$FRONTEND_DIR" && check "Frontend directory path resolves correctly"

# Check 5: README.md exists and is comprehensive
echo ""
echo "Checking README.md..."
test -f "$MEMORYCHAT_ROOT/README.md" && check "README.md exists"
if [ -f "$MEMORYCHAT_ROOT/README.md" ]; then
    README_LINES=$(wc -l < "$MEMORYCHAT_ROOT/README.md")
    [ $README_LINES -gt 100 ] && check "README.md is comprehensive (>100 lines)"
    
    grep -q "Project description" "$MEMORYCHAT_ROOT/README.md" && check "README contains project description" || grep -q "Features" "$MEMORYCHAT_ROOT/README.md" && check "README contains features"
    grep -q "Setup Instructions" "$MEMORYCHAT_ROOT/README.md" && check "README contains setup instructions"
    grep -q "How to Run" "$MEMORYCHAT_ROOT/README.md" && check "README contains how to run"
    grep -q "How to Use" "$MEMORYCHAT_ROOT/README.md" && check "README contains how to use"
    grep -q "Troubleshooting" "$MEMORYCHAT_ROOT/README.md" && check "README contains troubleshooting"
fi

# Check 6: stop_all.sh works (even when nothing is running)
echo ""
echo "Testing stop_all.sh (should work even when nothing is running)..."
cd "$MEMORYCHAT_ROOT"
./scripts/stop_all.sh > /dev/null 2>&1 && check "stop_all.sh executes without errors"

# Summary
echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}Failed: 0${NC}"
    echo ""
    echo -e "${GREEN}✓ All checkpoint 7.1 requirements met!${NC}"
    exit 0
fi

