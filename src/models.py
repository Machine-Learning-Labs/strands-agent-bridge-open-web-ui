"""
Pydantic models for OpenAI API compatibility.
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ImageUrl(BaseModel):
    """Image URL structure for multimodal content."""

    url: str
    detail: Optional[str] = "auto"


class TextContent(BaseModel):
    """Text content block."""

    type: str = "text"
    text: str


class ImageContent(BaseModel):
    """Image content block."""

    type: str = "image_url"
    image_url: ImageUrl


class Message(BaseModel):
    """Chat message structure."""

    role: str
    content: Union[str, List[Union[TextContent, ImageContent]]]


class ChatCompletionRequest(BaseModel):
    """OpenAI chat completion request format."""

    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class ChatCompletionChoice(BaseModel):
    """Individual completion choice."""

    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """OpenAI chat completion response format."""

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class Model(BaseModel):
    """Model information structure."""

    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelList(BaseModel):
    """List of available models."""

    object: str = "list"
    data: List[Model]
