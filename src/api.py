"""
OpenAI-compatible REST API endpoints for Strands Agent integration with Open Web UI.
"""
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, Header

from .models import ChatCompletionRequest, ChatCompletionResponse, ModelList, Model
from .service import ChatService


# Initialize FastAPI application
app = FastAPI(
    title="Strands Agent OpenAI-Compatible API",
    description="OpenAI-compatible API for Strands Agents integration with Open Web UI",
    version="1.0.0"
)

# Initialize chat service
chat_service = ChatService()


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
    # Validate API key if provided (basic security)
    if authorization:
        # In production, implement proper API key validation
        pass
    
    # Process through chat service
    return await chat_service.process_chat_completion(request)


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
