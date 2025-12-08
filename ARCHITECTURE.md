# Architecture Overview

## System Components

This project demonstrates the integration between Open Web UI and AWS Strands Agents SDK through an OpenAI-compatible API layer.

### Component Flow

```
┌─────────────────┐
│   Open Web UI   │  (Port 3000)
│   Web Interface │
└────────┬────────┘
         │ HTTP Requests
         │ (OpenAI API Format)
         ▼
┌─────────────────┐
│   Agent API     │  (Port 8000)
│  FastAPI Server │
│  /v1/models     │
│  /v1/chat/...   │
└────────┬────────┘
         │ Python SDK Calls
         ▼
┌─────────────────┐
│ Strands Agent   │
│    (Alfred)     │
│  Bedrock Model  │
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│  AWS Bedrock    │
│   Nova Pro v1   │
└─────────────────┘

┌─────────────────┐
│  PostgreSQL 17  │  (Port 5432)
│   Database      │  (Stores Open Web UI data)
└─────────────────┘
```

## Key Integration Points

### 1. OpenAI API Compatibility Layer (`src/api.py`)

The FastAPI application provides OpenAI-compatible endpoints:

- **GET /v1/models**: Lists available Strands agents as "models"
- **POST /v1/chat/completions**: Processes chat messages through the Strands agent
- **GET /v1/models/{model_id}**: Retrieves specific model information

### 2. Strands Agent Wrapper (`src/agent.py`)

The `AlfredAgent` class:

- Initialises a Strands Agent with AWS Bedrock model
- Configures the agent with a custom system prompt (Alfred personality)
- Provides synchronous and asynchronous invocation methods
- Handles response formatting

### 3. Request Flow

1. User sends message in Open Web UI
2. Open Web UI makes POST request to `/v1/chat/completions`
3. API extracts user message from OpenAI format
4. Message is passed to Strands Agent (Alfred)
5. Agent processes through AWS Bedrock
6. Response is formatted as OpenAI completion
7. Open Web UI displays the response

## Configuration

### Environment Variables

- **AWS Credentials**: Required for Bedrock access
- **OPENAI_API_KEY**: Used for service-to-service authentication
- **Database**: PostgreSQL connection details for Open Web UI

### Docker Networking

All services communicate through the `strands-network` bridge network:

- Services reference each other by container name
- Open Web UI connects to `http://agent-api:8000/v1`
- Agent API and Open Web UI both connect to `postgres:5432`

## Security Considerations

This is a demonstration project. For production use:

1. Implement proper API key validation
2. Add rate limiting
3. Use secrets management for credentials
4. Enable HTTPS/TLS
5. Implement proper error handling and logging
6. Add authentication and authorisation
7. Use environment-specific configurations

## Extending the System

### Adding New Agents

1. Create new agent class in `src/agent.py`
2. Register in `src/api.py` models list
3. Route requests based on model ID

### Adding Tools

Strands SDK supports tools. Example:

```python
from strands import tool

@tool
def get_weather(city: str) -> dict:
    """Get weather for a city."""
    # Implementation
    return {"status": "success", "content": [...]}

agent = Agent(tools=[get_weather])
```

### Streaming Support

To add streaming responses:

1. Enable streaming in Bedrock model
2. Implement Server-Sent Events (SSE) in API
3. Stream tokens as they arrive from Bedrock
