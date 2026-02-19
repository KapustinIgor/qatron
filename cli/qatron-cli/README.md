# QAtron CLI

Command-line interface for QAtron QA automation platform.

## Installation

### Using pipx (Recommended)

```bash
pipx install qatron
```

### Using pip

```bash
pip install qatron
```

### From Source

```bash
cd cli/qatron-cli
pip install -e .
```

## Usage

### Authentication

```bash
# Login to QAtron
qatron login

# Check authentication status
qatron auth status

# Logout
qatron logout
```

### Project Management

```bash
# Initialize a new project
qatron init my-project

# List projects
qatron projects list

# Show project details
qatron projects show <project-id>
```

### Running Tests

```bash
# Trigger a test run
qatron run --suite smoke --env staging

# With options
qatron run --suite regression --env production --branch main --commit abc123

# List runs
qatron runs list

# Get run status
qatron runs status <run-id>

# Download artifacts
qatron runs artifacts <run-id> --output ./artifacts
```

## Configuration

The CLI stores configuration in `~/.qatron/config.yaml`. You can also set environment variables:

- `QATRON_API_URL`: API base URL (default: http://localhost:8000/api/v1)
- `QATRON_TOKEN`: API authentication token

## Commands

- `qatron login` - Authenticate with QAtron
- `qatron init <name>` - Initialize a new project
- `qatron projects list` - List all projects
- `qatron projects show <id>` - Show project details
- `qatron runs run` - Trigger a test run
- `qatron runs list` - List test runs
- `qatron runs status <id>` - Get run status
- `qatron runs artifacts <id>` - Download run artifacts
