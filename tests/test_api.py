"""
Tests for the main API endpoints
"""
import pytest
from src.app import activities


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that default activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Ensure student is not already signed up
        assert email not in activities[activity]["participants"]
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify student was added
        assert email in activities[activity]["participants"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test signup with student already registered"""
        activity = "Chess Club"
        existing_email = activities[activity]["participants"][0]
        
        response = client.post(f"/activities/{activity}/signup?email={existing_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for nonexistent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_url_encoded_activity(self, client, reset_activities):
        """Test signup with URL-encoded activity name"""
        email = "student@mergington.edu"
        activity = "Track and Field"
        encoded_activity = "Track%20and%20Field"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student was added to the correct activity
        assert email in activities[activity]["participants"]
    
    def test_signup_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email"""
        from urllib.parse import quote
        email = "student+test@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='@')}")
        assert response.status_code == 200
        
        assert email in activities[activity]["participants"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        activity = "Chess Club"
        email = activities[activity]["participants"][0]
        
        # Ensure student is registered
        assert email in activities[activity]["participants"]
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify student was removed
        assert email not in activities[activity]["participants"]
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregistration with student not registered"""
        activity = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Ensure student is not registered
        assert email not in activities[activity]["participants"]
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from nonexistent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_url_encoded_activity(self, client, reset_activities):
        """Test unregistration with URL-encoded activity name"""
        activity = "Track and Field"
        encoded_activity = "Track%20and%20Field"
        
        # First add a student
        email = "student@mergington.edu"
        activities[activity]["participants"].append(email)
        
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify student was removed
        assert email not in activities[activity]["participants"]


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple operations"""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete signup and unregister flow"""
        email = "flowtest@mergington.edu"
        activity = "Programming Class"
        
        # Initial state - student not registered
        assert email not in activities[activity]["participants"]
        initial_count = len(activities[activity]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count + 1
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count
    
    def test_multiple_signups_different_activities(self, client, reset_activities):
        """Test student signing up for multiple different activities"""
        email = "multistudent@mergington.edu"
        activities_list = ["Chess Club", "Art Club", "Drama Society"]
        
        # Sign up for multiple activities
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
            assert email in activities[activity]["participants"]
        
        # Verify student is in all activities
        for activity in activities_list:
            assert email in activities[activity]["participants"]
    
    def test_activity_capacity_not_enforced(self, client, reset_activities):
        """Test that the API doesn't currently enforce capacity limits"""
        activity = "Chess Club"
        max_participants = activities[activity]["max_participants"]
        current_count = len(activities[activity]["participants"])
        
        # Add students beyond capacity (if not already at capacity)
        emails_to_add = []
        for i in range(max_participants - current_count + 5):
            email = f"student{i}@mergington.edu"
            emails_to_add.append(email)
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all students were added (no capacity enforcement)
        for email in emails_to_add:
            assert email in activities[activity]["participants"]