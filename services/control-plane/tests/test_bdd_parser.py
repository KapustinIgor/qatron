"""Unit tests for app.services.bdd_parser (Gherkin parsing)."""

from app.services.bdd_parser import GherkinParser


SIMPLE_FEATURE = """
Feature: Login

  As a user I can log in so that I use the system.

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    Then I see the dashboard
"""

FEATURE_WITH_TAGS = """
Feature: Search

  @smoke @search
  Scenario: User searches
    Given I am on the home page
    When I search for "pytest"
    Then I see results
"""


def test_parse_feature_content_extracts_name():
    """Parser extracts feature name from Feature: line."""
    result = GherkinParser.parse_feature_content(SIMPLE_FEATURE)
    assert result is not None
    assert result["name"] == "Login"


def test_parse_feature_content_extracts_one_scenario():
    """Parser extracts a single scenario with steps."""
    result = GherkinParser.parse_feature_content(SIMPLE_FEATURE)
    assert result is not None
    assert len(result["scenarios"]) == 1
    scenario = result["scenarios"][0]
    assert scenario["name"] == "Successful login"
    assert len(scenario["steps"]) == 3
    assert scenario["steps"][0]["type"] == "given"
    assert "login page" in scenario["steps"][0]["text"]


def test_parse_feature_content_extracts_tags():
    """Parser extracts tags (before Scenario they go to feature tags)."""
    result = GherkinParser.parse_feature_content(FEATURE_WITH_TAGS)
    assert result is not None
    assert "tags" in result
    assert any("smoke" in t for t in result["tags"])
    assert any("search" in t for t in result["tags"])
    assert len(result["scenarios"]) == 1


def test_parse_feature_content_empty_returns_none():
    """Empty or non-feature content returns None."""
    assert GherkinParser.parse_feature_content("") is None
    assert GherkinParser.parse_feature_content("Not a feature") is None


def test_parse_feature_file_missing_file_returns_none(tmp_path):
    """Parsing a non-existent file path returns None (no exception)."""
    path = tmp_path / "nonexistent.feature"
    assert path.exists() is False
    result = GherkinParser.parse_feature_file(path)
    assert result is None


def test_parse_feature_file_reads_real_file(tmp_path):
    """Parsing a real feature file returns parsed dict."""
    path = tmp_path / "my.feature"
    path.write_text(SIMPLE_FEATURE)
    result = GherkinParser.parse_feature_file(path)
    assert result is not None
    assert result["name"] == "Login"
    assert result["file_path"] == str(path)
