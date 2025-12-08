# Strands Agents SDK with Open Web UI

A simple demonstration of integrating AWS Strands Agents SDK with Open Web UI through an OpenAI-compatible API.

## Overview

This project demonstrates how to connect a Strands Agent to Open Web UI by exposing an OpenAI-compatible API endpoint. This allows Open Web UI to interact with your custom Strands agent as if it were an OpenAI model.

## Prerequisites

This project works with either:
- **Docker** + docker-compose
- **Podman** + podman-compose

The Makefile automatically detects which container runtime you have installed.

To check which runtime will be used:
```bash
make info
```

## Quick Start

1. Copy the environment file and configure your credentials:
```bash
cp .env.example .env
```

2. Edit `.env` with your AWS credentials and other required variables.

3. Start all services:
```bash
make up
```

4. Access Open Web UI at `http://localhost:3000`

5. In Open Web UI settings, add the custom model endpoint:
   - URL: `http://agent-api:8000/v1`
   - API Key: Your configured `OPENAI_API_KEY` from `.env`

## Services

- **Open Web UI**: Web interface on port 3000
- **Agent API**: OpenAI-compatible API on port 8000
- **PostgreSQL**: Database on port 5432

## Available Commands

Run `make help` to see all available commands:

- `make up` - Start all services
- `make down` - Stop all services
- `make logs` - View logs from all services
- `make ps` - Show running containers
- `make test` - Test the API endpoints
- `make clean` - Remove all containers and volumes

## Stopping Services

```bash
make down
```

## Licence

MIT
