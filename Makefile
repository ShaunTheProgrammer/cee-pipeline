# Makefile for CEE Pipeline Docker Operations

.PHONY: help build up down restart logs shell db-shell clean test backup restore

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)CEE Pipeline Docker Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Setup and Build
setup: ## Initial setup (copy env file)
	@echo "$(GREEN)Setting up environment...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.docker .env; \
		echo "$(YELLOW)⚠️  Created .env file. Please edit it and add your API keys!$(NC)"; \
	else \
		echo "$(GREEN)✓ .env file already exists$(NC)"; \
	fi

build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build

build-no-cache: ## Build Docker images without cache
	@echo "$(GREEN)Building Docker images (no cache)...$(NC)"
	docker-compose build --no-cache

# Service Management
up: ## Start all services
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "Dashboard: http://localhost/dashboard/dashboard.html"
	@echo "API Docs:  http://localhost:8000/docs"

down: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

rebuild: down build up ## Rebuild and restart all services

# Logs and Monitoring
logs: ## Show logs from all services
	docker-compose logs -f

logs-api: ## Show API logs
	docker-compose logs -f api

logs-db: ## Show database logs
	docker-compose logs -f postgres

logs-nginx: ## Show nginx logs
	docker-compose logs -f nginx

status: ## Show service status
	@echo "$(GREEN)Service Status:$(NC)"
	docker-compose ps

stats: ## Show resource usage
	docker stats

# Shell Access
shell: ## Access API container shell
	docker-compose exec api /bin/bash

shell-db: ## Access PostgreSQL shell
	docker-compose exec postgres psql -U cee_user -d cee_pipeline

shell-redis: ## Access Redis CLI
	docker-compose exec redis redis-cli

# Database Operations
db-backup: ## Backup database
	@echo "$(GREEN)Backing up database...$(NC)"
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U cee_user cee_pipeline > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up to backups/$(NC)"

db-restore: ## Restore database (usage: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Please specify FILE=path/to/backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	docker-compose exec -T postgres psql -U cee_user cee_pipeline < $(FILE)
	@echo "$(GREEN)✓ Database restored$(NC)"

db-reset: ## Reset database (⚠️  deletes all data)
	@echo "$(RED)⚠️  This will delete ALL data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec postgres psql -U cee_user -d cee_pipeline -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		docker-compose restart api; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	fi

# Testing
test: ## Run tests in container
	docker-compose exec api pytest cee_pipeline/tests/ -v

test-local: ## Run tests locally
	pytest cee_pipeline/tests/ -v

# Cleanup
clean: ## Remove stopped containers
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker-compose down
	docker system prune -f
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: ## Remove all containers, volumes, and images (⚠️  deletes all data)
	@echo "$(RED)⚠️  This will delete ALL data and images!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker system prune -a -f; \
		echo "$(GREEN)✓ Complete cleanup done$(NC)"; \
	fi

# Development
dev: ## Start in development mode with live reload
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Build and start in development mode
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Production
prod: ## Start in production mode
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health Checks
health: ## Check health of all services
	@echo "$(GREEN)Checking service health...$(NC)"
	@echo "API:        $$(curl -s http://localhost:8000/ > /dev/null && echo '$(GREEN)✓ Healthy$(NC)' || echo '$(RED)✗ Unhealthy$(NC)')"
	@echo "Nginx:      $$(curl -s http://localhost/health > /dev/null && echo '$(GREEN)✓ Healthy$(NC)' || echo '$(RED)✗ Unhealthy$(NC)')"
	@echo "PostgreSQL: $$(docker-compose exec postgres pg_isready -U cee_user > /dev/null 2>&1 && echo '$(GREEN)✓ Healthy$(NC)' || echo '$(RED)✗ Unhealthy$(NC)')"
	@echo "Redis:      $$(docker-compose exec redis redis-cli ping > /dev/null 2>&1 && echo '$(GREEN)✓ Healthy$(NC)' || echo '$(RED)✗ Unhealthy$(NC)')"

# Utility
init: setup build up ## Complete initialization (setup + build + up)
	@echo "$(GREEN)🎉 CEE Pipeline is ready!$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Edit .env and add your API keys"
	@echo "  2. Run 'make restart' to apply changes"
	@echo "  3. Visit http://localhost/dashboard/dashboard.html"
	@echo ""

url: ## Show service URLs
	@echo "$(GREEN)Service URLs:$(NC)"
	@echo "  Dashboard:  http://localhost/dashboard/dashboard.html"
	@echo "  API:        http://localhost:8000"
	@echo "  API Docs:   http://localhost:8000/docs"
	@echo "  Health:     http://localhost/health"

version: ## Show Docker and Compose versions
	@docker --version
	@docker-compose --version
