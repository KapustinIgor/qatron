"""Artifact collection utilities."""
from pathlib import Path
from typing import Dict, Optional


class ArtifactCollector:
    """Collects test artifacts."""

    def __init__(self, config):
        """Initialize artifact collector."""
        self.config = config

    def collect(self, workspace: Path, run_id: int, shard_index: int) -> Dict[str, Optional[str]]:
        """
        Collect all artifacts from test execution.

        Returns:
            Dictionary mapping artifact types to file paths
        """
        artifacts = {
            "allure": None,
            "coverage_xml": None,
            "coverage_html": None,
            "screenshots": None,
            "logs": None,
            "videos": None,
        }

        # Collect Allure results
        allure_results = workspace / "allure-results"
        if allure_results.exists() and any(allure_results.iterdir()):
            # Create zip of allure results
            import zipfile
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in allure_results.rglob("*"):
                        if file.is_file():
                            zipf.write(file, file.relative_to(allure_results))
                artifacts["allure"] = tmp.name

        # Collect coverage reports
        coverage_xml = workspace / "coverage.xml"
        if coverage_xml.exists():
            artifacts["coverage_xml"] = str(coverage_xml)

        coverage_html = workspace / "htmlcov"
        if coverage_html.exists() and coverage_html.is_dir():
            # Create zip of HTML coverage
            import zipfile
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in coverage_html.rglob("*"):
                        if file.is_file():
                            zipf.write(file, file.relative_to(coverage_html))
                artifacts["coverage_html"] = tmp.name

        # Collect screenshots (common locations)
        screenshot_dirs = [
            workspace / "screenshots",
            workspace / "test-results" / "screenshots",
        ]
        for screenshot_dir in screenshot_dirs:
            if screenshot_dir.exists() and any(screenshot_dir.rglob("*.png")):
                import zipfile
                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for file in screenshot_dir.rglob("*.png"):
                            zipf.write(file, file.name)
                    artifacts["screenshots"] = tmp.name
                break

        # Collect logs
        log_files = list(workspace.rglob("*.log"))
        if log_files:
            import zipfile
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for log_file in log_files:
                        zipf.write(log_file, log_file.name)
                artifacts["logs"] = tmp.name

        return artifacts
