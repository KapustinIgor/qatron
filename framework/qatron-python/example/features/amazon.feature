Feature: Amazon.com E2E Testing
  As a visitor
  I want to verify Amazon.com loads correctly
  So that I can confirm the site is accessible

  @amazon @smoke
  Scenario: Amazon home page loads and search is visible
    Given I am on the home page
    Then the page title should contain "Amazon"
    And the search box should be visible
