import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app, follow_redirects=False)

class TestActivitiesAPI:
    """Test suite for the Activities API endpoints"""

    def test_get_activities_success(self):
        """Test successful retrieval of all activities"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@example.com"
        initial_participants = activities[activity_name]["participants"].copy()

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        # Verify participant was added
        assert email in activities[activity_name]["participants"]
        # Clean up
        activities[activity_name]["participants"].remove(email)

    def test_signup_for_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        activity_name = "NonExistentActivity"
        email = "test@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_for_activity_duplicate(self):
        """Test signup when student is already signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]  # Use existing participant

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_for_activity_full(self):
        """Test signup when activity is at max capacity"""
        # Arrange
        activity_name = "Chess Club"
        # Fill the activity to max capacity
        max_participants = activities[activity_name]["max_participants"]
        emails_to_add = [f"temp{i}@example.com" for i in range(10)]  # Add 10 to fill from 2 to 12

        # Add participants to fill up
        for email in emails_to_add:
            if len(activities[activity_name]["participants"]) < max_participants:
                activities[activity_name]["participants"].append(email)

        # Now try to add one more
        extra_email = "overflow@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": extra_email})

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Activity is full" in data["detail"]

        # Clean up
        for email in emails_to_add:
            if email in activities[activity_name]["participants"]:
                activities[activity_name]["participants"].remove(email)

    def test_remove_participant_success(self):
        """Test successful removal of a participant"""
        # Arrange
        activity_name = "Programming Class"
        email = "test_remove@example.com"
        # Add the participant first
        activities[activity_name]["participants"].append(email)

        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        # Verify participant was removed
        assert email not in activities[activity_name]["participants"]

    def test_remove_participant_activity_not_found(self):
        """Test removal from non-existent activity"""
        # Arrange
        activity_name = "NonExistentActivity"
        email = "test@example.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self):
        """Test removal of non-existent participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@example.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_root_redirect(self):
        """Test root endpoint redirects to static index"""
        # Arrange - No special setup

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"