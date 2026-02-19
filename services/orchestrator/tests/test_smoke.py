"""Minimal smoke test so pytest collects at least one test (avoids exit code 5 in CI)."""


def test_smoke() -> None:
    """Placeholder so pytest does not exit with 'no tests collected'."""
    assert True
