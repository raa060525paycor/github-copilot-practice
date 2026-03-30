"""
Pytest configuration and fixtures for FastAPI tests.
"""
import pytest
from copy import deepcopy
from fastapi.testclient import TestClient


# Store the original activities data before tests modify it
_ORIGINAL_ACTIVITIES = None


@pytest.fixture(scope="session", autouse=True)
def _store_original_activities():
    """Store the original activities data once at the start of the test session."""
    global _ORIGINAL_ACTIVITIES
    from src.app import activities
    _ORIGINAL_ACTIVITIES = deepcopy(activities)
    yield


@pytest.fixture
def fresh_activities():
    """
    Reset activities data before each test to ensure test isolation.
    Each test starts with a fresh copy of the original activities.
    """
    import src.app
    
    # Reset activities to original state
    src.app.activities.clear()
    src.app.activities.update(deepcopy(_ORIGINAL_ACTIVITIES))
    
    yield src.app.activities
    
    # Cleanup: restore original activities after test
    src.app.activities.clear()
    src.app.activities.update(deepcopy(_ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """Provide a TestClient instance for testing the FastAPI app."""
    from src.app import app
    return TestClient(app)
