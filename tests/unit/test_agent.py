"""
Unit tests for AlfredAgent.
"""

import pytest
from unittest.mock import Mock, patch

from src.agent import AlfredAgent, create_alfred_agent


class TestAlfredAgent:
    """Test AlfredAgent class."""

    @patch("src.agent.BedrockModel")
    @patch("src.agent.Agent")
    def test_init_default_params(self, mock_agent_class, mock_bedrock_model):
        """Test AlfredAgent initialization with default parameters."""
        mock_model = Mock()
        mock_bedrock_model.return_value = mock_model
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        agent = AlfredAgent()

        # Check BedrockModel was created with correct parameters
        mock_bedrock_model.assert_called_once_with(
            model_id="us.amazon.nova-pro-v1:0", temperature=0.7, streaming=False
        )

        # Check Agent was created with model and system prompt
        mock_agent_class.assert_called_once()
        call_args = mock_agent_class.call_args
        assert call_args[1]["model"] == mock_model
        assert "Alfred Pennyworth" in call_args[1]["system_prompt"]

        assert agent.model == mock_model
        assert agent.agent == mock_agent

    def test_system_prompt_content(self):
        """Test that system prompt contains expected Alfred characteristics."""
        with patch("src.agent.BedrockModel"), patch("src.agent.Agent"):
            agent = AlfredAgent()

            prompt = agent.system_prompt
            assert "Alfred Pennyworth" in prompt
            assert "British manners" in prompt
            assert "dry wit" in prompt
            assert "loyalty" in prompt
            assert "Master Wayne" in prompt


class TestAlfredAgentInvoke:
    """Test AlfredAgent invoke methods."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent with proper response structure."""
        with patch("src.agent.BedrockModel"), patch(
            "src.agent.Agent"
        ) as mock_agent_class:
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            alfred = AlfredAgent()
            alfred.agent = mock_agent_instance
            return alfred, mock_agent_instance

    def test_invoke_successful_response(self, mock_agent):
        """Test successful invoke with proper response structure."""
        alfred, mock_agent_instance = mock_agent

        # Mock successful response
        mock_result = Mock()
        mock_result.message = {
            "content": [{"text": "Good day, sir. How may I assist you?"}]
        }
        mock_agent_instance.return_value = mock_result

        result = alfred.invoke("Hello Alfred")

        assert result == "Good day, sir. How may I assist you?"
        mock_agent_instance.assert_called_once_with("Hello Alfred")

    def test_invoke_empty_content(self, mock_agent):
        """Test invoke with empty content response."""
        alfred, mock_agent_instance = mock_agent

        # Mock response with empty content
        mock_result = Mock()
        mock_result.message = {"content": []}
        mock_agent_instance.return_value = mock_result

        result = alfred.invoke("Hello Alfred")

        assert "difficulty formulating a response" in result

    def test_invoke_exception_handling(self, mock_agent):
        """Test invoke exception handling."""
        alfred, mock_agent_instance = mock_agent

        # Mock agent raising exception
        mock_agent_instance.side_effect = Exception("Test error")

        result = alfred.invoke("Hello Alfred")

        assert "I apologise, but I encountered an issue" in result
        assert "Test error" in result


class TestCreateAlfredAgent:
    """Test create_alfred_agent factory function."""

    @patch("src.agent.AlfredAgent")
    def test_create_alfred_agent(self, mock_alfred_class):
        """Test factory function creates agent with correct model."""
        mock_agent = Mock()
        mock_alfred_class.return_value = mock_agent

        result = create_alfred_agent()

        mock_alfred_class.assert_called_once_with(model_id="us.amazon.nova-pro-v1:0")
        assert result == mock_agent
