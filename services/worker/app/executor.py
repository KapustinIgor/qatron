"""Worker job executor."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict

import boto3
import httpx
import yaml
from git import Repo

from app.config import get_config
from app.artifact_collector import ArtifactCollector


def main():
    """Main entry point for worker execution."""
    if len(sys.argv) < 2:
        print("Usage: executor.py <job_payload_json>")
        sys.exit(1)

    job_payload = json.loads(sys.argv[1])
    executor = JobExecutor(job_payload)
    executor.execute()


class JobExecutor:
    """Executes a test job."""

    def __init__(self, job_payload: Dict):
        """Initialize executor with job payload."""
        self.job_payload = job_payload
        self.run_id = job_payload.get("run_id")
        self.shard_index = job_payload.get("shard_index", 0)
        self.shard_total = job_payload.get("shard_total", 1)
        self.workspace = Path(os.getenv("WORKSPACE_DIR", "/workspace"))
        self.config = get_config()
        self.artifact_collector = ArtifactCollector(self.config)

    def execute(self):
        """Execute the test job."""
        try:
            # Step 1: Clone repository
            self.clone_repository()

            # Step 2: Load qatron.yml
            qatron_config = self.load_qatron_config()

            # Step 3: Install dependencies
            self.install_dependencies()

            # Step 4: Execute tests
            test_results = self.run_tests(qatron_config)

            # Step 5: Collect artifacts
            artifacts = self.artifact_collector.collect(self.workspace, self.run_id, self.shard_index)

            # Step 6: Upload artifacts to S3
            self.upload_artifacts(artifacts)

            # Step 7: Post results to Control Plane
            self.post_results(test_results, artifacts)

            # Step 8: Cleanup
            self.cleanup()

            sys.exit(0)

        except Exception as e:
            print(f"Error executing job: {e}", file=sys.stderr)
            self.post_error(str(e))
            sys.exit(1)

    def clone_repository(self):
        """Clone the repository at the specified commit."""
        repo_url = os.getenv("REPO_URL")
        commit = os.getenv("COMMIT", "HEAD")
        repo_auth_method = os.getenv("REPO_AUTH_METHOD", "token")

        if not repo_url:
            raise ValueError("REPO_URL environment variable not set")

        # Prepare repo URL with authentication
        if repo_auth_method == "token":
            token = os.getenv("REPO_TOKEN")
            if token:
                # Insert token into URL
                if repo_url.startswith("https://"):
                    repo_url = repo_url.replace("https://", f"https://{token}@")
        elif repo_auth_method == "ssh":
            # SSH keys should be mounted in container
            pass

        # Clone repository
        print(f"Cloning repository: {repo_url}")
        Repo.clone_from(repo_url, self.workspace, depth=1)

        # Checkout specific commit if provided
        if commit and commit != "HEAD":
            repo = Repo(self.workspace)
            repo.git.checkout(commit)
            print(f"Checked out commit: {commit}")

    def load_qatron_config(self) -> Dict:
        """Load qatron.yml configuration."""
        config_path = self.workspace / "qatron.yml"
        if not config_path.exists():
            raise FileNotFoundError("qatron.yml not found in repository")

        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config

    def install_dependencies(self):
        """Install project dependencies."""
        requirements_file = self.workspace / "requirements.txt"
        if requirements_file.exists():
            print("Installing Python dependencies...")
            subprocess.run(
                ["pip", "install", "-r", str(requirements_file)],
                cwd=self.workspace,
                check=True,
            )

        # Install qatron framework if needed
        subprocess.run(
            ["pip", "install", "qatron-python"],
            check=True,
        )

    def run_tests(self, qatron_config: Dict) -> Dict:
        """Run tests using pytest."""
        suite_name = os.getenv("SUITE_NAME", "default")
        environment = os.getenv("ENVIRONMENT", "default")
        layer = os.getenv("LAYER", "e2e")

        # Build pytest command
        cmd = ["pytest"]

        # Add markers based on layer and suite (suite_default, suite_smoke, etc.)
        if layer:
            cmd.extend(["-m", layer])
        if suite_name:
            suite_marker = f"suite_{suite_name.replace('-', '_')}"
            cmd.extend(["-m", suite_marker])

        # Add sharding if configured
        if self.shard_total > 1:
            cmd.extend(["--dist", "loadgroup", "-n", str(self.shard_total)])
            cmd.extend(["--dist", "loadfile"])
            # pytest-xdist sharding
            cmd.extend(["-n", str(self.shard_total)])

        # Add Allure reporting
        allure_results_dir = self.workspace / "allure-results"
        allure_results_dir.mkdir(exist_ok=True)
        cmd.extend(["--alluredir", str(allure_results_dir)])

        # Add coverage
        cmd.extend(["--cov", ".", "--cov-report", "xml", "--cov-report", "html"])

        # Add test directory
        test_dir = qatron_config.get("test_dir", "tests")
        cmd.append(str(self.workspace / test_dir))

        # Set environment variables
        env = os.environ.copy()
        env.update(qatron_config.get("environments", {}).get(environment, {}))

        print(f"Running tests: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=self.workspace, env=env, capture_output=True, text=True)

        # Parse test results
        test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "exit_code": result.returncode,
        }

        # Parse pytest output (simplified)
        if result.stdout:
            for line in result.stdout.split("\n"):
                if "passed" in line.lower():
                    test_results["passed"] += 1
                    test_results["total"] += 1
                elif "failed" in line.lower():
                    test_results["failed"] += 1
                    test_results["total"] += 1
                elif "skipped" in line.lower():
                    test_results["skipped"] += 1
                    test_results["total"] += 1

        return test_results

    def upload_artifacts(self, artifacts: Dict):
        """Upload artifacts to S3."""
        s3_client = boto3.client(
            "s3",
            endpoint_url=self.config.s3_endpoint_url,
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            region_name=self.config.s3_region,
        )

        for artifact_type, artifact_path in artifacts.items():
            if artifact_path and Path(artifact_path).exists():
                s3_key = f"runs/{self.run_id}/shard-{self.shard_index}/{artifact_type}/{Path(artifact_path).name}"
                print(f"Uploading {artifact_type} to S3: {s3_key}")
                s3_client.upload_file(
                    artifact_path,
                    self.config.s3_bucket_name,
                    s3_key,
                )

    def post_results(self, test_results: Dict, artifacts: Dict):
        """Post results to Control Plane API (internal endpoint or PUT /runs with token)."""
        control_plane_url = os.getenv("CONTROL_PLANE_API_URL", "http://control-plane:8000/api/v1").rstrip("/")
        api_token = os.getenv("API_TOKEN")
        internal_secret = os.getenv("INTERNAL_API_SECRET")

        status = "completed" if test_results["exit_code"] == 0 else "failed"
        payload = {
            "status": status,
            "total_tests": test_results["total"],
            "passed_tests": test_results["passed"],
            "failed_tests": test_results["failed"],
            "skipped_tests": test_results["skipped"],
        }

        headers = {}
        if internal_secret:
            headers["X-Internal-Secret"] = internal_secret
            url = f"{control_plane_url}/internal/runs/{self.run_id}/results"
        else:
            if api_token:
                headers["Authorization"] = f"Bearer {api_token}"
            url = f"{control_plane_url}/runs/{self.run_id}"

        try:
            response = httpx.put(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            print(f"Posted results to Control Plane: {status}")
        except Exception as e:
            print(f"Failed to post results: {e}", file=sys.stderr)

    def post_error(self, error_message: str):
        """Post error to Control Plane API."""
        control_plane_url = os.getenv("CONTROL_PLANE_API_URL", "http://control-plane:8000/api/v1").rstrip("/")
        api_token = os.getenv("API_TOKEN")
        internal_secret = os.getenv("INTERNAL_API_SECRET")

        payload = {"status": "failed"}
        headers = {}
        if internal_secret:
            headers["X-Internal-Secret"] = internal_secret
            url = f"{control_plane_url}/internal/runs/{self.run_id}/results"
        else:
            if api_token:
                headers["Authorization"] = f"Bearer {api_token}"
            url = f"{control_plane_url}/runs/{self.run_id}"

        try:
            httpx.put(url, json=payload, headers=headers, timeout=30.0)
        except Exception:
            pass  # Best effort

    def cleanup(self):
        """Clean up workspace."""
        if self.workspace.exists():
            shutil.rmtree(self.workspace)
            print("Cleaned up workspace")


if __name__ == "__main__":
    main()
