#!/bin/bash

# Test script for Alfred Butler API
# Make sure the API server is running on localhost:8000

API_BASE="http://localhost:8000"

echo "🧪 Testing Alfred Butler API"
echo "================================"

# Test 1: List available models
echo
echo "📋 1. Listing available models..."
curl -s "${API_BASE}/v1/models" | jq '.'

# Test 2: Simple text chat
echo
echo "💬 2. Simple text chat - Hello World..."
curl -s "${API_BASE}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alfred-butler",
    "messages": [
      {
        "role": "user",
        "content": "Hello Alfred, how are you today?"
      }
    ]
  }' | jq '.choices[0].message.content'

# Test 3: Streaming chat
echo
echo "🌊 3. Streaming chat - Hello World..."
curl -N "${API_BASE}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alfred-butler",
    "stream": true,
    "messages": [
      {
        "role": "user", 
        "content": "Tell me a short joke, Alfred"
      }
    ]
  }'

echo
echo

# Test 4: Multimodal - Image analysis
echo "🖼️  4. Multimodal - Image analysis..."
curl -s "${API_BASE}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alfred-butler",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What do you see in this image? Describe it in detail."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Th%C3%A9%C3%A2tre_D%E2%80%99op%C3%A9ra_Spatial.png"
            }
          }
        ]
      }
    ]
  }' | jq '.choices[0].message.content'

# Test 5: Health check
echo
echo "❤️  5. Health check..."
curl -s "${API_BASE}/health" | jq '.'

# Test 6: Root endpoint info
echo
echo "ℹ️  6. API information..."
curl -s "${API_BASE}/" | jq '.'

echo
echo "✅ All tests completed!"
echo
echo "💡 Tips:"
echo "   - Make sure jq is installed for pretty JSON output"
echo "   - Start the API server with: uvicorn src.api:app --host 0.0.0.0 --port 8000"
echo "   - Or use Docker: make up"