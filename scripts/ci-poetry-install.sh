#!/usr/bin/env bash
# Install Poetry deps only (no project package). Used by CI to avoid "No file/folder found for package".
set -e
cd "$(dirname "$0")/../services/control-plane" && poetry install --no-root
cd "$(dirname "$0")/../services/orchestrator" && poetry install --no-root
cd "$(dirname "$0")/../services/worker" && poetry install --no-root
