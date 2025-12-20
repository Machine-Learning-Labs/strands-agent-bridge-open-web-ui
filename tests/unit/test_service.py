"""
Unit tests for ChatService.
"""

import pytest
import base64
from unittest.mock import Mock, patch

from src.service import ChatService
from src.models import Message, TextContent, ImageContent, ImageUrl


class TestChatService:
    """Test ChatService class."""

    @pytest.fixture
    def service(self, mock_alfred_agent):
        """Create ChatService with mocked agent."""
        service = ChatService()
        service.alfred = mock_alfred_agent
        return service


class TestParseImageUrl:
    """Test parse_image_url method."""

    @pytest.fixture
    def service(self, mock_alfred_agent):
        service = ChatService()
        service.alfred = mock_alfred_agent
        return service

    def test_parse_base64_image(self, service):
        """Test parsing base64 data URL."""
        # Create a simple base64 encoded image
        image_data = b"fake_image_data"
        encoded = base64.b64encode(image_data).decode()
        data_url = f"data:image/png;base64,{encoded}"

        result = service.parse_image_url(data_url)
        assert result == image_data

    @patch("src.service.requests.get")
    def test_parse_http_url_success(self, mock_get, service):
        """Test parsing HTTP URL successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"image_content"
        mock_get.return_value = mock_response

        result = service.parse_image_url("https://example.com/image.png")
        assert result == b"image_content"
        mock_get.assert_called_once()


class TestConvertMessageToStrandsFormat:
    """Test convert_message_to_strands_format method."""

    @pytest.fixture
    def service(self, mock_alfred_agent):
        service = ChatService()
        service.alfred = mock_alfred_agent
        return service

    def test_convert_text_message(self, service):
        """Test converting simple text message."""
        message = Message(role="user", content="Hello world")
        result = service.convert_message_to_strands_format(message)
        assert result == "Hello world"

    def test_convert_multimodal_message(self, service):
        """Test converting multimodal message."""
        with patch.object(service, "parse_image_url", return_value=b"fake_image"):
            content = [
                TextContent(text="What's in this image?"),
                ImageContent(image_url=ImageUrl(url="data:image/png;base64,fake")),
            ]
            message = Message(role="user", content=content)

            result = service.convert_message_to_strands_format(message)

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0] == {"text": "What's in this image?"}
            assert "image" in result[1]


class TestExtractTextForTokens:
    """Test extract_text_for_tokens method."""

    @pytest.fixture
    def service(self, mock_alfred_agent):
        service = ChatService()
        service.alfred = mock_alfred_agent
        return service

    def test_extract_from_text_message(self, service):
        """Test extracting text from simple message."""
        message = Message(role="user", content="Hello world")
        result = service.extract_text_for_tokens(message)
        assert result == "Hello world"

    def test_extract_from_multimodal_message(self, service):
        """Test extracting text from multimodal message."""
        content = [
            TextContent(text="First part"),
            ImageContent(image_url=ImageUrl(url="https://example.com/image.png")),
            TextContent(text="Second part"),
        ]
        message = Message(role="user", content=content)

        result = service.extract_text_for_tokens(message)
        assert result == "First part Second part"


class TestEstimateTokenUsage:
    """Test estimate_token_usage method."""

    @pytest.fixture
    def service(self, mock_alfred_agent):
        service = ChatService()
        service.alfred = mock_alfred_agent
        return service

    def test_estimate_text_only(self, service):
        """Test token estimation for text-only messages."""
        messages = [
            Message(role="user", content="Hello world"),
            Message(role="assistant", content="Hi there"),
        ]
        response_text = "How can I help you?"

        usage = service.estimate_token_usage(messages, response_text)

        assert usage.prompt_tokens == 4  # "Hello world" + "Hi there" = 4 words
        assert usage.completion_tokens == 5  # "How can I help you?" = 5 words
        assert usage.total_tokens == 9
