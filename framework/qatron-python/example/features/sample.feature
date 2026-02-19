Feature: Sample feature for QAtron
  As a QA engineer
  I want to verify basic functionality
  So that I can ensure the system works

  Scenario: Basic functionality test
    Given I am on the home page
    When I click the login button
    Then I should see the login form

  @smoke @critical
  Scenario: Critical path test
    Given I am logged in
    When I navigate to the dashboard
    Then I should see my profile
