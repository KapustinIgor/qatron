"""Minimal test to verify pytest-bdd step discovery."""
from pytest_bdd import scenario, given, then, parsers

# Define step directly in test file
@given("I am on the home page")
def i_am_on_home_page(driver, environment):
    """Navigate to home page."""
    base_url = environment.get("base_url", "https://www.amazon.com")
    driver.get(base_url)
    # Wait for page to load
    import time
    time.sleep(2)  # Simple wait - in production use WebDriverWait


@then(parsers.parse('the page title should contain "{text}"'))
def page_title_contains(driver, text):
    """Verify page title contains specified text."""
    assert text.lower() in driver.title.lower(), \
        f"Expected '{text}' in title, but got: {driver.title}"


@then("the search box should be visible")
def search_box_visible(driver):
    """Verify Amazon search box is visible."""
    from qatron.page_object import BasePage
    from selenium.webdriver.common.by import By
    page = BasePage(driver)
    search_locator = (By.ID, "twotabsearchtextbox")
    assert page.is_displayed(search_locator, timeout=10), \
        "Amazon search box not visible on page"


@scenario("amazon.feature", "Amazon home page loads and search is visible")
def test_amazon_home_page_loads_and_search_is_visible():
    """Amazon E2E test scenario."""
    pass
