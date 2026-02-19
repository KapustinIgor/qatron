"""QAtron CLI main entry point."""
import click
from rich.console import Console

from qatron_cli.commands import auth, init, projects, runs

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="qatron")
def cli():
    """QAtron - Cloud-agnostic QA automation platform CLI."""
    pass


# Add command groups
cli.add_command(auth.auth_group)
cli.add_command(init.init_group)
cli.add_command(projects.projects_group)
cli.add_command(runs.runs_group)


if __name__ == "__main__":
    cli()
