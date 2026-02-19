"""Configuration loader for qatron.yml."""
import os
from pathlib import Path
from typing import Dict, Optional

import yaml


class QAtronConfig:
    """QAtron configuration from qatron.yml."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration."""
        if config_path is None:
            config_path = Path("qatron.yml")
        self.config_path = config_path
        self._config: Dict = {}
        self.load()

    def load(self):
        """Load configuration from qatron.yml."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"qatron.yml not found at {self.config_path}")

        with open(self.config_path) as f:
            self._config = yaml.safe_load(f) or {}

    def get_environment(self, env_name: str) -> Dict:
        """Get environment configuration."""
        environments = self._config.get("environments", {})
        return environments.get(env_name, {})

    def get_suite(self, suite_name: str) -> Dict:
        """Get suite configuration."""
        suites = self._config.get("suites", {})
        return suites.get(suite_name, {})

    def get_coverage_threshold(self, layer: str) -> Optional[float]:
        """Get coverage threshold for a layer."""
        coverage = self._config.get("coverage", {})
        thresholds = coverage.get("thresholds", {})
        return thresholds.get(layer)

    @property
    def environments(self) -> Dict:
        """Get all environments."""
        return self._config.get("environments", {})

    @property
    def suites(self) -> Dict:
        """Get all suites."""
        return self._config.get("suites", {})


def load_config(config_path: Optional[Path] = None) -> QAtronConfig:
    """Load QAtron configuration."""
    return QAtronConfig(config_path)
