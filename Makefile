.PHONY: help install dev test lint format clean start stop restart status logs ps down migrate migrate-upgrade migrate-downgrade migrate-current migrate-history

COMPOSE_DIR := deployment/docker-compose

help:
	@echo "Available targets:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development environment"
	@echo "  make start      - Start QAtron services (or: make start SVC=control-plane)"
	@echo "  make stop       - Stop QAtron services (or: make stop SVC=control-plane)"
	@echo "  make restart    - Restart QAtron services"
	@echo "  make status     - Show service status"
	@echo "  make logs       - Show service logs (use SVC=name for one service)"
	@echo "  make ps         - List running containers"
	@echo "  make down       - Stop and remove containers"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make migrate    - Run database migrations (upgrade to head)"
	@echo "  make migrate-upgrade - Upgrade database to head"
	@echo "  make migrate-downgrade - Downgrade database by one revision"
	@echo "  make migrate-current - Show current migration revision"
	@echo "  make migrate-history - Show migration history"

install:
	@echo "Installing dependencies..."
	cd services/control-plane && poetry install
	cd services/orchestrator && poetry install
	cd services/worker && poetry install
	cd services/reporting && poetry install
	cd services/data-manager && poetry install
	cd framework/qatron-python && poetry install
	cd cli/qatron-cli && poetry install
	cd services/board && npm install

dev:
	docker compose -f $(COMPOSE_DIR)/docker-compose.yml up -d

start:
	./$(COMPOSE_DIR)/manage.sh start $(SVC)

stop:
	./$(COMPOSE_DIR)/manage.sh stop $(SVC)

restart:
	./$(COMPOSE_DIR)/manage.sh restart $(SVC)

status:
	./$(COMPOSE_DIR)/manage.sh status

logs:
	./$(COMPOSE_DIR)/manage.sh logs $(SVC)

ps:
	./$(COMPOSE_DIR)/manage.sh ps

down:
	./$(COMPOSE_DIR)/manage.sh down

test:
	pytest

lint:
	ruff check .
	mypy .

format:
	black .
	ruff check --fix .

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +

migrate:
	@echo "Running database migrations..."
	docker compose -f $(COMPOSE_DIR)/docker-compose.yml exec -T control-plane alembic upgrade head

migrate-upgrade:
	@echo "Upgrading database to head..."
	docker compose -f $(COMPOSE_DIR)/docker-compose.yml exec -T control-plane alembic upgrade head

migrate-downgrade:
	@echo "Downgrading database by one revision..."
	docker compose -f $(COMPOSE_DIR)/docker-compose.yml exec -T control-plane alembic downgrade -1

migrate-current:
	@echo "Current migration revision:"
	docker compose -f $(COMPOSE_DIR)/docker-compose.yml exec -T control-plane alembic current

migrate-history:
	@echo "Migration history:"
	docker compose -f $(COMPOSE_DIR)/docker-compose.yml exec -T control-plane alembic history
