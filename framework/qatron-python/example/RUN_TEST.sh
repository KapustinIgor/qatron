#!/bin/bash
# Quick script to run Amazon E2E test

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export ENVIRONMENT=amazon
export SELENIUM_GRID_URL=http://localhost:4444/wd/hub
export PYTHONPATH=..:$PYTHONPATH

# Run test
pytest test_amazon.py -v --tb=short
