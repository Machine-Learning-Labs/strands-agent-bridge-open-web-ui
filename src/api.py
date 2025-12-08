"""
OpenAI-compatible API for Strands Agent integration with Open Web UI.

This module provides an OpenAI-compatible REST API that allows Open Web UI
to interact with Strands agents as if they were OpenAI models.
"""
import time
import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agent import create_alfred_agent


# Pydantic models for OpenAI API compatibility
class Message(BaseModel):
    """Chat message structure."""
    role: str
    content: str


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


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Strands Agent OpenAI-Compatible API",
        "version": "1.0.0",
        "agent": "Alfred - The Butler",
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
            ),
            Model(
                id="strands-agent",
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
        
        last_message = user_messages[-1].content
        
        # Process through Alfred agent
        response_text = await alfred.ainvoke(last_message)
        
        # Estimate token usage (simplified)
        prompt_tokens = sum(len(msg.content.split()) for msg in request.messages)
        completion_tokens = len(response_text.split())
        
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
    if model_id in ["alfred-butler", "strands-agent"]:
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
