"""Project initialization commands."""
import os
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.prompt import Prompt

console = Console()


@click.group()
def init_group():
    """Project initialization commands."""
    pass


@init_group.command()
@click.argument("project_name")
def init(project_name: str):
    """Initialize a new QAtron project."""
    project_path = Path(project_name)
    
    if project_path.exists():
        console.print(f"[red]✗[/red] Directory {project_name} already exists")
        return

    console.print(f"[yellow]Creating project: {project_name}[/yellow]")
    project_path.mkdir(parents=True)

    # Create directory structure
    (project_path / "features").mkdir()
    (project_path / "steps").mkdir()
    (project_path / "pages").mkdir()
    (project_path / "api").mkdir()
    (project_path / "tests").mkdir()
    (project_path / "tests" / "unit").mkdir()
    (project_path / "tests" / "contract").mkdir()
    (project_path / "tests" / "integration").mkdir()
    (project_path / "tests" / "e2e").mkdir()
    (project_path / "data").mkdir()

    # Create qatron.yml
    qatron_config = {
        "environments": {
            "local": {
                "base_url": "http://localhost:3000",
                "api_url": "http://localhost:8000/api/v1",
                "dataset": "local-dataset",
            },
            "staging": {
                "base_url": "https://staging.example.com",
                "api_url": "https://api-staging.example.com/v1",
                "dataset": "staging-dataset",
            },
        },
        "suites": {
            "smoke": {
                "layer": "e2e",
                "tags": ["smoke", "critical"],
                "shards": 1,
                "retries": 0,
                "timeout": 600,
            },
            "regression": {
                "layer": "e2e",
                "tags": ["regression"],
                "shards": 4,
                "retries": 1,
                "timeout": 3600,
            },
        },
        "coverage": {
            "thresholds": {
                "unit": 80.0,
                "contract": 70.0,
                "integration": 60.0,
                "e2e": 50.0,
            }
        },
    }

    with open(project_path / "qatron.yml", "w") as f:
        yaml.dump(qatron_config, f, default_flow_style=False)

    # Create example feature file
    feature_content = """Feature: Sample feature
  As a QA engineer
  I want to verify basic functionality
  So that I can ensure the system works

  Scenario: Basic functionality test
    Given I am on the home page
    When I click the login button
    Then I should see the login form
"""
    with open(project_path / "features" / "sample.feature", "w") as f:
        f.write(feature_content)

    # Create example steps file
    steps_content = '''"""Example step definitions."""
from pytest_bdd import given, when, then
from qatron.page_object import BasePage
from selenium.webdriver.common.by import By


@given("I am on the home page")
def i_am_on_home_page(driver, environment):
    """Navigate to home page."""
    base_url = environment.get("base_url", "http://localhost:3000")
    driver.get(base_url)


@when("I click the login button")
def i_click_login_button(driver):
    """Click login button."""
    page = BasePage(driver)
    page.click((By.ID, "login-button"))


@then("I should see the login form")
def i_should_see_login_form(driver):
    """Verify login form is displayed."""
    page = BasePage(driver)
    assert page.is_displayed((By.ID, "login-form")), "Login form not displayed"
'''
    with open(project_path / "steps" / "steps.py", "w") as f:
        f.write(steps_content)

    # Create requirements.txt
    requirements_content = """qatron-python
pytest
pytest-bdd
selenium
requests
"""
    with open(project_path / "requirements.txt", "w") as f:
        f.write(requirements_content)

    # Create .gitignore
    gitignore_content = """__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
.venv/
venv/
.env
*.log
allure-results/
allure-report/
"""
    with open(project_path / ".gitignore", "w") as f:
        f.write(gitignore_content)

    # Create README
    readme_content = f"""# {project_name}

QAtron test automation project.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run specific suite
pytest -m suite:smoke
```

## Structure

- `features/` - BDD feature files
- `steps/` - Step definitions
- `pages/` - Page Object Models
- `api/` - API client code
- `tests/` - Test files organized by layer
- `data/` - Test data fixtures
- `qatron.yml` - QAtron configuration
"""
    with open(project_path / "README.md", "w") as f:
        f.write(readme_content)

    console.print(f"[green]✓[/green] Project {project_name} created successfully")
    console.print(f"\nNext steps:")
    console.print(f"  cd {project_name}")
    console.print(f"  pip install -r requirements.txt")
    console.print(f"  qatron run smoke --env local")
