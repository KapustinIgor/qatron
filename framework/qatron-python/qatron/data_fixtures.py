"""Data fixtures loader."""
import json
import os
from pathlib import Path
from typing import Dict, Optional


def load_data_fixture(fixture_name: str, environment: Optional[str] = None) -> Dict:
    """
    Load a data fixture.

    Args:
        fixture_name: Name of the fixture file (without extension)
        environment: Optional environment name for environment-specific fixtures

    Returns:
        Dictionary with fixture data
    """
    # Try environment-specific fixture first
    if environment:
        env_fixture_path = Path(f"data/{environment}/{fixture_name}.json")
        if env_fixture_path.exists():
            with open(env_fixture_path) as f:
                return json.load(f)

    # Fall back to default fixture
    fixture_path = Path(f"data/{fixture_name}.json")
    if fixture_path.exists():
        with open(fixture_path) as f:
            return json.load(f)

    raise FileNotFoundError(f"Fixture not found: {fixture_name}")


def get_test_data(key: str, environment: Optional[str] = None) -> any:
    """
    Get test data by key.

    Args:
        key: Dot-separated key path (e.g., "user.email")
        environment: Optional environment name

    Returns:
        Value at the key path
    """
    env = environment or os.getenv("ENVIRONMENT", "default")
    parts = key.split(".")
    fixture_name = parts[0]
    data = load_data_fixture(fixture_name, env)

    # Navigate through nested structure
    value = data
    for part in parts[1:]:
        value = value[part]

    return value
