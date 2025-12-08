# Detect container runtime (Docker or Podman)
CONTAINER_RUNTIME := $(shell command -v podman 2> /dev/null)
ifdef CONTAINER_RUNTIME
    COMPOSE_CMD = podman-compose
    RUNTIME_NAME = Podman
else
    CONTAINER_RUNTIME := $(shell command -v docker 2> /dev/null)
    ifdef CONTAINER_RUNTIME
        COMPOSE_CMD = docker-compose
        RUNTIME_NAME = Docker
    else
        $(error Neither Docker nor Podman found. Please install one of them.)
    endif
endif

.PHONY: help up down build logs clean restart ps test info

help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

info: ## Show detected container runtime
	@echo "Using: $(RUNTIME_NAME)"
	@echo "Command: $(COMPOSE_CMD)"
	@$(CONTAINER_RUNTIME) --version

up: ## Start all services
	$(COMPOSE_CMD) up -d

down: ## Stop all services
	$(COMPOSE_CMD) down

build: ## Build the agent API image
	$(COMPOSE_CMD) build

logs: ## View logs from all services
	$(COMPOSE_CMD) logs -f

logs-api: ## View logs from agent API only
	$(COMPOSE_CMD) logs -f agent-api

logs-ui: ## View logs from Open Web UI only
	$(COMPOSE_CMD) logs -f open-webui

clean: ## Remove all containers, volumes, and images
	$(COMPOSE_CMD) down -v
	$(COMPOSE_CMD) rm -f

restart: ## Restart all services
	$(COMPOSE_CMD) restart

ps: ## Show running containers
	$(COMPOSE_CMD) ps

test: ## Test the API endpoint
	@echo "Testing API health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@echo "\nTesting models endpoint..."
	@curl -s http://localhost:8000/v1/models | python3 -m json.tool

shell-api: ## Open shell in agent API container
	$(COMPOSE_CMD) exec agent-api /bin/bash

shell-db: ## Open PostgreSQL shell
	$(COMPOSE_CMD) exec postgres psql -U postgres -d openwebui
