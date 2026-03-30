"""
Tests for the GET /activities endpoint.
"""
import pytest


def test_get_activities_returns_all_activities(client, fresh_activities):
    """Test that /activities returns all activities."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return all 9 activities
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert "Basketball Team" in data
    assert "Tennis Club" in data
    assert "Drama Club" in data
    assert "Art Studio" in data
    assert "Science Olympiad" in data
    assert "Debate Team" in data


def test_get_activities_has_correct_structure(client, fresh_activities):
    """Test that each activity has the expected fields."""
    response = client.get("/activities")
    data = response.json()
    
    # Check that each activity has required fields
    for activity_name, activity_info in data.items():
        assert isinstance(activity_name, str)
        assert isinstance(activity_info, dict)
        
        # Verify required fields exist
        assert "description" in activity_info
        assert "schedule" in activity_info
        assert "max_participants" in activity_info
        assert "participants" in activity_info
        
        # Verify types
        assert isinstance(activity_info["description"], str)
        assert isinstance(activity_info["schedule"], str)
        assert isinstance(activity_info["max_participants"], int)
        assert isinstance(activity_info["participants"], list)
        
        # Verify participants are strings (emails)
        for participant in activity_info["participants"]:
            assert isinstance(participant, str)


def test_get_activities_returns_non_empty_list(client, fresh_activities):
    """Test that /activities returns a non-empty list of activities."""
    response = client.get("/activities")
    data = response.json()
    
    assert len(data) > 0


def test_get_activities_success_status(client, fresh_activities):
    """Test that /activities returns a successful status code."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
