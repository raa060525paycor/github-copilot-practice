"""
Tests for the POST /activities/{activity_name}/signup endpoint.
"""
import pytest


def test_signup_happy_path(client, fresh_activities):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newhero@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newhero@mergington.edu for Chess Club"
    
    # Verify email was added to participants
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "newhero@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_activity_not_found(client, fresh_activities):
    """Test signup for a non-existent activity returns 404."""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client, fresh_activities):
    """Test signup for an activity when student is already registered returns 400."""
    # michael@mergington.edu is already in Chess Club
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_multiple_different_students(client, fresh_activities):
    """Test that multiple different students can signup for the same activity."""
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    email3 = "student3@mergington.edu"
    
    # Signup first student
    response1 = client.post(
        "/activities/Tennis Club/signup",
        params={"email": email1}
    )
    assert response1.status_code == 200
    
    # Signup second student
    response2 = client.post(
        "/activities/Tennis Club/signup",
        params={"email": email2}
    )
    assert response2.status_code == 200
    
    # Signup third student
    response3 = client.post(
        "/activities/Tennis Club/signup",
        params={"email": email3}
    )
    assert response3.status_code == 200
    
    # Verify all 3 are registered (plus the 1 original = 4 total)
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    participants = activities_data["Tennis Club"]["participants"]
    
    assert email1 in participants
    assert email2 in participants
    assert email3 in participants
    assert len(participants) == 4  # 1 original + 3 new


def test_signup_same_student_twice_fails(client, fresh_activities):
    """Test that signing up the same student twice fails on second attempt."""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        "/activities/Art Studio/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        "/activities/Art Studio/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_response_message_format(client, fresh_activities):
    """Test that signup response message has correct format."""
    email = "format@mergington.edu"
    activity = "Science Olympiad"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity}"


def test_signup_to_different_activities(client, fresh_activities):
    """Test that a student can signup for multiple different activities."""
    email = "multitask@mergington.edu"
    
    # Signup for first activity
    response1 = client.post(
        "/activities/Debate Team/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Signup for second activity
    response2 = client.post(
        "/activities/Drama Club/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify in both activities
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    
    assert email in activities_data["Debate Team"]["participants"]
    assert email in activities_data["Drama Club"]["participants"]


def test_signup_with_special_characters_in_email(client, fresh_activities):
    """Test signup with various valid email formats."""
    emails = [
        "student+tag@mergington.edu",
        "first.last@mergington.edu",
        "name_underscore@mergington.edu"
    ]
    
    for email in emails:
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200, f"Failed for email: {email}"


def test_signup_case_sensitive_email(client, fresh_activities):
    """Test that emails are case-sensitive in registration check."""
    email_lower = "casesensitive@mergington.edu"
    email_upper = "CASESENSITIVE@mergington.edu"
    
    # Signup with lowercase
    response1 = client.post(
        "/activities/Gym Class/signup",
        params={"email": email_lower}
    )
    assert response1.status_code == 200
    
    # Signup with uppercase should succeed (different email)
    response2 = client.post(
        "/activities/Gym Class/signup",
        params={"email": email_upper}
    )
    assert response2.status_code == 200
    
    # Both should be in participants
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    participants = activities_data["Gym Class"]["participants"]
    
    assert email_lower in participants
    assert email_upper in participants
