"""Amazon.com step definitions for pytest-bdd."""
from pytest_bdd import then, parsers
from qatron.page_object import BasePage
from selenium.webdriver.common.by import By


@then(parsers.parse('the page title should contain "{text}"'))
def page_title_contains(driver, text):
    """Verify page title contains specified text."""
    assert text.lower() in driver.title.lower(), \
        f"Expected '{text}' in title, but got: {driver.title}"


@then("the search box should be visible")
def search_box_visible(driver):
    """Verify Amazon search box is visible."""
    page = BasePage(driver)
    # Amazon's main search input ID (may need adjustment if Amazon changes their HTML)
    search_locator = (By.ID, "twotabsearchtextbox")
    assert page.is_displayed(search_locator, timeout=10), \
        "Amazon search box not visible on page"
