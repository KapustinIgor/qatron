"""Authentication commands."""
import click
from rich.console import Console
from rich.prompt import Prompt

from qatron_cli.api_client import APIClient
from qatron_cli.config import config

console = Console()


@click.group()
def auth_group():
    """Authentication commands."""
    pass


@auth_group.command()
@click.option("--url", help="QAtron API URL", default=None)
@click.option("--username", help="Username", default=None)
@click.option("--password", help="Password", default=None, hide_input=True)
def login(url: str, username: str, password: str):
    """Login to QAtron and save credentials."""
    api_url = url or config.get_api_url()
    username = username or Prompt.ask("Username")
    password = password or Prompt.ask("Password", password=True)

    try:
        # Login via API
        client = APIClient(api_url=api_url)
        response = client.post(
            "/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_data = response.json()
        token = token_data.get("access_token")

        if token:
            # Save configuration
            config.set_api_url(api_url)
            config.set_token(token)
            console.print("[green]✓[/green] Successfully logged in")
        else:
            console.print("[red]✗[/red] Login failed: No token received")
    except Exception as e:
        console.print(f"[red]✗[/red] Login failed: {e}")


@auth_group.command()
def logout():
    """Logout and clear saved credentials."""
    config.set_token("")
    console.print("[green]✓[/green] Logged out")


@auth_group.command()
def status():
    """Check authentication status."""
    api_url = config.get_api_url()
    token = config.get_token()

    console.print(f"API URL: {api_url}")
    console.print(f"Token: {'[green]Set[/green]' if token else '[red]Not set[/red]'}")

    if token:
        try:
            client = APIClient()
            response = client.get("/projects")
            console.print("[green]✓[/green] Authentication valid")
        except Exception as e:
            console.print(f"[red]✗[/red] Authentication failed: {e}")
