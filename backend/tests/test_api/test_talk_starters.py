import pytest
from unittest.mock import patch, AsyncMock


class TestTalkStarters:
    """Test talk starter generation."""
    
    def test_generate_talk_starters_missing_device_id(self, client):
        """Test generating starters without device ID."""
        response = client.post(
            "/api/v1/talk-starters",
            json={"friend_id": 1, "language": "en"}
        )
        assert response.status_code == 400
    
    def test_generate_talk_starters_friend_not_found(self, client, headers):
        """Test generating starters for non-existent friend."""
        response = client.post(
            "/api/v1/talk-starters",
            json={"friend_id": 9999, "language": "en"},
            headers=headers
        )
        # Will return 402 first (no tokens) or 404 (friend not found)
        assert response.status_code in [402, 404]
    
    @patch('app.services.llm_service.generate_talk_starters')
    def test_generate_talk_starters_success(self, mock_llm, client, headers):
        """Test successful talk starter generation."""
        mock_llm.return_value = [
            "How was your weekend?",
            "Any exciting plans?",
            "How's the project going?"
        ]
        
        # Create a friend
        friend_response = client.post(
            "/api/v1/friends",
            json={"name": "Test Friend"},
            headers=headers
        )
        friend_id = friend_response.json()["id"]
        
        # Generate starters (uses free trial)
        response = client.post(
            "/api/v1/talk-starters",
            json={"friend_id": friend_id, "language": "en"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "starters" in data
        assert len(data["starters"]) > 0
    
    @patch('app.services.llm_service.generate_talk_starters')
    def test_generate_talk_starters_exhausted_free_trial(self, mock_llm, client, db, headers):
        """Test generation when free trial exhausted."""
        # Create friend first
        friend_response = client.post(
            "/api/v1/friends",
            json={"name": "Test"},
            headers=headers
        )
        friend_id = friend_response.json()["id"]
        
        # Exhaust free trials by making 3 requests
        mock_llm.return_value = ["Starter 1", "Starter 2"]
        
        for i in range(3):
            response = client.post(
                "/api/v1/talk-starters",
                json={"friend_id": friend_id, "language": "en"},
                headers=headers
            )
            assert response.status_code == 200
        
        # 4th request should fail
        response = client.post(
            "/api/v1/talk-starters",
            json={"friend_id": friend_id, "language": "en"},
            headers=headers
        )
        assert response.status_code == 402
        
        # Check error format
        data = response.json()
        detail = data.get("detail")
        if isinstance(detail, dict):
            assert "error" in detail


class TestTalkStartersLanguages:
    """Test talk starters with different languages."""
    
    @patch('app.services.llm_service.generate_talk_starters')
    def test_generate_starters_chinese(self, mock_llm, client, headers):
        """Test generating starters in Chinese."""
        mock_llm.return_value = ["最近怎么样？", "有什么新鲜事吗？"]
        
        friend_response = client.post(
            "/api/v1/friends",
            json={"name": "测试朋友"},
            headers=headers
        )
        friend_id = friend_response.json()["id"]
        
        response = client.post(
            "/api/v1/talk-starters",
            json={"friend_id": friend_id, "language": "zh"},
            headers=headers
        )
        assert response.status_code == 200
    
    @patch('app.services.llm_service.generate_talk_starters')
    def test_generate_starters_japanese(self, mock_llm, client, headers):
        """Test generating starters in Japanese."""
        mock_llm.return_value = ["最近どうですか？", "何か新しいことありますか？"]
        
        friend_response = client.post(
            "/api/v1/friends",
            json={"name": "テスト"},
            headers=headers
        )
        friend_id = friend_response.json()["id"]
        
        response = client.post(
            "/api/v1/talk-starters",
            json={"friend_id": friend_id, "language": "ja"},
            headers=headers
        )
        assert response.status_code == 200
