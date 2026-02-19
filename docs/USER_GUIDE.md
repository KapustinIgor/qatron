# QAtron User Guide

Complete guide to using QAtron for QA automation, covering all testing scenarios, integration patterns, and workflows.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Setup](#project-setup)
3. [Writing Tests](#writing-tests)
4. [Running Tests](#running-tests)
5. [CI/CD Integration](#cicd-integration)
6. [Test Data Management](#test-data-management)
7. [Reporting and Analytics](#reporting-and-analytics)
8. [Infrastructure Management](#infrastructure-management)
9. [Advanced Scenarios](#advanced-scenarios)
10. [Troubleshooting](#troubleshooting)
11. [Background Tasks and Cleanup](#background-tasks-and-cleanup)

---

## Getting Started

### First-Time Setup

1. **Install QAtron Platform**
   ```bash
   ./deployment/docker-compose/install.sh
   ```

2. **Install CLI Tool**
   ```bash
   pipx install qatron
   ```

3. **Login to QAtron**
   ```bash
   qatron login --url http://localhost:8000
   # Enter your credentials
   ```

4. **Verify Installation**
   ```bash
   qatron auth status
   # Should show: Authentication valid
   ```

### Access Points

- **QAtron Board (UI)**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Control Plane API**: http://localhost:8000/api/v1
- **Grafana Dashboards**: http://localhost:3001

---

## Project Setup

### Scenario 1: Create New Project via CLI

```bash
# Initialize project
qatron init my-awesome-project
cd my-awesome-project

# Project structure created:
# - features/          # BDD feature files
# - steps/            # Step definitions
# - pages/            # Page Object Models
# - api/              # API client code
# - tests/            # Test files by layer
#   - unit/
#   - contract/
#   - integration/
#   - e2e/
# - data/             # Test data fixtures
# - qatron.yml        # Configuration
```

### Scenario 2: Create Project via API

```bash
# Get authentication token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin" \
  | jq -r '.access_token')

# Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "E-Commerce Platform",
    "description": "Main e-commerce application tests",
    "repo_url": "https://github.com/company/ecommerce-tests",
    "repo_auth_method": "token",
    "organization_id": 1
  }'
```

### Scenario 3: Create Project via UI

1. Open http://localhost:3000
2. Navigate to **Projects** → **New Project**
3. Fill in:
   - Project name
   - Repository URL
   - Authentication method (token/SSH)
   - Description
4. Click **Create**

### Scenario 4: Configure Environments

Edit `qatron.yml`:

```yaml
environments:
  local:
    base_url: http://localhost:3000
    api_url: http://localhost:8000/api/v1
    dataset: local-dataset
    
  dev:
    base_url: https://dev.example.com
    api_url: https://api-dev.example.com/v1
    dataset: dev-dataset
    
  staging:
    base_url: https://staging.example.com
    api_url: https://api-staging.example.com/v1
    dataset: staging-dataset
    
  production:
    base_url: https://example.com
    api_url: https://api.example.com/v1
    dataset: production-dataset
```

### Scenario 5: Configure Test Suites

```yaml
suites:
  smoke:
    layer: e2e
    tags: [smoke, critical]
    shards: 1
    retries: 0
    timeout: 600
    
  regression:
    layer: e2e
    tags: [regression]
    shards: 4
    retries: 1
    timeout: 3600
    
  integration:
    layer: integration
    tags: [integration]
    shards: 2
    retries: 0
    timeout: 1800
    
  contract:
    layer: contract
    tags: [contract, api]
    shards: 1
    retries: 0
    timeout: 300
    
  unit:
    layer: unit
    tags: [unit]
    shards: 1
    retries: 0
    timeout: 60
```

---

## Writing Tests

### BDD Feature Ingestion

QAtron can automatically scan and index BDD feature files from your repository, making them searchable and trackable in the UI.

#### Ingesting Features from Repository

**Via API:**

```bash
# Ingest all .feature files from a repository path
curl -X POST http://localhost:8000/api/v1/features/projects/1/ingest-features \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/test/repository"
  }'

# Response:
# {
#   "message": "Successfully ingested 5 features",
#   "features_count": 5
# }
```

**What Gets Indexed:**
- Feature name, description, tags
- Scenarios (regular and outlines)
- Steps (Given/When/Then/And/But)
- Examples tables (for scenario outlines)
- Data tables (within steps)

#### Viewing Ingested Features

```bash
# List all features for a project
curl http://localhost:8000/api/v1/features/projects/1/features \
  -H "Authorization: Bearer $TOKEN" | jq

# Response includes:
# - Feature metadata (name, file_path, tags, description)
# - Scenarios with their steps
# - Scenario types (scenario vs scenario_outline)
```

**Use Cases:**
- Track feature coverage across projects
- View BDD structure without running tests
- Map test results to features/scenarios
- Identify missing step definitions

### Scenario 1: E2E Test with BDD (Gherkin)

**File: `features/checkout.feature`**

```gherkin
Feature: Shopping Cart Checkout
  As a customer
  I want to complete a purchase
  So that I can receive my order

  @smoke @critical
  Scenario: Successful checkout with valid payment
    Given I am logged in as "testuser@example.com"
    And I have items in my cart
    When I proceed to checkout
    And I enter valid payment details
    And I confirm the order
    Then I should see order confirmation
    And I should receive order confirmation email

  @regression
  Scenario: Checkout with invalid credit card
    Given I am logged in as "testuser@example.com"
    And I have items in my cart
    When I proceed to checkout
    And I enter invalid credit card "1234-5678-9012-3456"
    And I confirm the order
    Then I should see error message "Invalid credit card"
    And my cart should still contain items

  @regression @edge-case
  Scenario Outline: Checkout with different payment methods
    Given I am logged in as "testuser@example.com"
    And I have items in my cart
    When I proceed to checkout
    And I select payment method "<payment_method>"
    And I enter payment details
    And I confirm the order
    Then I should see order confirmation

    Examples:
      | payment_method |
      | Credit Card    |
      | PayPal         |
      | Apple Pay      |
      | Google Pay     |
```

**File: `steps/checkout_steps.py`**

```python
from pytest_bdd import given, when, then, parsers
from qatron.page_object import BasePage
from selenium.webdriver.common.by import By
from qatron.data_fixtures import get_test_data


@given(parsers.parse('I am logged in as "{email}"'))
def i_am_logged_in(driver, environment, email):
    """Login via API and set session cookie."""
    from qatron.api_client import APIClient
    
    api_client = APIClient(environment["api_url"])
    response = api_client.post("/auth/login", json={
        "email": email,
        "password": get_test_data("users.password", environment["name"])
    })
    token = response.json()["token"]
    
    # Set authentication cookie
    driver.add_cookie({"name": "auth_token", "value": token})


@given("I have items in my cart")
def i_have_items_in_cart(driver, environment):
    """Add items to cart."""
    page = BasePage(driver)
    driver.get(f"{environment['base_url']}/products")
    page.click((By.CSS_SELECTOR, ".product-card:first-child .add-to-cart"))
    page.click((By.CSS_SELECTOR, ".product-card:nth-child(2) .add-to-cart"))


@when("I proceed to checkout")
def i_proceed_to_checkout(driver):
    """Navigate to checkout."""
    page = BasePage(driver)
    page.click((By.ID, "cart-icon"))
    page.click((By.ID, "checkout-button"))


@when("I enter valid payment details")
def i_enter_valid_payment(driver):
    """Enter valid payment information."""
    page = BasePage(driver)
    page.send_keys((By.ID, "card-number"), "4111-1111-1111-1111")
    page.send_keys((By.ID, "expiry"), "12/25")
    page.send_keys((By.ID, "cvv"), "123")


@when(parsers.parse('I enter invalid credit card "{card_number}"'))
def i_enter_invalid_card(driver, card_number):
    """Enter invalid credit card."""
    page = BasePage(driver)
    page.send_keys((By.ID, "card-number"), card_number)


@then("I should see order confirmation")
def i_should_see_confirmation(driver):
    """Verify order confirmation page."""
    page = BasePage(driver)
    assert page.is_displayed((By.ID, "order-confirmation"))
    order_id = page.get_text((By.ID, "order-number"))
    assert order_id is not None


@then(parsers.parse('I should see error message "{message}"'))
def i_should_see_error(driver, message):
    """Verify error message."""
    page = BasePage(driver)
    error_text = page.get_text((By.CSS_SELECTOR, ".error-message"))
    assert message in error_text
```

### Scenario 2: API Contract Test

**File: `tests/contract/test_user_api.py`**

```python
import pytest
from qatron.api_client import APIClient


@pytest.mark.contract
@pytest.mark.api
class TestUserAPI:
    """Contract tests for User API."""
    
    def test_get_user_by_id(self, api_client):
        """Test GET /users/{id} contract."""
        response = api_client.get("/users/1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify contract
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)
        assert "@" in data["email"]
    
    def test_create_user_contract(self, api_client):
        """Test POST /users contract."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!"
        }
        
        response = api_client.post("/users", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify contract
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert "created_at" in data
        assert "password" not in data  # Password should not be returned
    
    def test_update_user_contract(self, api_client):
        """Test PUT /users/{id} contract."""
        update_data = {"full_name": "Updated Name"}
        
        response = api_client.put("/users/1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
    
    @pytest.mark.parametrize("invalid_email", [
        "not-an-email",
        "@example.com",
        "user@",
        ""
    ])
    def test_create_user_invalid_email(self, api_client, invalid_email):
        """Test validation contract for invalid emails."""
        response = api_client.post("/users", json={
            "email": invalid_email,
            "username": "test",
            "password": "Pass123!"
        })
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
```

### Scenario 3: Integration Test

**File: `tests/integration/test_order_workflow.py`**

```python
import pytest
from qatron.api_client import APIClient
from qatron.data_fixtures import load_data_fixture


@pytest.mark.integration
class TestOrderWorkflow:
    """Integration tests for order processing workflow."""
    
    def test_complete_order_workflow(self, api_client, environment):
        """Test end-to-end order workflow."""
        # 1. Create user
        user_data = load_data_fixture("test_user", environment["name"])
        user_response = api_client.post("/users", json=user_data)
        user_id = user_response.json()["id"]
        
        # 2. Add products to cart
        products = load_data_fixture("test_products", environment["name"])
        for product in products:
            api_client.post(f"/users/{user_id}/cart", json={"product_id": product["id"]})
        
        # 3. Create order
        order_data = {
            "user_id": user_id,
            "shipping_address": load_data_fixture("test_address", environment["name"])
        }
        order_response = api_client.post("/orders", json=order_data)
        order_id = order_response.json()["id"]
        
        # 4. Process payment
        payment_response = api_client.post(f"/orders/{order_id}/payment", json={
            "payment_method": "credit_card",
            "card_token": "test_token_123"
        })
        assert payment_response.status_code == 200
        
        # 5. Verify order status
        order_status = api_client.get(f"/orders/{order_id}").json()
        assert order_status["status"] == "confirmed"
        
        # 6. Verify inventory updated
        for product in products:
            inventory = api_client.get(f"/products/{product['id']}/inventory").json()
            assert inventory["quantity"] < product["initial_quantity"]
    
    def test_order_with_insufficient_inventory(self, api_client, environment):
        """Test order fails when inventory is insufficient."""
        # Setup: Create order with quantity > available
        order_data = {
            "items": [{
                "product_id": 1,
                "quantity": 1000  # More than available
            }]
        }
        
        response = api_client.post("/orders", json=order_data)
        assert response.status_code == 400
        assert "insufficient inventory" in response.json()["detail"].lower()
```

### Scenario 4: Unit Test

**File: `tests/unit/test_calculator.py`**

```python
import pytest
from app.utils.calculator import Calculator


@pytest.mark.unit
class TestCalculator:
    """Unit tests for Calculator utility."""
    
    def test_add(self):
        """Test addition."""
        calc = Calculator()
        assert calc.add(2, 3) == 5
        assert calc.add(-1, 1) == 0
        assert calc.add(0, 0) == 0
    
    def test_subtract(self):
        """Test subtraction."""
        calc = Calculator()
        assert calc.subtract(5, 3) == 2
        assert calc.subtract(0, 5) == -5
    
    def test_multiply(self):
        """Test multiplication."""
        calc = Calculator()
        assert calc.multiply(3, 4) == 12
        assert calc.multiply(0, 100) == 0
    
    def test_divide(self):
        """Test division."""
        calc = Calculator()
        assert calc.divide(10, 2) == 5
        assert calc.divide(7, 2) == 3.5
    
    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        calc = Calculator()
        with pytest.raises(ValueError):
            calc.divide(10, 0)
```

### Scenario 5: Page Object Model Pattern

**File: `pages/login_page.py`**

```python
from qatron.page_object import BasePage
from selenium.webdriver.common.by import By
from qatron.helpers import wait_for


class LoginPage(BasePage):
    """Page Object for Login page."""
    
    # Locators
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot Password?")
    
    def enter_username(self, username: str):
        """Enter username."""
        self.send_keys(self.USERNAME_INPUT, username)
    
    def enter_password(self, password: str):
        """Enter password."""
        self.send_keys(self.PASSWORD_INPUT, password)
    
    def click_login(self):
        """Click login button."""
        self.click(self.LOGIN_BUTTON)
    
    def login(self, username: str, password: str):
        """Complete login flow."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
    
    def get_error_message(self) -> str:
        """Get error message if present."""
        if self.is_displayed(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def wait_for_page_load(self):
        """Wait for page to load."""
        wait_for(
            lambda: self.is_displayed(self.USERNAME_INPUT),
            timeout=10
        )
```

### Scenario 6: Data-Driven Testing

**File: `data/test_users.json`**

```json
{
  "valid_users": [
    {
      "email": "admin@example.com",
      "password": "Admin123!",
      "role": "admin"
    },
    {
      "email": "user@example.com",
      "password": "User123!",
      "role": "user"
    }
  ],
  "invalid_users": [
    {
      "email": "invalid-email",
      "password": "Pass123!",
      "expected_error": "Invalid email format"
    },
    {
      "email": "user@example.com",
      "password": "short",
      "expected_error": "Password too short"
    }
  ]
}
```

**File: `tests/e2e/test_login_data_driven.py`**

```python
import pytest
from qatron.data_fixtures import load_data_fixture
from pages.login_page import LoginPage


@pytest.mark.e2e
class TestLoginDataDriven:
    """Data-driven login tests."""
    
    @pytest.mark.parametrize("user", [
        {"email": "admin@example.com", "password": "Admin123!"},
        {"email": "user@example.com", "password": "User123!"}
    ])
    def test_valid_login(self, driver, environment, user):
        """Test login with valid credentials."""
        login_page = LoginPage(driver)
        driver.get(f"{environment['base_url']}/login")
        login_page.login(user["email"], user["password"])
        
        # Verify redirect to dashboard
        wait_for(
            lambda: "dashboard" in driver.current_url,
            timeout=5
        )
    
    def test_invalid_login_scenarios(self, driver, environment):
        """Test various invalid login scenarios."""
        invalid_users = load_data_fixture("test_users", environment["name"])["invalid_users"]
        
        for user_data in invalid_users:
            login_page = LoginPage(driver)
            driver.get(f"{environment['base_url']}/login")
            login_page.login(user_data["email"], user_data["password"])
            
            error = login_page.get_error_message()
            assert user_data["expected_error"] in error
```

---

## Running Tests

### Scenario 1: Run Tests Locally via CLI

```bash
# Run smoke suite
qatron run --suite smoke --env staging

# Run regression suite
qatron run --suite regression --env production

# Run with specific branch and commit
qatron run --suite integration --env dev \
  --branch feature/new-api \
  --commit abc123def

# Run failed tests only
qatron run --suite regression --env staging --failed-only
```

### Scenario 2: Run Tests via API

```bash
# Trigger run via API
curl -X POST http://localhost:8000/api/v1/runs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "suite_id": 1,
    "environment_id": 1,
    "branch": "main",
    "commit": "abc123",
    "triggered_by": "manual"
  }'

# Response includes run_id
# Use run_id to check status
```

### Scenario 3: Run Tests via UI

1. Open http://localhost:3000
2. Navigate to **Runs** → **New Run**
3. Select:
   - Project
   - Suite
   - Environment
   - Branch (optional)
   - Commit (optional)
4. Click **Start Run**

### Scenario 4: Run Specific Test Layers

```bash
# Run only unit tests
pytest -m unit

# Run only contract tests
pytest -m contract

# Run only integration tests
pytest -m integration

# Run only e2e tests
pytest -m e2e

# Run multiple layers
pytest -m "unit or contract"
```

### Scenario 5: Run Tests by Tags

```bash
# Run smoke tests
pytest -m smoke

# Run critical tests
pytest -m critical

# Run regression tests
pytest -m regression

# Run tests with multiple tags
pytest -m "smoke and critical"

# Exclude flaky tests
pytest -m "not flaky_candidate"
```

### Scenario 6: Parallel Execution with Sharding

```bash
# Run with 4 shards (configured in qatron.yml)
qatron run --suite regression --env staging
# Automatically splits tests across 4 workers

# Manual sharding
pytest --dist loadgroup -n 4
```

### Scenario 7: Rerun Failed Tests

```bash
# Rerun only failed tests from last run
qatron run --suite regression --env staging --failed-only

# Or via pytest
pytest --lf  # Last failed
pytest --ff  # Failed first, then rest
```

### Scenario 8: Run with Coverage

```bash
# Run with coverage collection
pytest --cov=. --cov-report=html --cov-report=xml

# Check coverage thresholds
pytest --cov=. --cov-fail-under=80
```

---

## CI/CD Integration

### Service Tokens for CI/CD

Service tokens provide long-lived, programmatic access to QAtron APIs without user credentials. They're ideal for CI/CD pipelines.

#### Creating a Service Token

**Via API (Admin only):**

```bash
# Login as admin first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin&password=admin" \
  -H "Content-Type: application/x-www-form-urlencoded" | jq -r '.access_token')

# Create service token (save the token immediately - shown only once!)
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/service-tokens \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub Actions CI",
    "description": "Service token for GitHub Actions workflows",
    "organization_id": 1,
    "project_id": null,
    "expires_at": null
  }')

SERVICE_TOKEN=$(echo $RESPONSE | jq -r '.token')
echo "Service Token: $SERVICE_TOKEN"
# Store this token securely in your CI/CD secrets!
```

**Token Properties:**
- **Scoped**: Can be organization-wide (`project_id: null`) or project-specific
- **Expiration**: Optional expiry date (`expires_at: null` = no expiry)
- **Revocable**: Can be revoked via API or UI
- **Audited**: All token usage is logged in audit logs

#### Using Service Tokens in CI/CD

Replace `QATRON_API_TOKEN` in your CI/CD workflows with the service token:

```yaml
# GitHub Actions example
env:
  QATRON_API_URL: https://qatron.example.com/api/v1
  QATRON_SERVICE_TOKEN: ${{ secrets.QATRON_SERVICE_TOKEN }}  # Use service token, not user token
```

#### Managing Service Tokens

```bash
# List all service tokens
curl http://localhost:8000/api/v1/auth/service-tokens \
  -H "Authorization: Bearer $TOKEN" | jq

# Revoke a service token
curl -X DELETE http://localhost:8000/api/v1/auth/service-tokens/{token_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 1: GitHub Actions Integration

**File: `.github/workflows/qatron-tests.yml`**

```yaml
name: QAtron Test Execution

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Trigger QAtron Smoke Tests
        run: |
          RESPONSE=$(curl -X POST ${{ secrets.QATRON_API_URL }}/runs \
            -H "Authorization: Bearer ${{ secrets.QATRON_SERVICE_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "project_id": ${{ secrets.QATRON_PROJECT_ID }},
              "suite_id": 1,
              "environment_id": 1,
              "branch": "${{ github.ref_name }}",
              "commit": "${{ github.sha }}",
              "triggered_by": "github-actions"
            }')
          
          RUN_ID=$(echo $RESPONSE | jq -r '.id')
          echo "RUN_ID=$RUN_ID" >> $GITHUB_ENV
      
      - name: Wait for Run Completion
        run: |
          while true; do
            STATUS=$(curl -s -H "Authorization: Bearer ${{ secrets.QATRON_SERVICE_TOKEN }}" \
              ${{ secrets.QATRON_API_URL }}/runs/$RUN_ID | jq -r '.status')
            
            if [ "$STATUS" = "completed" ]; then
              echo "Tests passed!"
              exit 0
            elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "partial_failed" ] || [ "$STATUS" = "infra_failed" ] || [ "$STATUS" = "timed_out" ]; then
              echo "Tests failed with status: $STATUS"
              exit 1
            fi
            
            sleep 10
          done
      
      - name: Download Artifacts
        if: always()
        run: |
          qatron runs artifacts $RUN_ID --output ./artifacts
      
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: ./artifacts
```

### Scenario 2: GitLab CI Integration

**File: `.gitlab-ci.yml`**

```yaml
stages:
  - test

variables:
  QATRON_API_URL: "https://qatron.example.com/api/v1"
  QATRON_PROJECT_ID: "1"

smoke-tests:
  stage: test
  script:
    - |
      RESPONSE=$(curl -X POST ${QATRON_API_URL}/runs \
        -H "Authorization: Bearer ${QATRON_SERVICE_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
          \"project_id\": ${QATRON_PROJECT_ID},
          \"suite_id\": 1,
          \"environment_id\": 1,
          \"branch\": \"${CI_COMMIT_REF_NAME}\",
          \"commit\": \"${CI_COMMIT_SHA}\",
          \"triggered_by\": \"gitlab-ci\"
        }")
      
      RUN_ID=$(echo $RESPONSE | jq -r '.id')
      
      # Poll for completion
      while true; do
        STATUS=$(curl -s -H "Authorization: Bearer ${QATRON_SERVICE_TOKEN}" \
          ${QATRON_API_URL}/runs/${RUN_ID} | jq -r '.status')
        
        if [ "$STATUS" = "completed" ]; then
          exit 0
        elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "partial_failed" ] || [ "$STATUS" = "infra_failed" ] || [ "$STATUS" = "timed_out" ]; then
          exit 1
        fi
        
        sleep 10
      done
  only:
    - main
    - develop
    - merge_requests
```

### Scenario 3: Jenkins Pipeline Integration

**File: `Jenkinsfile`**

```groovy
pipeline {
    agent any
    
    environment {
        QATRON_API_URL = 'https://qatron.example.com/api/v1'
        QATRON_API_TOKEN = credentials('qatron-api-token')
        QATRON_PROJECT_ID = '1'
    }
    
    stages {
        stage('Trigger QAtron Tests') {
            steps {
                script {
                    def response = httpRequest(
                        httpMode: 'POST',
                        url: "${env.QATRON_API_URL}/runs",
                        customHeaders: [
                            [name: 'Authorization', value: "Bearer ${env.QATRON_API_TOKEN}"],
                            [name: 'Content-Type', value: 'application/json']
                        ],
                        requestBody: """
                        {
                            "project_id": ${env.QATRON_PROJECT_ID},
                            "suite_id": 1,
                            "environment_id": 1,
                            "branch": "${env.GIT_BRANCH}",
                            "commit": "${env.GIT_COMMIT}",
                            "triggered_by": "jenkins"
                        }
                        """
                    )
                    
                    def runData = readJSON text: response.content
                    env.RUN_ID = runData.id
                }
            }
        }
        
        stage('Wait for Test Completion') {
            steps {
                script {
                    def status = 'running'
                    while (status != 'completed' && status != 'failed') {
                        sleep(time: 10, unit: 'SECONDS')
                        def statusResponse = httpRequest(
                            httpMode: 'GET',
                            url: "${env.QATRON_API_URL}/runs/${env.RUN_ID}",
                            customHeaders: [[name: 'Authorization', value: "Bearer ${env.QATRON_API_TOKEN}"]]
                        )
                        def runStatus = readJSON text: statusResponse.content
                        status = runStatus.status
                        echo "Run status: ${status}"
                    }
                    
                    if (status == 'failed') {
                        error("QAtron tests failed!")
                    }
                }
            }
        }
        
        stage('Download Artifacts') {
            steps {
                sh 'qatron runs artifacts ${RUN_ID} --output ./artifacts'
                archiveArtifacts artifacts: 'artifacts/**', fingerprint: true
            }
        }
    }
}
```

### Scenario 4: CircleCI Integration

**File: `.circleci/config.yml`**

```yaml
version: 2.1

jobs:
  qatron-tests:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install QAtron CLI
          command: pip install qatron
      - run:
          name: Trigger Tests
          command: |
            qatron login --url $QATRON_API_URL
            RUN_ID=$(qatron run --suite smoke --env staging --branch $CIRCLE_BRANCH --commit $CIRCLE_SHA | jq -r '.id')
            echo "export RUN_ID=$RUN_ID" >> $BASH_ENV
      - run:
          name: Wait for Completion
          command: |
            while true; do
              STATUS=$(qatron runs status $RUN_ID | jq -r '.status')
              if [ "$STATUS" = "completed" ]; then
                exit 0
              elif [ "$STATUS" = "failed" ]; then
                exit 1
              fi
              sleep 10
            done
      - run:
          name: Download Artifacts
          command: qatron runs artifacts $RUN_ID --output ./artifacts
      - store_artifacts:
          path: ./artifacts

workflows:
  version: 2
  test:
    jobs:
      - qatron-tests
```

### Scenario 5: Azure DevOps Integration

**File: `azure-pipelines.yml`**

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'
  
  - script: |
      pip install qatron
    displayName: 'Install QAtron CLI'
  
  - script: |
      qatron login --url $(QATRON_API_URL)
      RUN_ID=$(qatron run --suite smoke --env staging \
        --branch $(Build.SourceBranchName) \
        --commit $(Build.SourceVersion) | jq -r '.id')
      echo "##vso[task.setvariable variable=RUN_ID]$RUN_ID"
    displayName: 'Trigger QAtron Tests'
  
  - script: |
      while true; do
        STATUS=$(qatron runs status $(RUN_ID) | jq -r '.status')
        echo "Run status: $STATUS"
        
        if [ "$STATUS" = "completed" ]; then
          exit 0
        elif [ "$STATUS" = "failed" ]; then
          exit 1
        fi
        
        sleep 10
      done
    displayName: 'Wait for Test Completion'
  
  - script: |
      qatron runs artifacts $(RUN_ID) --output ./artifacts
    displayName: 'Download Artifacts'
    condition: always()
  
  - task: PublishTestResults@2
    inputs:
      testResultsFormat: 'JUnit'
      testResultsFiles: 'artifacts/junit.xml'
    condition: always()
```

### Scenario 6: Webhook-Based CI Integration

**Setup webhook in QAtron:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-ci.com/webhook/qatron",
    "events": ["run.completed", "run.failed"],
    "secret": "webhook-secret-123"
  }'
```

**CI receives webhook:**

```python
# Flask example
@app.route('/webhook/qatron', methods=['POST'])
def qatron_webhook():
    signature = request.headers.get('X-QAtron-Signature')
    # Verify signature
    
    data = request.json
    run_id = data['run_id']
    status = data['status']
    
    if status == 'failed':
        # Fail CI pipeline
        sys.exit(1)
    
    return 'OK'
```

### Scenario 7: Conditional Test Execution

```yaml
# In CI, run different suites based on changes
# .github/workflows/smart-tests.yml

name: Smart Test Execution

on:
  pull_request:
    paths:
      - 'frontend/**'
      - 'backend/**'
      - 'api/**'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.changes.outputs.frontend }}
      backend: ${{ steps.changes.outputs.backend }}
      api: ${{ steps.changes.outputs.api }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            frontend:
              - 'frontend/**'
            backend:
              - 'backend/**'
            api:
              - 'api/**'
  
  run-frontend-tests:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: |
          qatron run --suite e2e --env staging --tags frontend
  
  run-backend-tests:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: |
          qatron run --suite integration --env staging --tags backend
  
  run-api-tests:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: |
          qatron run --suite contract --env staging --tags api
```

---

## Test Data Management

### Scenario 1: Register Dataset

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/datasets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "user-dataset",
    "description": "Test user data",
    "dataset_type": "database",
    "refresh_mechanism": "manual",
    "validation_rules_ref": "s3://rules/user-validation.json"
  }'
```

### Scenario 2: Validate Dataset Before Run

**Via Configuration (qatron.yml):**

```yaml
# In qatron.yml
suites:
  regression:
    layer: e2e
    require_dataset_health: true  # Block run if dataset unhealthy
    dataset: staging-dataset
```

**Via API:**

When a suite has `require_dataset_health: true` and the environment has a dataset assigned, QAtron validates the dataset before starting a run. If validation fails, run creation returns 400 with validation details.

```bash
# Update suite to require dataset validation (when API supports it)
curl -X PUT http://localhost:8000/api/v1/suites/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"require_dataset_health": true}'
```

**How It Works:**
1. Suite has `require_dataset_health: true`
2. Environment has a dataset assigned
3. On run creation, QAtron validates the dataset (e.g. via Great Expectations)
4. If validation fails, run creation is blocked with error details
5. If validation passes, run proceeds normally

### Scenario 3: Automated Dataset Refresh

```bash
# Trigger dataset refresh
curl -X POST http://localhost:8000/api/v1/datasets/1/refresh \
  -H "Authorization: Bearer $TOKEN"

# Check dataset health
curl http://localhost:8000/api/v1/datasets/1/health \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 4: Environment-Specific Data

```python
# Load environment-specific test data
from qatron.data_fixtures import load_data_fixture

def test_with_env_data(environment):
    """Test using environment-specific data."""
    users = load_data_fixture("test_users", environment["name"])
    # Use users specific to current environment
```

---

## Reporting and Analytics

### Scenario 1: View Run Results in UI

1. Open http://localhost:3000
2. Navigate to **Runs**
3. Click on a run to see:
   - BDD hierarchy (Features → Scenarios → Steps)
   - Step attachments (screenshots, logs)
   - Error classification
   - Coverage summary
   - Dataset information
   - **Run status** (see expanded statuses below)
   - **Shard results** (individual shard performance)
   - **Coverage data** in run_metadata

#### Run Status Values

QAtron supports expanded run statuses for orchestration visibility:

| Status | Description |
|--------|-------------|
| `queued` | Run is queued, waiting for execution |
| `provisioning` | Infrastructure is being provisioned |
| `running` | Tests are executing |
| `reporting` | Generating reports and aggregating results |
| `completed` | All tests passed |
| `failed` | Tests failed |
| `partial_failed` | Some shards failed, others passed |
| `timed_out` | Run exceeded timeout |
| `infra_failed` | Infrastructure failure (worker crash, Selenium Grid down) |
| `cancelled` | Run was cancelled by user |

#### Shard Tracking

For parallel runs with sharding, view individual shard results in `run_metadata.shards`:

```bash
# Get run with shard metadata
curl http://localhost:8000/api/v1/runs/123 \
  -H "Authorization: Bearer $TOKEN" | jq '.run_metadata.shards'

# Example response:
# {
#   "1": {"status": "completed", "passed": 10, "failed": 2, "duration": 120},
#   "2": {"status": "completed", "passed": 8, "failed": 1, "duration": 115}
# }
```

#### Coverage Data

Coverage is stored in `run_metadata.coverage`:

```bash
curl http://localhost:8000/api/v1/runs/123 \
  -H "Authorization: Bearer $TOKEN" | jq '.run_metadata.coverage'

# Example: { "total": 85.5, "files": { "src/app.py": 90.2 } }
```

### Scenario 2: Generate Allure Report

```bash
# Via API
curl -X POST http://localhost:8002/api/v1/reports/123/generate \
  -H "Authorization: Bearer $TOKEN"

# Get report URL
curl http://localhost:8002/api/v1/reports/123/allure \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 3: View Metrics

```bash
# Get run metrics
curl http://localhost:8002/api/v1/metrics/runs?project_id=1&days=30 \
  -H "Authorization: Bearer $TOKEN"

# Get flakiness scores
curl http://localhost:8002/api/v1/metrics/flakiness \
  -H "Authorization: Bearer $TOKEN"

# Get coverage metrics
curl http://localhost:8002/api/v1/metrics/coverage/123 \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 4: Download Artifacts

```bash
# Via CLI
qatron runs artifacts 123 --output ./artifacts

# Via API
curl http://localhost:8000/api/v1/runs/123/artifacts \
  -H "Authorization: Bearer $TOKEN" \
  -o artifacts.zip
```

---

## Infrastructure Management

### Scenario 1: Monitor Infrastructure

1. Open http://localhost:3000
2. Navigate to **Infrastructure**
3. View:
   - Queue depth
   - Worker status (ready/busy)
   - Job throughput
   - Selenium Grid status

### Scenario 2: Scale Workers

```bash
# Via Kubernetes
kubectl scale deployment qatron-worker --replicas=10 -n qatron-system

# Check status
kubectl get pods -n qatron-system | grep worker
```

### Scenario 3: Monitor Queue

```bash
# Check RabbitMQ queue depth
docker compose exec rabbitmq rabbitmqctl list_queues

# Via API
curl http://localhost:8000/api/v1/infrastructure/queues \
  -H "Authorization: Bearer $TOKEN"
```

---

## Advanced Scenarios

### Audit Logging

QAtron maintains an audit log of important actions for security and compliance.

**Audited Actions:**
- `user.login` — User authentication
- `run.triggered` — Test run creation
- `project.created`, `project.updated`, `project.deleted`
- `service_token.created`, `service_token.revoked`
- `secret.updated`, `role.assigned`

**Audit Log Fields:** action, user_id, resource_type, resource_id, details (JSON), ip_address, user_agent, created_at

**Querying Audit Logs (database):**

```sql
-- Recent audit logs
SELECT action, user_id, resource_type, resource_id, created_at
FROM audit_logs ORDER BY created_at DESC LIMIT 100;

-- Run triggers by user
SELECT * FROM audit_logs WHERE action = 'run.triggered' AND user_id = 1;
```

When the audit-logs API is available, use: `GET /api/v1/audit-logs?user_id=1&action=run.triggered&limit=50`

### Scenario 1: Multi-Environment Testing

```bash
# Run same suite across multiple environments
for env in dev staging production; do
  qatron run --suite smoke --env $env
done
```

### Scenario 2: Parallel Suite Execution

```bash
# Run multiple suites in parallel
qatron run --suite smoke --env staging &
qatron run --suite integration --env staging &
qatron run --suite contract --env staging &
wait
```

### Scenario 3: Test Selection by Feature

```bash
# Run tests for specific feature
pytest features/checkout.feature

# Run tests for multiple features
pytest features/checkout.feature features/payment.feature
```

### Scenario 4: Custom Test Execution

```python
# Custom pytest execution
import pytest

# Run with custom markers
pytest.main([
    "-m", "smoke and not flaky",
    "--env", "staging",
    "--alluredir", "allure-results"
])
```

### Scenario 5: Retry Flaky Tests

```yaml
# In qatron.yml
suites:
  regression:
    retries: 2
    retry_on: [flaky_candidate, infrastructure_error]
```

### Scenario 6: Coverage Enforcement

```yaml
# In qatron.yml
coverage:
  thresholds:
    unit: 90.0
    contract: 80.0
    integration: 70.0
    e2e: 60.0
  fail_below_threshold: true
```

---

## Troubleshooting

### Scenario 1: Run Failed - Check Logs

```bash
# View run logs
qatron runs logs 123

# View worker logs
docker compose logs worker

# View orchestrator logs
docker compose logs orchestrator
```

### Scenario 2: Test Timeout

```yaml
# Increase timeout in qatron.yml
suites:
  slow-suite:
    timeout: 7200  # 2 hours
```

### Scenario 3: Worker Not Available

```bash
# Check worker status
curl http://localhost:8000/api/v1/infrastructure/workers \
  -H "Authorization: Bearer $TOKEN"

# Scale workers
kubectl scale deployment qatron-worker --replicas=5
```

### Scenario 4: Database Connection Issues

```bash
# Test database connection
docker compose exec postgres psql -U qatron -d qatron -c "SELECT 1;"

# Check migrations
docker compose exec control-plane alembic current
```

### Scenario 5: Runs stuck in QUEUED after Trigger

**Symptom:** You click **Trigger run** but runs stay in **QUEUED** (Tests: 0/0, Duration: N/A). They never move to Running or Completed/Failed.

**Cause:** The run is only updated when the **orchestrator-worker** (Celery) runs the job and the **worker** service executes it. If either is not running, nothing updates the run.

**Fix:**

1. **Start the full stack** so both the Celery worker and the job runner are up:
   ```bash
   cd deployment/docker-compose
   docker compose up -d orchestrator orchestrator-worker worker control-plane postgres redis rabbitmq minio selenium-hub selenium-node
   ```
   (Or use your install script that starts all services.)

2. **Check that orchestrator-worker is running** (it runs the trigger and dispatches to the worker):
   ```bash
   docker compose ps orchestrator-worker
   docker compose logs orchestrator-worker --tail 50
   ```

3. **Check that the worker service is running** (it clones the repo and runs pytest):
   ```bash
   docker compose ps worker
   docker compose logs worker --tail 50
   curl -s http://localhost:8004/healthz
   ```
   If the worker is not in your compose file, add the `worker` service and set `WORKER_URL=http://worker:8004` for `orchestrator-worker`.

4. After starting these services, click **Trigger run** again. The run should move to **Running** and then **Completed** or **Failed** once the worker finishes.

### Scenario 6: Trigger Run doesn't create Selenium Grid sessions

**Symptom:** You click **Trigger run** in the UI and see "Run triggered", but Selenium Grid shows no running or queued sessions (queue size 0).

**Checks:**

1. **Worker and Selenium Grid must be running** — Start the full stack (including `worker`, `selenium-hub`, `selenium-node`). The worker service receives jobs from the orchestrator, clones the project repo, runs pytest, and uses `SELENIUM_GRID_URL` (e.g. `http://selenium-hub:4444/wd/hub`) for E2E tests.
2. **Project repo URL must be cloneable** — The worker clones the repository; use a valid Git URL (e.g. a public GitHub repo). If the project's repo URL is a placeholder or unreachable, the job will fail after trigger.
3. **Run E2E tests locally** — To see sessions on the grid without the platform, run your test project locally with the grid URL:
   ```bash
   export SELENIUM_GRID_URL=http://localhost:4444/wd/hub
   pytest
   ```
   Open Selenium Grid at `http://localhost:4444` to see active sessions.

---

## Background Tasks and Cleanup

QAtron runs automated cleanup tasks when Celery workers are configured.

**Artifact Cleanup**
- **Schedule:** Daily at 03:00 UTC
- **Retention:** Configurable via `CELERY_ARTIFACT_RETENTION_DAYS` (default: 30)
- **Action:** Removes artifacts from completed/failed/cancelled runs older than retention

**Expired Token Cleanup**
- **Schedule:** Daily at 04:00 UTC
- **Action:** Deactivates service tokens that have passed their expiration date

**Configuration (docker-compose or .env):**
```yaml
CELERY_ARTIFACT_RETENTION_DAYS: 30
CELERY_BROKER_URL: redis://redis:6379/1
CELERY_RESULT_BACKEND: redis://redis:6379/2
```

**Manual trigger (when Celery is running):**
```bash
cd services/control-plane
poetry run celery -A app.celery_app call cleanup_artifacts --kwargs '{"retention_days": 30}'
poetry run celery -A app.celery_app call cleanup_expired_tokens
```

---

This guide covers all major testing and integration scenarios. For specific use cases, refer to the API documentation at http://localhost:8000/docs.
