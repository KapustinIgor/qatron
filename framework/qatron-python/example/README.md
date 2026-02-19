# QAtron Example Project - Amazon E2E Testing

This example project demonstrates E2E testing of www.amazon.com using QAtron.

## IDE / Linting

If your editor reports **"Import pytest_bdd could not be resolved"**, use this project’s venv as the Python interpreter: choose the interpreter at `example/venv/bin/python` (or `example\\venv\\Scripts\\python.exe` on Windows). The repo’s `pyrightconfig.json` adds this venv to the analysis path when present.

## Quick Start

### 1. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Amazon E2E Test

```bash
# Activate virtual environment first
source venv/bin/activate

# Set environment variables
export ENVIRONMENT=amazon
export SELENIUM_GRID_URL=http://localhost:4444/wd/hub

# Run the test
pytest test_amazon.py -v --tb=short
```

### 3. Run with Browser Options

```bash
# Activate virtual environment first
source venv/bin/activate

# Run headless (no browser window)
export HEADLESS=true
export BROWSER=chrome
export ENVIRONMENT=amazon
export SELENIUM_GRID_URL=http://localhost:4444/wd/hub
pytest test_amazon.py -v
```

## Project Structure

- `features/` - BDD feature files (Gherkin)
- `steps/` - Step definitions (Python)
- `qatron.yml` - QAtron configuration (environments, suites)
- `conftest.py` - pytest configuration (imports QAtron fixtures)

## Environments

Configured in `qatron.yml`:
- `amazon` - https://www.amazon.com (for E2E testing)
- `local` - http://localhost:3000 (for local development)
- `staging` - staging.example.com
- `production` - example.com

## Running Tests

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Set required environment variables
export ENVIRONMENT=amazon
export SELENIUM_GRID_URL=http://localhost:4444/wd/hub

# Run the Amazon test
pytest test_amazon.py -v

# Run with HTML report
pytest test_amazon.py --html=report.html --self-contained-html
```

## Prerequisites

- QAtron platform running (Docker Compose)
- Selenium Grid ready at http://localhost:4444
- Python 3.11+
- Dependencies installed (`pip install -r requirements.txt`)
