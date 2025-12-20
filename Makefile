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

# Test configuration
TEST_TYPE ?= all
TEST_SCRIPT = ./bin/run-tests.sh

.PHONY: help up down build logs clean restart ps test info
.PHONY: test-unit test-integration test-performance test-contract test-coverage test-fast
.PHONY: install-dev lint format quality clean-test

help: ## Display this help message
	@echo "Available commands:"
	@echo ""
	@echo "🐳 Container Management:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*Container.*$$|^[a-zA-Z_-]+:.*?## .*service.*$$|^[a-zA-Z_-]+:.*?## .*image.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧪 Testing:"
	@grep -E '^test.*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Development:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*dev.*$$|^[a-zA-Z_-]+:.*?## .*lint.*$$|^[a-zA-Z_-]+:.*?## .*format.*$$|^[a-zA-Z_-]+:.*?## .*quality.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "ℹ️  Other:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v -E 'Container|service|image|test|dev|lint|format|quality' | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

info: ## Show detected container runtime
	@echo "Using: $(RUNTIME_NAME)"
	@echo "Command: $(COMPOSE_CMD)"
	@$(CONTAINER_RUNTIME) --version

up: ## Start all Container services
	$(COMPOSE_CMD) up -d

down: ## Stop all Container services
	$(COMPOSE_CMD) down

build: ## Build the agent API Container image
	$(COMPOSE_CMD) build

logs: ## View logs from all Container services
	$(COMPOSE_CMD) logs -f

logs-api: ## View logs from agent API Container only
	$(COMPOSE_CMD) logs -f agent-api

logs-ui: ## View logs from Open Web UI Container only
	$(COMPOSE_CMD) logs -f open-webui

clean: ## Remove all Container containers, volumes, and images
	$(COMPOSE_CMD) down -v
	$(COMPOSE_CMD) rm -f

restart: ## Restart all Container services
	$(COMPOSE_CMD) restart

ps: ## Show running Container containers
	$(COMPOSE_CMD) ps

# Testing targets
test: ## Run tests (TEST_TYPE=all|unit|integration|coverage)
	@$(TEST_SCRIPT) $(TEST_TYPE)

test-unit: ## Run unit tests only
	@$(TEST_SCRIPT) unit

test-integration: ## Run integration tests only
	@$(TEST_SCRIPT) integration

test-coverage: ## Run tests with coverage report
	@$(TEST_SCRIPT) coverage

# Development targets
install-dev: ## Install development dependencies
	pip install -r requirements.dev.txt

lint: ## Run code linting
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src tests; \
	else \
		echo "⚠️  flake8 not found. Run 'make install-dev' first"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		mypy src; \
	else \
		echo "⚠️  mypy not found. Run 'make install-dev' first"; \
	fi

format: ## Format code with black and isort
	@if command -v black >/dev/null 2>&1; then \
		black src tests; \
	else \
		echo "⚠️  black not found. Run 'make install-dev' first"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort src tests; \
	else \
		echo "⚠️  isort not found. Run 'make install-dev' first"; \
	fi

quality: ## Run format, lint, and unit tests
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test-unit

clean-test: ## Clean test artifacts
	rm -rf .pytest_cache htmlcov .coverage coverage.xml test-report.html
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# API testing (for running services)
test-api: ## Test the running API endpoint
	@echo "Testing API health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@echo "\nTesting models endpoint..."
	@curl -s http://localhost:8000/v1/models | python3 -m json.tool

shell-api: ## Open shell in agent API Container
	$(COMPOSE_CMD) exec agent-api /bin/bash

shell-db: ## Open PostgreSQL shell in Container
	$(COMPOSE_CMD) exec postgres psql -U postgres -d openwebui