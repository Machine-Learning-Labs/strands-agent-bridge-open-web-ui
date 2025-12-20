"""
Simple pytest configuration and fixtures.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from src.api import app
from src.models import Message, TextContent, ImageContent, ImageUrl


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_alfred_agent():
    """Create a mock Alfred agent."""
    mock_agent = Mock()
    mock_agent.invoke = Mock(return_value="Good day, sir. How may I assist you?")
    return mock_agent


@pytest.fixture
def sample_text_message():
    """Create a sample text message."""
    return Message(role="user", content="Hello Alfred, how are you today?")


@pytest.fixture
def sample_image_message():
    """Create a sample image message."""
    return Message(
        role="user",
        content=[
            TextContent(type="text", text="What do you see?"),
            ImageContent(
                type="image_url",
                image_url=ImageUrl(
                    url="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                ),
            ),
        ],
    )
