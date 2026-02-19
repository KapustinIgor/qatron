"""Run management commands."""
import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from qatron_cli.api_client import APIClient

console = Console()


@click.group()
def runs_group():
    """Run management commands."""
    pass


@runs_group.command()
@click.option("--suite", required=True, help="Test suite name")
@click.option("--env", required=True, help="Environment name")
@click.option("--project", type=int, help="Project ID")
@click.option("--branch", help="Git branch")
@click.option("--commit", help="Git commit SHA")
def run(suite: str, env: str, project: int, branch: str, commit: str):
    """Trigger a test run."""
    try:
        # Load qatron.yml to get project and suite info
        config_path = Path("qatron.yml")
        if not config_path.exists():
            console.print("[red]✗[/red] qatron.yml not found. Run 'qatron init' first.")
            return

        import yaml
        with open(config_path) as f:
            qatron_config = yaml.safe_load(f)

        # Get suite configuration
        suites = qatron_config.get("suites", {})
        suite_config = suites.get(suite)
        if not suite_config:
            console.print(f"[red]✗[/red] Suite '{suite}' not found in qatron.yml")
            return

        # Get environment
        environments = qatron_config.get("environments", {})
        env_config = environments.get(env)
        if not env_config:
            console.print(f"[red]✗[/red] Environment '{env}' not found in qatron.yml")
            return

        # TODO: Get project ID from config or API
        if not project:
            console.print("[yellow]⚠[/yellow] Project ID not specified. Using default.")
            project = 1  # Default for now

        # Create run
        client = APIClient()
        run_data = {
            "project_id": project,
            "suite_id": 1,  # TODO: Get from API or config
            "environment_id": 1,  # TODO: Get from API or config
            "branch": branch or "main",
            "commit": commit,
            "triggered_by": "cli",
        }

        response = client.post("/runs", json=run_data)
        run = response.json()

        console.print(f"[green]✓[/green] Run created: {run.get('id')}")
        console.print(f"Status: {run.get('status')}")
        console.print(f"View at: {client.api_url.replace('/api/v1', '')}/runs/{run.get('id')}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create run: {e}")


@runs_group.command("list")
@click.option("--project", type=int, help="Filter by project ID")
@click.option("--status", help="Filter by status")
@click.option("--limit", type=int, default=20, help="Limit number of results")
def list_runs(project: int, status: str, limit: int):
    """List test runs."""
    try:
        client = APIClient()
        params = {"limit": limit}
        if project:
            params["project_id"] = project
        if status:
            params["status"] = status

        response = client.get("/runs", params=params)
        runs = response.json()

        if not runs:
            console.print("No runs found")
            return

        table = Table(title="Test Runs")
        table.add_column("ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Project", style="green")
        table.add_column("Branch", style="yellow")
        table.add_column("Created", style="blue")

        for run in runs:
            status_style = {
                "completed": "[green]",
                "failed": "[red]",
                "running": "[yellow]",
                "queued": "[blue]",
            }.get(run.get("status", ""), "")
            table.add_row(
                str(run.get("id", "")),
                f"{status_style}{run.get('status', '')}[/]",
                str(run.get("project_id", "")),
                run.get("branch", ""),
                run.get("created_at", "")[:19] if run.get("created_at") else "",
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list runs: {e}")


@runs_group.command()
@click.argument("run_id", type=int)
def status(run_id: int):
    """Get run status."""
    try:
        client = APIClient()
        response = client.get(f"/runs/{run_id}")
        run = response.json()

        console.print(f"\n[bold]Run #{run_id}[/bold]")
        console.print(f"Status: {run.get('status')}")
        console.print(f"Project: {run.get('project_id')}")
        console.print(f"Suite: {run.get('suite_id')}")
        console.print(f"Environment: {run.get('environment_id')}")
        console.print(f"Branch: {run.get('branch', 'N/A')}")
        console.print(f"Commit: {run.get('commit', 'N/A')}")
        console.print(f"Tests: {run.get('passed_tests', 0)}/{run.get('total_tests', 0)} passed")
        if run.get("duration_seconds"):
            console.print(f"Duration: {run.get('duration_seconds')}s")
        console.print(f"Created: {run.get('created_at')}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get run status: {e}")


@runs_group.command()
@click.argument("run_id", type=int)
@click.option("--output", "-o", help="Output directory", default="artifacts")
def artifacts(run_id: int, output: str):
    """Download run artifacts."""
    try:
        client = APIClient()
        response = client.get(f"/runs/{run_id}")
        run = response.json()

        # TODO: Implement artifact download from S3
        console.print(f"[yellow]⚠[/yellow] Artifact download not yet implemented")
        console.print(f"Run artifacts are available at:")
        console.print(f"  S3: qatron-artifacts/runs/{run_id}/")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to download artifacts: {e}")
