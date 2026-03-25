.PHONY: help dev prod prod-traefik prod-traefik-down prod-traefik-logs down logs migrate seed gen-key

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development stack (with hot reload, MailHog, MinIO)
	@cp -n .env.example .env.dev 2>/dev/null || true
	docker compose -f docker-compose.dev.yml up --build

down: ## Stop all containers
	docker compose -f docker-compose.dev.yml down

down-v: ## Stop all containers and remove volumes
	docker compose -f docker-compose.dev.yml down -v

prod: ## Start production stack
	docker compose up --build -d

prod-down: ## Stop production stack
	docker compose down

prod-traefik: ## Start production stack with Traefik (requires .env.prod)
	docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d

prod-traefik-down: ## Stop Traefik production stack
	docker compose -f docker-compose.prod.yml --env-file .env.prod down

prod-traefik-logs: ## Tail logs from Traefik production stack
	docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f

logs: ## Tail logs from all dev services
	docker compose -f docker-compose.dev.yml logs -f

logs-be: ## Tail backend logs
	docker compose -f docker-compose.dev.yml logs -f backend

logs-fe: ## Tail frontend logs
	docker compose -f docker-compose.dev.yml logs -f frontend

logs-worker: ## Tail worker logs
	docker compose -f docker-compose.dev.yml logs -f worker

migrate: ## Run database migrations (inside running backend container)
	docker compose -f docker-compose.dev.yml exec backend alembic upgrade head

gen-key: ## Generate a Fernet encryption key for TOTP_ENCRYPTION_KEY
	@python3 -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

shell-be: ## Open a shell in the backend container
	docker compose -f docker-compose.dev.yml exec backend bash

shell-db: ## Open psql in the database container
	docker compose -f docker-compose.dev.yml exec db psql -U postgres -d myapp

mailhog: ## Open MailHog UI
	@open http://localhost:8025 || xdg-open http://localhost:8025

minio: ## Open MinIO console
	@open http://localhost:9001 || xdg-open http://localhost:9001

redis-ui: ## Open Redis Commander UI
	@open http://localhost:8081 || xdg-open http://localhost:8081

docs: ## Open API docs (Swagger)
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs
