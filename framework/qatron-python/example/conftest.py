"""pytest configuration - imports QAtron fixtures."""
import sys
from pathlib import Path

# Add parent directory (qatron-python) to Python path so we can import qatron
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import QAtron's conftest to get driver, environment, and other fixtures
pytest_plugins = ["qatron.conftest"]

# Import step definitions so pytest-bdd can find them
# Must import before pytest-bdd collects tests
import steps.steps  # noqa: F401
import steps.amazon_steps  # noqa: F401


def pytest_configure(config):
    """Register markers and ensure step definitions are imported before test collection."""
    config.addinivalue_line("markers", "e2e: E2E tests (run with layer=e2e).")
    config.addinivalue_line("markers", "suite_default: Default suite (platform runs with suite=default).")
    # Import steps to register them with pytest-bdd
    import steps.steps  # noqa: F401
    import steps.amazon_steps  # noqa: F401
