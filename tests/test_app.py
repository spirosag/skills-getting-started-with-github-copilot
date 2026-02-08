"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import copy

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import app as app_module


@pytest.fixture
def client():
    """Create a test client for the FastAPI app with fresh state"""
    # Reset the activities to initial state for each test
    initial_activities = {
        "Basketball Team": {
            "description": "Join the varsity and JV basketball teams for competitive play",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Volleyball Club": {
            "description": "Learn volleyball skills and compete in tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["jordan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and theatrical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["marcus@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation skills and compete in debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ryan@mergington.edu", "sophia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore advanced scientific concepts",
            "schedule": "Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(initial_activities))
    
    return TestClient(app_module.app)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing"""
    return "test-student@mergington.edu"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that get activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that get activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Basketball Team",
            "Volleyball Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_details in activities.items():
            for field in required_fields:
                assert field in activity_details, f"Missing {field} in {activity_name}"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_returns_200(self, client, sample_email):
        """Test that signup returns a 200 status code"""
        response = client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200

    def test_signup_for_activity_returns_success_message(self, client, sample_email):
        """Test that signup returns a success message"""
        response = client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_email):
        """Test that signup adds the participant to the activity"""
        # First, get initial participants
        response = client.get("/activities")
        initial_count = len(response.json()["Basketball Team"]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        assert signup_response.status_code == 200
        
        # Check that participant was added
        response = client.get("/activities")
        final_count = len(response.json()["Basketball Team"]["participants"])
        assert final_count == initial_count + 1
        assert sample_email in response.json()["Basketball Team"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client, sample_email):
        """Test that signup for a nonexistent activity returns 404"""
        response = client.post(
            f"/activities/Nonexistent Activity/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_fails(self, client, sample_email):
        """Test that signing up twice for the same activity fails"""
        # Sign up for the first time
        response1 = client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Try to sign up again
        response2 = client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity_returns_200(self, client, sample_email):
        """Test that unregister returns a 200 status code"""
        # First sign up
        client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        
        # Then unregister
        response = client.post(
            f"/activities/Basketball Team/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 200

    def test_unregister_from_activity_returns_success_message(self, client, sample_email):
        """Test that unregister returns a success message"""
        # Sign up first
        client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        
        # Unregister
        response = client.post(
            f"/activities/Basketball Team/unregister",
            params={"email": sample_email}
        )
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]

    def test_unregister_removes_participant_from_activity(self, client, sample_email):
        """Test that unregister removes the participant from the activity"""
        # Sign up
        client.post(
            f"/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        
        # Get count before unregister
        response = client.get("/activities")
        count_before = len(response.json()["Basketball Team"]["participants"])
        
        # Unregister
        unregister_response = client.post(
            f"/activities/Basketball Team/unregister",
            params={"email": sample_email}
        )
        assert unregister_response.status_code == 200
        
        # Check that participant was removed
        response = client.get("/activities")
        count_after = len(response.json()["Basketball Team"]["participants"])
        assert count_after == count_before - 1
        assert sample_email not in response.json()["Basketball Team"]["participants"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client, sample_email):
        """Test that unregister from a nonexistent activity returns 404"""
        response = client.post(
            f"/activities/Nonexistent Activity/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_when_not_signed_up_fails(self, client, sample_email):
        """Test that unregistering when not signed up fails"""
        response = client.post(
            f"/activities/Basketball Team/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_endpoint_redirects(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
