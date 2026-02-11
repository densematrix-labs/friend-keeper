import pytest


class TestTokens:
    """Test token management."""
    
    def test_get_tokens_new_device(self, client, headers):
        """Test getting tokens for a new device."""
        response = client.get("/api/v1/tokens", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["tokens_remaining"] == 0
        assert data["free_trial_remaining"] == 3
    
    def test_get_tokens_missing_device_id(self, client):
        """Test getting tokens without device ID."""
        response = client.get("/api/v1/tokens")
        assert response.status_code == 400


class TestCheckout:
    """Test checkout creation."""
    
    def test_checkout_invalid_product(self, client, headers):
        """Test checkout with invalid product."""
        response = client.post(
            "/api/v1/checkout",
            json={
                "product_sku": "invalid",
                "success_url": "https://example.com/success",
                "device_id": "test-device"
            },
            headers=headers
        )
        assert response.status_code == 400
        assert "Invalid product" in response.json()["detail"]


class TestErrorResponses:
    """Test error response formats."""
    
    def test_402_error_detail_format(self, client, db, headers):
        """Test that 402 errors have proper detail format."""
        # Create a friend first
        friend_response = client.post(
            "/api/v1/friends",
            json={"name": "Test Friend"},
            headers=headers
        )
        friend_id = friend_response.json()["id"]
        
        # Exhaust free trials
        from app.models import GenerationToken
        from tests.conftest import TestingSessionLocal
        
        test_db = TestingSessionLocal()
        token = GenerationToken(device_id="test-device-12345", free_trial_used=10)
        test_db.add(token)
        test_db.commit()
        test_db.close()
        
        # Try to generate
        response = client.post(
            "/api/v1/talk-starters",
            json={"friend_id": friend_id, "language": "en"},
            headers=headers
        )
        
        assert response.status_code == 402
        data = response.json()
        detail = data.get("detail")
        
        # Detail should be object with error field
        if isinstance(detail, dict):
            assert "error" in detail or "message" in detail, \
                f"Object detail must have 'error' or 'message': {detail}"
        else:
            assert isinstance(detail, str), f"detail must be string or object: {detail}"
    
    def test_404_error_detail_is_string(self, client, headers):
        """Test that 404 errors have string detail."""
        response = client.get("/api/v1/friends/99999", headers=headers)
        assert response.status_code == 404
        data = response.json()
        assert isinstance(data["detail"], str)
    
    def test_400_error_detail_is_string(self, client):
        """Test that 400 errors have string detail."""
        response = client.get("/api/v1/friends")  # Missing device ID
        assert response.status_code == 400
        data = response.json()
        assert isinstance(data["detail"], str)


class TestWebhook:
    """Test webhook handling."""
    
    def test_webhook_invalid_json(self, client):
        """Test webhook with invalid JSON."""
        response = client.post(
            "/api/v1/webhook/creem",
            content=b"invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
    
    def test_webhook_unknown_event(self, client):
        """Test webhook with unknown event type."""
        response = client.post(
            "/api/v1/webhook/creem",
            json={"event_type": "unknown.event", "object": {}}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ignored"
    
    def test_webhook_checkout_completed_missing_metadata(self, client):
        """Test webhook with missing metadata."""
        response = client.post(
            "/api/v1/webhook/creem",
            json={
                "event_type": "checkout.completed",
                "object": {"id": "test-checkout"}
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "missing metadata"
