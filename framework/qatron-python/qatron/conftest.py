"""pytest configuration and fixtures."""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from qatron.config import load_config


@pytest.fixture(scope="session")
def qatron_config():
    """Load QAtron configuration."""
    return load_config()


@pytest.fixture(scope="session")
def environment(qatron_config):
    """Get current environment from environment variable."""
    env_name = os.getenv("ENVIRONMENT", "default")
    return qatron_config.get_environment(env_name)


@pytest.fixture(scope="function")
def driver():
    """Create WebDriver instance."""
    browser = os.getenv("BROWSER", "chrome").lower()
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    selenium_grid_url = os.getenv("SELENIUM_GRID_URL", "http://selenium-hub:4444/wd/hub")

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Remote(command_executor=selenium_grid_url, options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Remote(command_executor=selenium_grid_url, options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    yield driver

    driver.quit()


@pytest.fixture
def api_client(environment):
    """Create API client for the current environment."""
    from qatron.api_client import APIClient

    api_url = environment.get("api_url")
    if not api_url:
        pytest.skip("API URL not configured for environment")
    return APIClient(api_url)
