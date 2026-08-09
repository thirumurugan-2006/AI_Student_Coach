"""
Tests for Groq Service with mocking to avoid requiring real API keys.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from services.groq_service import GroqService
from pydantic import BaseModel


class TestSchema(BaseModel):
    """Test schema for structured output."""
    message: str
    value: int


@pytest.fixture
def groq_service():
    """Create a GroqService instance with test settings."""
    with patch('services.groq_service.settings') as mock_settings:
        mock_settings.GROQ_API_KEY = "test-api-key"
        mock_settings.GROQ_MODEL = "llama3-8b-8192"
        mock_settings.GROQ_TIMEOUT = 60
        mock_settings.GROQ_TEMPERATURE = 0.3
        mock_settings.GROQ_TOP_P = 0.9
        mock_settings.GROQ_MAX_TOKENS = 2048
        return GroqService()


@pytest.mark.asyncio
async def test_groq_generate_text(groq_service):
    """Test Groq text generation with mocked HTTP response."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Test response from Groq"
                }
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await groq_service.generate("Test prompt")
        
        assert result == "Test response from Groq"
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()


@pytest.mark.asyncio
async def test_groq_generate_structured(groq_service):
    """Test Groq structured output generation with mocked HTTP response."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"message": "Test", "value": 42}'
                }
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await groq_service.generate("Test prompt", schema=TestSchema)
        
        assert isinstance(result, TestSchema)
        assert result.message == "Test"
        assert result.value == 42


@pytest.mark.asyncio
async def test_groq_health_check(groq_service):
    """Test Groq health check with mocked HTTP response."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await groq_service.health_check()
        
        assert result is True


@pytest.mark.asyncio
async def test_groq_connection_error(groq_service):
    """Test Groq connection error handling."""
    with patch('httpx.AsyncClient') as mock_client:
        import httpx
        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.ConnectError("Connection failed")
        
        with pytest.raises(ConnectionError):
            await groq_service.generate("Test prompt")


@pytest.mark.asyncio
async def test_groq_timeout_error(groq_service):
    """Test Groq timeout error handling."""
    with patch('httpx.AsyncClient') as mock_client:
        import httpx
        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
        
        with pytest.raises(TimeoutError):
            await groq_service.generate("Test prompt")
