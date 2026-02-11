import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

from app.services.llm_service import generate_talk_starters


class TestLLMService:
    """Test LLM service."""
    
    @pytest.mark.asyncio
    async def test_generate_starters_no_api_key(self):
        """Test fallback when no API key."""
        with patch('app.services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_proxy_key = ""
            
            starters = await generate_talk_starters(
                "John",
                "friend",
                "No previous interactions",
                "en"
            )
            
            assert len(starters) == 3
            assert "How have you been" in starters[0]
    
    @pytest.mark.asyncio
    async def test_generate_starters_success(self):
        """Test successful API call."""
        with patch('app.services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_proxy_key = "test-key"
            mock_settings.return_value.llm_proxy_url = "https://test.api"
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '["How are you?", "What\'s new?", "Any plans?"]'
                    }
                }]
            }
            mock_response.raise_for_status = MagicMock()
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                starters = await generate_talk_starters(
                    "John",
                    "friend",
                    "Previous: Had coffee",
                    "en"
                )
                
                assert len(starters) == 3
                assert "How are you?" in starters
    
    @pytest.mark.asyncio
    async def test_generate_starters_api_error(self):
        """Test fallback on API error."""
        with patch('app.services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_proxy_key = "test-key"
            mock_settings.return_value.llm_proxy_url = "https://test.api"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    side_effect=httpx.HTTPError("API Error")
                )
                
                starters = await generate_talk_starters(
                    "John",
                    "friend",
                    "Previous: Had coffee",
                    "en"
                )
                
                # Should return fallback starters
                assert len(starters) == 3
                assert "How have you been" in starters[0]
    
    @pytest.mark.asyncio
    async def test_generate_starters_different_languages(self):
        """Test language parameter is used."""
        with patch('app.services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_proxy_key = "test-key"
            mock_settings.return_value.llm_proxy_url = "https://test.api"
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '["最近怎么样？", "有什么新鲜事？"]'
                    }
                }]
            }
            mock_response.raise_for_status = MagicMock()
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.post = mock_post
                
                await generate_talk_starters(
                    "小明",
                    "friend",
                    "之前聊了工作",
                    "zh"
                )
                
                # Verify the call included Chinese in the prompt
                call_args = mock_post.call_args
                assert "Chinese" in str(call_args)
