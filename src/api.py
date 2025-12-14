"""
OpenAI-compatible API for Strands Agent integration with Open Web UI.

This module provides an OpenAI-compatible REST API that allows Open Web UI
to interact with Strands agents as if they were OpenAI models.
"""
import time
import uuid
import base64
import re
import requests
from typing import List, Optional, Dict, Any, Union
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agent import create_alfred_agent


# Pydantic models for OpenAI API compatibility
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


# Initialise FastAPI application
app = FastAPI(
    title="Strands Agent OpenAI-Compatible API",
    description="OpenAI-compatible API for Strands Agents integration with Open Web UI",
    version="1.0.0"
)

# Initialise Alfred agent
alfred = create_alfred_agent()


def parse_image_url(image_url: str) -> bytes:
    """Parse image URL and return image bytes."""
    # Check if it's a base64 data URL
    pattern = r"^data:image/[a-z]*;base64,\s*"
    if re.match(pattern, image_url):
        image_data = re.sub(pattern, "", image_url)
        return base64.b64decode(image_data)
    
    # Handle HTTP URLs
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(image_url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unable to fetch image from URL: {response.status_code}"
            )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error fetching image: {str(e)}"
        )


def convert_message_to_strands_format(message: Message):
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
                image_bytes = parse_image_url(part.image_url.url)
                
                # Determine format from URL - be more flexible with format detection
                image_format = "png"  # default
                
                # Check data URL first
                format_match = re.search(r"data:image/([a-z]+);", part.image_url.url)
                if format_match:
                    image_format = format_match.group(1)
                else:
                    # Try to get format from URL extension
                    url_format_match = re.search(r"\.([a-z]+)(?:\?|$)", part.image_url.url.lower())
                    if url_format_match:
                        ext = url_format_match.group(1)
                        # Map common extensions to Strands supported formats
                        format_mapping = {
                            "jpg": "jpeg",
                            "jpeg": "jpeg", 
                            "png": "png",
                            "gif": "gif",
                            "webp": "webp"
                        }
                        image_format = format_mapping.get(ext, "png")
                
                # According to Strands docs, the format should be exactly as shown
                content_blocks.append({
                    "image": {
                        "format": image_format,
                        "source": {"bytes": image_bytes}
                    }
                })
        
        return content_blocks
    else:
        return str(message.content)


def extract_text_for_tokens(message: Message) -> str:
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


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Alfred Butler - Multimodal AI Assistant",
        "version": "1.0.0",
        "model": "alfred-butler",
        "features": ["text", "images", "multimodal"],
        "endpoints": {
            "models": "/v1/models",
            "chat": "/v1/chat/completions"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "alfred"}


@app.get("/v1/models")
async def list_models() -> ModelList:
    """
    List available models (OpenAI-compatible endpoint).
    
    Returns a list of available models that Open Web UI can use.
    """
    return ModelList(
        data=[
            Model(
                id="alfred-butler",
                created=int(time.time()),
                owned_by="strands-agents"
            )
        ]
    )


@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None)
) -> ChatCompletionResponse:
    """
    Create a chat completion (OpenAI-compatible endpoint).
    
    This endpoint receives chat messages from Open Web UI and processes them
    through the Strands agent, returning responses in OpenAI format.
    
    Args:
        request: Chat completion request with messages
        authorization: Optional API key header
        
    Returns:
        Chat completion response with agent's reply
    """
    try:
        # Validate API key if provided (basic security)
        if authorization:
            # In production, implement proper API key validation
            pass
        
        # Extract the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Convert message to Strands format (handles both text and images)
        last_message_content = convert_message_to_strands_format(user_messages[-1])
        
        # Process through Alfred agent
        response_text = await alfred.ainvoke(last_message_content)
        
        # Estimate token usage (simplified)
        prompt_tokens = 0
        for msg in request.messages:
            text_content = extract_text_for_tokens(msg)
            prompt_tokens += len(text_content.split())
            # Add estimated tokens for images
            if isinstance(msg.content, list):
                image_count = sum(1 for part in msg.content if isinstance(part, ImageContent))
                prompt_tokens += image_count * 85  # Rough estimate for image processing
        
        completion_tokens = len(response_text.split()) if response_text else 0
        
        # Build OpenAI-compatible response
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=response_text
                    ),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/v1/models/{model_id}")
async def get_model(model_id: str) -> Model:
    """
    Retrieve specific model information.
    
    Args:
        model_id: Model identifier
        
    Returns:
        Model information
    """
    if model_id == "alfred-butler":
        return Model(
            id=model_id,
            created=int(time.time()),
            owned_by="strands-agents"
        )
    else:
        raise HTTPException(status_code=404, detail="Model not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
