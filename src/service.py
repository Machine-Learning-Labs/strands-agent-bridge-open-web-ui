"""
Business logic for chat completions and message processing.
"""

import time
import uuid
import base64
import re
import requests
from typing import List, Union
from fastapi import HTTPException

from .models import (
    Message,
    TextContent,
    ImageContent,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    Usage,
)
from .agent import create_alfred_agent


class ChatService:
    """Service class handling chat completion logic and message processing."""

    def __init__(self):
        """Initialize the chat service with Alfred agent."""
        self.alfred = create_alfred_agent()

    def parse_image_url(self, image_url: str) -> bytes:
        """Parse image URL and return image bytes."""
        # Check if it's a base64 data URL
        pattern = r"^data:image/[a-z]*;base64,\s*"
        if re.match(pattern, image_url):
            image_data = re.sub(pattern, "", image_url)
            return base64.b64decode(image_data)

        # Handle HTTP URLs
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unable to fetch image from URL: {response.status_code}",
                )
        except requests.RequestException as e:
            raise HTTPException(
                status_code=400, detail=f"Error fetching image: {str(e)}"
            )

    def convert_message_to_strands_format(self, message: Message):
        """
        Convert OpenAI message to Strands format.
        Returns either a string (text only) or list of ContentBlocks (multimodal).
        """
        if isinstance(message.content, str):
            return message.content
        elif isinstance(message.content, list):
            content_blocks = []

            for part in message.content:
                if isinstance(part, TextContent):
                    content_blocks.append({"text": part.text})
                elif isinstance(part, ImageContent):
                    # Parse image and convert to Strands format
                    image_bytes = self.parse_image_url(part.image_url.url)

                    # Determine format from URL - be more flexible with format detection
                    image_format = "png"  # default

                    # Check data URL first
                    format_match = re.search(
                        r"data:image/([a-z]+);", part.image_url.url
                    )
                    if format_match:
                        image_format = format_match.group(1)
                    else:
                        # Try to get format from URL extension
                        url_format_match = re.search(
                            r"\.([a-z]+)(?:\?|$)", part.image_url.url.lower()
                        )
                        if url_format_match:
                            ext = url_format_match.group(1)
                            # Map common extensions to Strands supported formats
                            format_mapping = {
                                "jpg": "jpeg",
                                "jpeg": "jpeg",
                                "png": "png",
                                "gif": "gif",
                                "webp": "webp",
                            }
                            image_format = format_mapping.get(ext, "png")

                    # According to Strands docs, the format should be exactly as shown
                    content_blocks.append(
                        {
                            "image": {
                                "format": image_format,
                                "source": {"bytes": image_bytes},
                            }
                        }
                    )

            return content_blocks
        else:
            return str(message.content)

    def extract_text_for_tokens(self, message: Message) -> str:
        """Extract only text content for token counting."""
        if isinstance(message.content, str):
            return message.content
        elif isinstance(message.content, list):
            text_parts = []
            for part in message.content:
                if isinstance(part, TextContent):
                    text_parts.append(part.text)
            return " ".join(text_parts)
        else:
            return str(message.content)

    def estimate_token_usage(
        self, messages: List[Message], response_text: str
    ) -> Usage:
        """Estimate token usage for the conversation."""
        prompt_tokens = 0
        for msg in messages:
            text_content = self.extract_text_for_tokens(msg)
            prompt_tokens += len(text_content.split())
            # Add estimated tokens for images
            if isinstance(msg.content, list):
                image_count = sum(
                    1 for part in msg.content if isinstance(part, ImageContent)
                )
                prompt_tokens += image_count * 85  # Rough estimate for image processing

        completion_tokens = len(response_text.split()) if response_text else 0

        return Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    async def process_chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Process a chat completion request through the Alfred agent.

        Args:
            request: Chat completion request with messages

        Returns:
            Chat completion response with agent's reply
        """
        try:
            # Extract the last user message
            user_messages = [msg for msg in request.messages if msg.role == "user"]
            if not user_messages:
                raise HTTPException(status_code=400, detail="No user message found")

            # Convert message to Strands format (handles both text and images)
            last_message_content = self.convert_message_to_strands_format(
                user_messages[-1]
            )

            # Process through Alfred agent
            response_text = await self.alfred.ainvoke(last_message_content)

            # Estimate token usage
            usage = self.estimate_token_usage(request.messages, response_text)

            # Build OpenAI-compatible response
            return ChatCompletionResponse(
                id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
                created=int(time.time()),
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=Message(role="assistant", content=response_text),
                        finish_reason="stop",
                    )
                ],
                usage=usage,
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing request: {str(e)}"
            )
