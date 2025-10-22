.PHONY: help build up down restart logs clean ps

help: ## Show this help message
	@echo "RentRate Docker Commands"
	@echo "========================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker compose build

up: ## Start all services
	docker compose up

up-build: ## Build and start all services
	docker compose up --build

up-d: ## Start all services in detached mode
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Show logs from all services
	docker compose logs -f

logs-backend: ## Show backend logs
	docker compose logs -f backend

logs-frontend: ## Show frontend logs
	docker compose logs -f frontend

logs-db: ## Show database logs
	docker compose logs -f db

logs-translate: ## Show translation service logs (if self-hosted)
	@echo "Note: Translation service is not running locally by default."
	@echo "The project uses the public LibreTranslate API."
	@echo "If you've enabled local LibreTranslate, uncomment the service in docker-compose.yml"
	@docker compose logs -f libretranslate 2>/dev/null || echo "LibreTranslate service not running"

ps: ## List running containers
	docker compose ps

clean: ## Stop and remove all containers, networks, and volumes
	docker compose down -v

shell-backend: ## Open shell in backend container
	docker compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend /bin/sh

shell-db: ## Open PostgreSQL shell
	docker compose exec db psql -U rentrate -d rentrate
