#!/bin/bash
# Script to run Step 7.4 Performance Tests

cd "$(dirname "$0")/../backend" || exit 1

echo "=========================================="
echo "Step 7.4: Performance Testing"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if server is running
if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "Warning: Server does not appear to be running."
    echo "Please start the backend server first:"
    echo "  ./scripts/start_backend.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run performance tests
echo "Running performance tests..."
echo ""
python3 test_step7_4_performance.py

echo ""
echo "=========================================="
echo "Performance testing complete!"
echo "=========================================="


