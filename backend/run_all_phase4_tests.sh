#!/bin/bash

cd memorychat/backend

echo "=========================================="
echo "PHASE 4 COMPREHENSIVE TESTING"
echo "=========================================="
echo ""

echo "1. Structural Verification Tests"
echo "--------------------------------"
for script in verify_step4_*.py; do
    echo "Testing $script..."
    python3 "$script" 2>&1 | grep -E "(Success Rate|Total Checks|Passed)" | tail -3
done

echo ""
echo "2. Functional Tests"
echo "-------------------"
for script in test_step4_*_functional.py; do
    echo "Testing $script..."
    python3 "$script" 2>&1 | grep -E "(Success Rate|Total Checks|Passed)" | tail -3
done

echo ""
echo "3. Integration Test"
echo "--------------------"
python3 test_phase4_integration.py 2>&1 | grep -E "(Success Rate|Total Checks|Passed)" | tail -3

echo ""
echo "4. End-to-End Test"
echo "------------------"
python3 test_phase4_end_to_end.py 2>&1 | grep -E "(Success Rate|Total Checks|Passed)" | tail -3

echo ""
echo "=========================================="
echo "ALL TESTS COMPLETE"
echo "=========================================="
