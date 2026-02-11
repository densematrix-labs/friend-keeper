import pytest


class TestFriendsCRUD:
    """Test friend CRUD operations."""
    
    def test_create_friend(self, client, headers):
        """Test creating a friend."""
        response = client.post(
            "/api/v1/friends",
            json={
                "name": "John Doe",
                "nickname": "Johnny",
                "relation_type": "friend",
                "contact_frequency": "weekly"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["nickname"] == "Johnny"
        assert data["relation_type"] == "friend"
        assert data["contact_frequency"] == "weekly"
        assert data["health_status"] == "red"  # No interactions yet
    
    def test_create_friend_minimal(self, client, headers):
        """Test creating a friend with minimal data."""
        response = client.post(
            "/api/v1/friends",
            json={"name": "Jane"},
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane"
        assert data["relation_type"] == "friend"  # Default
        assert data["contact_frequency"] == "monthly"  # Default
    
    def test_create_friend_missing_device_id(self, client):
        """Test creating friend without device ID."""
        response = client.post(
            "/api/v1/friends",
            json={"name": "Test"}
        )
        assert response.status_code == 400
        assert "X-Device-Id" in response.json()["detail"]
    
    def test_create_friend_invalid_name(self, client, headers):
        """Test creating friend with empty name."""
        response = client.post(
            "/api/v1/friends",
            json={"name": ""},
            headers=headers
        )
        assert response.status_code == 422
    
    def test_list_friends(self, client, headers):
        """Test listing friends."""
        # Create some friends
        client.post("/api/v1/friends", json={"name": "Friend 1"}, headers=headers)
        client.post("/api/v1/friends", json={"name": "Friend 2"}, headers=headers)
        
        response = client.get("/api/v1/friends", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_list_friends_empty(self, client, headers):
        """Test listing friends when empty."""
        response = client.get("/api/v1/friends", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_friends_isolation(self, client, headers):
        """Test that friends are isolated by device ID."""
        # Create friend with device 1
        client.post("/api/v1/friends", json={"name": "Friend 1"}, headers=headers)
        
        # List with device 2
        response = client.get("/api/v1/friends", headers={"X-Device-Id": "other-device"})
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_friend(self, client, headers):
        """Test getting a specific friend."""
        # Create a friend
        create_response = client.post(
            "/api/v1/friends",
            json={"name": "Test Friend"},
            headers=headers
        )
        friend_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/friends/{friend_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Friend"
        assert "interactions" in data
    
    def test_get_friend_not_found(self, client, headers):
        """Test getting non-existent friend."""
        response = client.get("/api/v1/friends/9999", headers=headers)
        assert response.status_code == 404
    
    def test_update_friend(self, client, headers):
        """Test updating a friend."""
        # Create a friend
        create_response = client.post(
            "/api/v1/friends",
            json={"name": "Old Name"},
            headers=headers
        )
        friend_id = create_response.json()["id"]
        
        # Update
        response = client.patch(
            f"/api/v1/friends/{friend_id}",
            json={"name": "New Name", "contact_frequency": "weekly"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["contact_frequency"] == "weekly"
    
    def test_update_friend_not_found(self, client, headers):
        """Test updating non-existent friend."""
        response = client.patch(
            "/api/v1/friends/9999",
            json={"name": "Test"},
            headers=headers
        )
        assert response.status_code == 404
    
    def test_delete_friend(self, client, headers):
        """Test deleting a friend."""
        # Create a friend
        create_response = client.post(
            "/api/v1/friends",
            json={"name": "To Delete"},
            headers=headers
        )
        friend_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/api/v1/friends/{friend_id}", headers=headers)
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/api/v1/friends/{friend_id}", headers=headers)
        assert get_response.status_code == 404
    
    def test_delete_friend_not_found(self, client, headers):
        """Test deleting non-existent friend."""
        response = client.delete("/api/v1/friends/9999", headers=headers)
        assert response.status_code == 404


class TestInteractions:
    """Test interaction logging."""
    
    def test_log_interaction(self, client, headers):
        """Test logging an interaction."""
        # Create a friend
        create_response = client.post(
            "/api/v1/friends",
            json={"name": "Test Friend"},
            headers=headers
        )
        friend_id = create_response.json()["id"]
        
        # Log interaction
        response = client.post(
            f"/api/v1/friends/{friend_id}/interactions",
            json={
                "summary": "Had coffee, talked about work",
                "next_topics": ["Ask about vacation", "Follow up on project"]
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["summary"] == "Had coffee, talked about work"
        assert data["next_topics"] == ["Ask about vacation", "Follow up on project"]
    
    def test_log_interaction_minimal(self, client, headers):
        """Test logging interaction with minimal data."""
        # Create a friend
        create_response = client.post(
            "/api/v1/friends",
            json={"name": "Test"},
            headers=headers
        )
        friend_id = create_response.json()["id"]
        
        # Log minimal interaction
        response = client.post(
            f"/api/v1/friends/{friend_id}/interactions",
            json={},
            headers=headers
        )
        assert response.status_code == 201
    
    def test_log_interaction_not_found(self, client, headers):
        """Test logging interaction for non-existent friend."""
        response = client.post(
            "/api/v1/friends/9999/interactions",
            json={"summary": "Test"},
            headers=headers
        )
        assert response.status_code == 404
    
    def test_interaction_updates_health(self, client, headers):
        """Test that logging interaction updates health status."""
        # Create a friend
        create_response = client.post(
            "/api/v1/friends",
            json={"name": "Test", "contact_frequency": "weekly"},
            headers=headers
        )
        friend_id = create_response.json()["id"]
        
        # Initially red
        get_response = client.get(f"/api/v1/friends/{friend_id}", headers=headers)
        assert get_response.json()["health_status"] == "red"
        
        # Log interaction
        client.post(
            f"/api/v1/friends/{friend_id}/interactions",
            json={"summary": "Talked today"},
            headers=headers
        )
        
        # Now green
        get_response = client.get(f"/api/v1/friends/{friend_id}", headers=headers)
        assert get_response.json()["health_status"] == "green"


class TestDashboard:
    """Test dashboard endpoint."""
    
    def test_dashboard_empty(self, client, headers):
        """Test dashboard with no friends."""
        response = client.get("/api/v1/friends/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_friends"] == 0
        assert data["need_contact_today"] == []
        assert data["need_contact_this_week"] == []
    
    def test_dashboard_with_friends(self, client, headers):
        """Test dashboard with friends."""
        # Create friends
        client.post(
            "/api/v1/friends",
            json={"name": "Friend 1", "contact_frequency": "weekly"},
            headers=headers
        )
        client.post(
            "/api/v1/friends",
            json={"name": "Friend 2", "contact_frequency": "monthly"},
            headers=headers
        )
        
        response = client.get("/api/v1/friends/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_friends"] == 2
        # Both should be red (no interactions)
        assert data["at_risk_friendships"] == 2
