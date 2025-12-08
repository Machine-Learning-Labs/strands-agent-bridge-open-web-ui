.PHONY: help up down build logs clean restart ps test

help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

build: ## Build the agent API image
	docker-compose build

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View logs from agent API only
	docker-compose logs -f agent-api

logs-ui: ## View logs from Open Web UI only
	docker-compose logs -f open-webui

clean: ## Remove all containers, volumes, and images
	docker-compose down -v
	docker-compose rm -f

restart: ## Restart all services
	docker-compose restart

ps: ## Show running containers
	docker-compose ps

test: ## Test the API endpoint
	@echo "Testing API health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@echo "\nTesting models endpoint..."
	@curl -s http://localhost:8000/v1/models | python3 -m json.tool

shell-api: ## Open shell in agent API container
	docker-compose exec agent-api /bin/bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d openwebui
