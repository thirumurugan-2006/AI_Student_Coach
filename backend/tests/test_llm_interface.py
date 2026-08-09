"""
Tests for LLM Interface with provider switching.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from core.llm_interface import LLMInterface
from pydantic import BaseModel


class TestSchema(BaseModel):
    """Test schema for structured output."""
    message: str


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('core.llm_interface.settings') as mock:
        mock.LLM_PROVIDER = "groq"
        yield mock


@pytest.mark.asyncio
async def test_llm_interface_groq_provider(mock_settings):
    """Test LLM Interface with Groq provider."""
    with patch('core.llm_interface.GroqService') as mock_groq_class:
        mock_groq = Mock()
        mock_groq.generate = AsyncMock(return_value="Test response")
        mock_groq.health_check = AsyncMock(return_value=True)
        mock_groq_class.return_value = mock_groq
        
        llm = LLMInterface()
        
        assert llm.provider == "groq"
        
        result = await llm.generate("Test prompt")
        assert result == "Test response"
        
        health = await llm.health_check()
        assert health is True


@pytest.mark.asyncio
async def test_llm_interface_ollama_provider():
    """Test LLM Interface with Ollama provider."""
    with patch('core.llm_interface.settings') as mock_settings:
        mock_settings.LLM_PROVIDER = "ollama"
        
        with patch('core.llm_interface.OllamaService') as mock_ollama_class:
            mock_ollama = Mock()
            mock_ollama.generate = AsyncMock(return_value="Test response")
            mock_ollama.health_check = AsyncMock(return_value=True)
            mock_ollama_class.return_value = mock_ollama
            
            llm = LLMInterface()
            
            assert llm.provider == "ollama"
            
            result = await llm.generate("Test prompt")
            assert result == "Test response"


@pytest.mark.asyncio
async def test_llm_interface_structured_output(mock_settings):
    """Test LLM Interface with structured output schema."""
    with patch('core.llm_interface.GroqService') as mock_groq_class:
        mock_groq = Mock()
        mock_response = TestSchema(message="Test", value=42)
        mock_groq.generate = AsyncMock(return_value=mock_response)
        mock_groq_class.return_value = mock_groq
        
        llm = LLMInterface()
        result = await llm.generate("Test prompt", schema=TestSchema)
        
        assert isinstance(result, TestSchema)
        assert result.message == "Test"
