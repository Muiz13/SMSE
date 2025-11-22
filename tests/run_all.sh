#!/bin/bash
# Run all tests in the repository

echo "Running all tests..."
echo "==================="

# Run supervisor tests
echo ""
echo "Running Supervisor tests..."
pytest supervisor/tests/ -v

# Run agent tests
echo ""
echo "Running Agent tests..."
pytest agents/smart_campus_energy_agent/tests/ -v

# Run LTM tests
echo ""
echo "Running LTM tests..."
pytest agents/smart_campus_energy_agent/tests/test_ltm.py -v

echo ""
echo "All tests completed!"

