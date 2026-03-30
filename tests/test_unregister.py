"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.
"""
import pytest


def test_unregister_happy_path(client, fresh_activities):
    """Test successful unregistration from an activity."""
    email = "michael@mergington.edu"
    
    # Verify email is in Chess Club before unregister
    activities_before = client.get("/activities").json()
    assert email in activities_before["Chess Club"]["participants"]
    
    # Unregister
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from Chess Club"
    
    # Verify email was removed
    activities_after = client.get("/activities").json()
    assert email not in activities_after["Chess Club"]["participants"]


def test_unregister_activity_not_found(client, fresh_activities):
    """Test unregister from non-existent activity returns 404."""
    response = client.delete(
        "/activities/Fake Activity/unregister",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_student_not_registered(client, fresh_activities):
    """Test unregister for a student not in the activity returns 400."""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_then_signup_again(client, fresh_activities):
    """Test that a student can re-signup after unregistering."""
    email = "flexible@mergington.edu"
    activity = "Programming Class"
    
    # Initial signup
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Verify registered
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]
    
    # Unregister
    response2 = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify unregistered
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
    
    # Re-signup
    response3 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response3.status_code == 200
    
    # Verify re-registered
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_unregister_response_message_format(client, fresh_activities):
    """Test that unregister response message has correct format."""
    email = "daniel@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity}"


def test_unregister_multiple_times_fails_second_attempt(client, fresh_activities):
    """Test that unregistering the same student twice fails on second attempt."""
    email = "isabella@mergington.edu"  # Already in Drama Club
    activity = "Drama Club"
    
    # First unregister should succeed
    response1 = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second unregister should fail
    response2 = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "not registered" in response2.json()["detail"]


def test_unregister_from_different_activities(client, fresh_activities):
    """Test unregistering a student from multiple different activities."""
    email = "sophia@mergington.edu"  # Already in Programming Class and Debate Team
    
    # Unregister from first activity
    response1 = client.delete(
        "/activities/Programming Class/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Unregister from second activity
    response2 = client.delete(
        "/activities/Debate Team/unregister",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify removed from both
    activities = client.get("/activities").json()
    assert email not in activities["Programming Class"]["participants"]
    assert email not in activities["Debate Team"]["participants"]


def test_unregister_reduces_participant_count(client, fresh_activities):
    """Test that unregistering reduces the participant count."""
    activity = "Science Olympiad"
    email = "ryan@mergington.edu"  # Already participant
    
    # Get initial count
    activities_before = client.get("/activities").json()
    initial_count = len(activities_before[activity]["participants"])
    
    # Unregister
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Get new count
    activities_after = client.get("/activities").json()
    new_count = len(activities_after[activity]["participants"])
    
    # Should be one less
    assert new_count == initial_count - 1


def test_unregister_does_not_affect_other_activities(client, fresh_activities):
    """Test that unregistering from one activity doesn't affect others."""
    email = "sophia@mergington.edu"  # In Programming Class and Debate Team
    
    # Unregister from Programming Class
    response = client.delete(
        "/activities/Programming Class/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify still in Debate Team
    activities = client.get("/activities").json()
    assert email not in activities["Programming Class"]["participants"]
    assert email in activities["Debate Team"]["participants"]


def test_unregister_different_emails_independent(client, fresh_activities):
    """Test that unregistering one student doesn't affect others in same activity."""
    activity = "Gym Class"
    
    # Get all participants before
    activities_before = client.get("/activities").json()
    participants_before = activities_before[activity]["participants"].copy()
    
    # Unregister one student
    student_to_remove = "john@mergington.edu"
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": student_to_remove}
    )
    assert response.status_code == 200
    
    # Verify the student was removed but others are still there
    activities_after = client.get("/activities").json()
    participants_after = activities_after[activity]["participants"]
    
    assert student_to_remove not in participants_after
    
    # All other participants should still be there
    for participant in participants_before:
        if participant != student_to_remove:
            assert participant in participants_after
