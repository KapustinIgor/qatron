"""Example step definitions for pytest-bdd."""
from pytest_bdd import given, when, then, parsers
from qatron.page_object import BasePage
from selenium.webdriver.common.by import By


@given("I am on the home page")
def i_am_on_home_page(driver, environment):
    """Navigate to home page."""
    base_url = environment.get("base_url", "http://localhost:3000")
    driver.get(base_url)
    # Wait for page to load
    import time
    time.sleep(2)  # Simple wait - in production use WebDriverWait


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


@given("I am logged in")
def i_am_logged_in(driver, environment, api_client):
    """Log in via API and set session."""
    # This is a placeholder - implement actual login logic
    pass


@when(parsers.parse("I navigate to {page_name}"))
def i_navigate_to_page(driver, page_name, environment):
    """Navigate to a specific page."""
    base_url = environment.get("base_url")
    driver.get(f"{base_url}/{page_name}")


@then("I should see my profile")
def i_should_see_profile(driver):
    """Verify profile is displayed."""
    page = BasePage(driver)
    assert page.is_displayed((By.ID, "profile")), "Profile not displayed"
