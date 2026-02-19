"""CLI configuration management."""
import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """CLI configuration."""

    def __init__(self):
        """Initialize configuration."""
        self.config_dir = Path.home() / ".qatron"
        self.config_file = self.config_dir / "config.yaml"
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return yaml.safe_load(f) or {}
        return {}

    def get_api_url(self) -> str:
        """Get API URL from config or environment."""
        return (
            self._config.get("api_url")
            or os.getenv("QATRON_API_URL")
            or "http://localhost:8000/api/v1"
        )

    def get_token(self) -> Optional[str]:
        """Get API token from config or environment."""
        return self._config.get("token") or os.getenv("QATRON_TOKEN")

    def set_api_url(self, url: str):
        """Set API URL in config."""
        self._config["api_url"] = url
        self._save_config()

    def set_token(self, token: str):
        """Set API token in config."""
        self._config["token"] = token
        self._save_config()

    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            yaml.dump(self._config, f)


config = Config()
