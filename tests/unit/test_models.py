"""
Unit tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from src.models import (
    ImageUrl,
    TextContent,
    ImageContent,
    Message,
    ChatCompletionRequest,
    Usage,
    Model,
    ModelList,
)


class TestImageUrl:
    """Test ImageUrl model."""

    def test_valid_image_url(self):
        """Test creating a valid ImageUrl."""
        image_url = ImageUrl(url="https://example.com/image.png")
        assert image_url.url == "https://example.com/image.png"
        assert image_url.detail == "auto"

    def test_image_url_with_detail(self):
        """Test ImageUrl with custom detail."""
        image_url = ImageUrl(url="https://example.com/image.png", detail="high")
        assert image_url.detail == "high"


class TestTextContent:
    """Test TextContent model."""

    def test_valid_text_content(self):
        """Test creating valid TextContent."""
        content = TextContent(text="Hello world")
        assert content.type == "text"
        assert content.text == "Hello world"


class TestMessage:
    """Test Message model."""

    def test_text_message(self):
        """Test message with text content."""
        message = Message(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"

    def test_multimodal_message(self):
        """Test message with mixed content."""
        content = [
            TextContent(text="What's in this image?"),
            ImageContent(image_url=ImageUrl(url="https://example.com/image.png")),
        ]
        message = Message(role="user", content=content)
        assert message.role == "user"
        assert len(message.content) == 2


class TestChatCompletionRequest:
    """Test ChatCompletionRequest model."""

    def test_minimal_request(self):
        """Test minimal chat completion request."""
        messages = [Message(role="user", content="Hello")]
        request = ChatCompletionRequest(model="alfred-butler", messages=messages)

        assert request.model == "alfred-butler"
        assert len(request.messages) == 1
        assert request.temperature == 0.7  # default
        assert request.stream is False  # default


class TestUsage:
    """Test Usage model."""

    def test_valid_usage(self):
        """Test creating valid Usage."""
        usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 5
        assert usage.total_tokens == 15


class TestModel:
    """Test Model model."""

    def test_valid_model(self):
        """Test creating valid Model."""
        model = Model(id="alfred-butler", created=1234567890, owned_by="strands-agents")
        assert model.id == "alfred-butler"
        assert model.object == "model"
        assert model.created == 1234567890
        assert model.owned_by == "strands-agents"


class TestModelList:
    """Test ModelList model."""

    def test_valid_model_list(self):
        """Test creating valid ModelList."""
        model = Model(id="alfred-butler", created=1234567890, owned_by="strands-agents")
        model_list = ModelList(data=[model])

        assert model_list.object == "list"
        assert len(model_list.data) == 1
        assert model_list.data[0].id == "alfred-butler"
