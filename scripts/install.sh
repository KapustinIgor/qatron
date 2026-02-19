#!/bin/bash
# First-time setup: start API (localhost:8000) and Board (localhost:3000).
# Run this once after cloning so the UI and trigger work.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
exec "$REPO_ROOT/deployment/docker-compose/install.sh" "$@"
