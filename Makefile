# Bluetooth Manager Makefile

# Variables
HOST_IP ?= $(shell ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")
CLIENT_NAME ?= $(shell hostname)

# Colors for output
GREEN = \033[0;32m
BLUE = \033[0;34m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help setup-docker setup-native host-docker client-docker host client clean status

help: ## Show this help message
	@echo "$(BLUE)🔵 Bluetooth Manager for Two Macs$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Usage examples:$(NC)"
	@echo "  make setup-docker          # Setup Docker environment"
	@echo "  make host-docker           # Start host with Docker"
	@echo "  make client-docker HOST_IP=192.168.1.100  # Start client with Docker"
	@echo "  make host                  # Start host with Python"
	@echo "  make client HOST_IP=192.168.1.100         # Start client with Python"

setup-docker: ## Setup Docker environment
	@echo "$(BLUE)🐳 Setting up Docker environment...$(NC)"
	@./scripts/setup-docker.sh

setup-native: ## Setup native Python environment  
	@echo "$(BLUE)🐍 Setting up native Python environment...$(NC)"
	@./scripts/setup-native.sh

host-docker: ## Start host server with Docker
	@echo "$(GREEN)🚀 Starting host server with Docker...$(NC)"
	@echo "$(YELLOW)📱 Access from your phone: http://$(HOST_IP):5000$(NC)"
	@./scripts/start-host-docker.sh

client-docker: ## Start client with Docker (requires HOST_IP)
	@if [ -z "$(HOST_IP)" ] || [ "$(HOST_IP)" = "localhost" ]; then \
		echo "$(RED)❌ Please provide HOST_IP: make client-docker HOST_IP=192.168.1.100$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🔌 Starting client with Docker...$(NC)"
	@echo "$(YELLOW)🎯 Connecting to: $(HOST_IP)$(NC)"
	@./scripts/start-client-docker.sh $(HOST_IP) $(CLIENT_NAME)

host: ## Start host server with Python
	@echo "$(GREEN)🚀 Starting host server with Python...$(NC)"
	@echo "$(YELLOW)📱 Access from your phone: http://$(HOST_IP):5000$(NC)"
	@./scripts/start-host.sh

client: ## Start client with Python (requires HOST_IP)
	@if [ -z "$(HOST_IP)" ] || [ "$(HOST_IP)" = "localhost" ]; then \
		echo "$(RED)❌ Please provide HOST_IP: make client HOST_IP=192.168.1.100$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🔌 Starting client with Python...$(NC)"
	@echo "$(YELLOW)🎯 Connecting to: $(HOST_IP)$(NC)"
	@./scripts/start-client.sh $(HOST_IP) $(CLIENT_NAME)

clean: ## Clean up Docker containers and images
	@echo "$(YELLOW)🧹 Cleaning up Docker containers...$(NC)"
	@docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
	@docker-compose -f docker/docker-compose.client.yml down 2>/dev/null || true
	@docker system prune -f
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

status: ## Show current system status
	@echo "$(BLUE)📊 System Status$(NC)"
	@echo "$(YELLOW)Local IP:$(NC) $(HOST_IP)"
	@echo "$(YELLOW)Hostname:$(NC) $(CLIENT_NAME)"
	@echo "$(YELLOW)Bluetooth:$(NC) $(shell blueutil -p 2>/dev/null && echo 'ON' || echo 'OFF/Unknown')"
	@echo "$(YELLOW)Docker:$(NC) $(shell docker --version 2>/dev/null || echo 'Not installed')"
	@echo "$(YELLOW)BlueUtil:$(NC) $(shell blueutil --version 2>/dev/null || echo 'Not installed')"

build: ## Build Docker images
	@echo "$(BLUE)🏗️  Building Docker images...$(NC)"
	@docker-compose -f docker/docker-compose.yml build
	@docker-compose -f docker/docker-compose.client.yml build
	@echo "$(GREEN)✅ Images built successfully$(NC)"
