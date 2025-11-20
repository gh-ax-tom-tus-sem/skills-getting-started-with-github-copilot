"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {}
    for name, details in activities.items():
        original_activities[name] = {
            "description": details["description"],
            "schedule": details["schedule"], 
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
    
    yield
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity():
    """Sample activity data for testing"""
    return {
        "name": "Test Activity",
        "description": "A test activity for testing purposes",
        "schedule": "Test Schedule",
        "max_participants": 5,
        "participants": ["test1@mergington.edu", "test2@mergington.edu"]
    }