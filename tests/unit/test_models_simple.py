"""
Simple unit tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from src.models import ImageUrl, TextContent, Message


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
