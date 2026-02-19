#!/bin/bash
set -e

# Execute the worker job
python -m app.executor "$@"
