"""Project management commands."""
import click
from rich.console import Console
from rich.table import Table

from qatron_cli.api_client import APIClient

console = Console()


@click.group()
def projects_group():
    """Project management commands."""
    pass


@projects_group.command("list")
def list_projects():
    """List all projects."""
    try:
        client = APIClient()
        response = client.get("/projects")
        projects = response.json()

        if not projects:
            console.print("No projects found")
            return

        table = Table(title="Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Repo URL", style="green")
        table.add_column("Created", style="yellow")

        for project in projects:
            table.add_row(
                str(project.get("id", "")),
                project.get("name", ""),
                project.get("repo_url", ""),
                project.get("created_at", "")[:10] if project.get("created_at") else "",
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list projects: {e}")


@projects_group.command()
@click.argument("project_id", type=int)
def show(project_id: int):
    """Show project details."""
    try:
        client = APIClient()
        response = client.get(f"/projects/{project_id}")
        project = response.json()

        console.print(f"\n[bold]Project: {project.get('name')}[/bold]")
        console.print(f"ID: {project.get('id')}")
        console.print(f"Description: {project.get('description', 'N/A')}")
        console.print(f"Repo URL: {project.get('repo_url')}")
        console.print(f"Auth Method: {project.get('repo_auth_method')}")
        console.print(f"Created: {project.get('created_at')}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to show project: {e}")
