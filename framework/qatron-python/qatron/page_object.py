"""Base Page Object Model class."""
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from qatron.helpers import wait_for


class BasePage:
    """Base Page Object Model class."""

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """
        Initialize page object.

        Args:
            driver: Selenium WebDriver instance
            timeout: Default timeout for element waits
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def find_element(self, locator: tuple, timeout: Optional[int] = None):
        """Find element with wait."""
        wait_timeout = timeout or self.timeout
        return WebDriverWait(self.driver, wait_timeout).until(
            EC.presence_of_element_located(locator)
        )

    def find_elements(self, locator: tuple, timeout: Optional[int] = None):
        """Find elements with wait."""
        wait_timeout = timeout or self.timeout
        return WebDriverWait(self.driver, wait_timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    def click(self, locator: tuple, timeout: Optional[int] = None):
        """Click element."""
        element = self.find_element(locator, timeout)
        element.click()

    def send_keys(self, locator: tuple, text: str, timeout: Optional[int] = None):
        """Send keys to element."""
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple, timeout: Optional[int] = None) -> str:
        """Get element text."""
        element = self.find_element(locator, timeout)
        return element.text

    def is_displayed(self, locator: tuple, timeout: Optional[int] = None) -> bool:
        """Check if element is displayed."""
        try:
            element = self.find_element(locator, timeout)
            return element.is_displayed()
        except Exception:
            return False
