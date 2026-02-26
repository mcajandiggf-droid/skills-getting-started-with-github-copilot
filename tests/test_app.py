"""
Backend tests for Mergington High School activities API.
Tests follow the Arrange-Act-Assert (AAA) pattern.
"""

from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities to reset between tests
INITIAL_ACTIVITIES = deepcopy(activities)

# Create test client
client = TestClient(app)


def setup_function():
    """Reset activities to initial state before each test."""
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_initial_data():
    """Test that GET /activities returns the initial activities data."""
    # Arrange: no setup needed, initial state is already set

    # Act: fetch all activities
    response = client.get("/activities")

    # Assert: verify response and data
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_new_participant_succeeds():
    """Test that signing up a new participant with valid activity succeeds."""
    # Arrange: prepare test data
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    original_count = len(activities[activity_name]["participants"])

    # Act: signup new participant
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert: verify response and side effects
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == original_count + 1


def test_signup_duplicate_participant_fails():
    """Test that signing up a duplicate participant returns 400 error."""
    # Arrange: choose an existing participant
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]
    original_count = len(activities[activity_name]["participants"])

    # Act: attempt to signup duplicate
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email}
    )

    # Assert: verify error and no changes
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    assert len(activities[activity_name]["participants"]) == original_count


def test_signup_nonexistent_activity_fails():
    """Test that signing up for a non-existent activity returns 404 error."""
    # Arrange: prepare test data with invalid activity
    invalid_activity = "Nonexistent Club"
    test_email = "student@mergington.edu"

    # Act: attempt to signup for invalid activity
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": test_email}
    )

    # Assert: verify 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant_succeeds():
    """Test that removing an existing participant succeeds."""
    # Arrange: select a participant to remove
    activity_name = "Chess Club"
    email_to_remove = activities[activity_name]["participants"][0]
    original_count = len(activities[activity_name]["participants"])

    # Act: remove the participant
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email_to_remove}
    )

    # Assert: verify response and side effects
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
    assert email_to_remove not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == original_count - 1


def test_remove_nonexistent_participant_fails():
    """Test that removing a non-existent participant returns 404 error."""
    # Arrange: prepare test data with email not in activity
    activity_name = "Chess Club"
    nonexistent_email = "notasignup@mergington.edu"

    # Act: attempt to remove non-existent participant
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": nonexistent_email}
    )

    # Assert: verify 404 error
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


def test_remove_from_nonexistent_activity_fails():
    """Test that removing from a non-existent activity returns 404 error."""
    # Arrange: prepare test data with invalid activity
    invalid_activity = "Nonexistent Club"
    test_email = "student@mergington.edu"

    # Act: attempt to remove from invalid activity
    response = client.delete(
        f"/activities/{invalid_activity}/participants",
        params={"email": test_email}
    )

    # Assert: verify 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
