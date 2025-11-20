"""
Tests for edge cases and error handling
"""
import pytest
from urllib.parse import quote


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_signup_empty_email(self, client, reset_activities):
        """Test signup with empty email parameter"""
        activity = "Chess Club"
        response = client.post(f"/activities/{activity}/signup?email=")
        # Should still work as empty string is a valid parameter value
        assert response.status_code == 200
    
    def test_signup_missing_email_parameter(self, client, reset_activities):
        """Test signup without email parameter"""
        activity = "Chess Club"
        response = client.post(f"/activities/{activity}/signup")
        assert response.status_code == 422  # FastAPI validation error
    
    def test_unregister_empty_email(self, client, reset_activities):
        """Test unregister with empty email parameter"""
        activity = "Chess Club"
        response = client.delete(f"/activities/{activity}/unregister?email=")
        assert response.status_code == 400  # Student not registered
    
    def test_unregister_missing_email_parameter(self, client, reset_activities):
        """Test unregister without email parameter"""
        activity = "Chess Club"
        response = client.delete(f"/activities/{activity}/unregister")
        assert response.status_code == 422  # FastAPI validation error
    
    def test_activity_name_with_special_characters(self, client, reset_activities):
        """Test activity names with special characters"""
        from src.app import activities
        
        # Add a test activity with special characters
        special_activity = "Test & Activity (Special)"
        activities[special_activity] = {
            "description": "Test activity with special characters",
            "schedule": "Test schedule",
            "max_participants": 10,
            "participants": []
        }
        
        email = "test@mergington.edu"
        encoded_activity = quote(special_activity)
        
        # Test signup
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[special_activity]["participants"]
        
        # Test unregister
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={email}")
        assert response.status_code == 200
        assert email not in activities[special_activity]["participants"]
        
        # Cleanup
        del activities[special_activity]
    
    def test_case_sensitive_activity_names(self, client, reset_activities):
        """Test that activity names are case sensitive"""
        email = "test@mergington.edu"
        
        # Try with different case
        response = client.post("/activities/chess%20club/signup?email=" + email)
        assert response.status_code == 404  # Should not find "chess club"
        
        # Try with correct case
        response = client.post("/activities/Chess%20Club/signup?email=" + email)
        assert response.status_code == 200


class TestDataConsistency:
    """Test data consistency and state management"""
    
    def test_participant_list_integrity(self, client, reset_activities):
        """Test that participant lists maintain integrity"""
        from src.app import activities
        
        activity = "Chess Club"
        initial_participants = activities[activity]["participants"].copy()
        email = "integrity@mergington.edu"
        
        # Add participant
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify only one instance was added
        count = activities[activity]["participants"].count(email)
        assert count == 1
        
        # Verify original participants are still there
        for participant in initial_participants:
            assert participant in activities[activity]["participants"]
    
    def test_concurrent_operations_simulation(self, client, reset_activities):
        """Test simulated concurrent operations"""
        from src.app import activities
        
        activity = "Programming Class"
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Simulate multiple rapid signups
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        for email in emails:
            assert email in activities[activity]["participants"]
        
        # Simulate rapid unregistrations
        for email in emails[:3]:
            response = client.delete(f"/activities/{activity}/unregister?email={email}")
            assert response.status_code == 200
        
        # Verify correct ones were removed
        for email in emails[:3]:
            assert email not in activities[activity]["participants"]
        for email in emails[3:]:
            assert email in activities[activity]["participants"]


class TestHTTPMethods:
    """Test HTTP method restrictions and behavior"""
    
    def test_signup_wrong_http_method(self, client):
        """Test signup endpoint with wrong HTTP methods"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        url = f"/activities/{activity}/signup?email={email}"
        
        # Test GET method (should not be allowed)
        response = client.get(url)
        assert response.status_code == 405  # Method not allowed
        
        # Test DELETE method (should not be allowed)
        response = client.delete(url)
        assert response.status_code == 405  # Method not allowed
    
    def test_unregister_wrong_http_method(self, client):
        """Test unregister endpoint with wrong HTTP methods"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        url = f"/activities/{activity}/unregister?email={email}"
        
        # Test GET method (should not be allowed)
        response = client.get(url)
        assert response.status_code == 405  # Method not allowed
        
        # Test POST method (should not be allowed)
        response = client.post(url)
        assert response.status_code == 405  # Method not allowed