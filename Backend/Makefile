# Makefile for Django project

# Variables
MANAGE_PY = python manage.py
DOCKER_COMPOSE = docker-compose

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  install           Install dependencies"
	@echo "  migrate           Run database migrations"
	@echo "  runserver         Start the development server"
	@echo "  test              Run tests"
	@echo "  coverage          Run tests with coverage"
	@echo "  shell             Open Django shell"
	@echo "  createsuperuser   Create a superuser"
	@echo "  collectstatic     Collect static files"
	@echo "  docker-up         Start services with Docker Compose"
	@echo "  docker-down       Stop services with Docker Compose"
	@echo "  docker-logs       View logs from Docker containers"
	@echo "  docker-shell      Open shell in web container"
	@echo "  clean             Remove Python cache files"
	@echo "  help              Show this help message"

# Install dependencies
.PHONY: install
install:
	pip install -r requirements/development.txt

# Run migrations
.PHONY: migrate
migrate:
	$(MANAGE_PY) migrate

# Start development server
.PHONY: runserver
runserver:
	$(MANAGE_PY) runserver

# Run tests
.PHONY: test
test:
	$(MANAGE_PY) test

# Run tests with coverage
.PHONY: coverage
coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing

# Open Django shell
.PHONY: shell
shell:
	$(MANAGE_PY) shell

# Create superuser
.PHONY: createsuperuser
createsuperuser:
	$(MANAGE_PY) createsuperuser

# Collect static files
.PHONY: collectstatic
collectstatic:
	$(MANAGE_PY) collectstatic --noinput

# Docker Compose commands
.PHONY: docker-up
docker-up:
	$(DOCKER_COMPOSE) up -d

.PHONY: docker-down
docker-down:
	$(DOCKER_COMPOSE) down

.PHONY: docker-logs
docker-logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: docker-shell
docker-shell:
	$(DOCKER_COMPOSE) exec web bash

# Clean Python cache files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml

# First time setup
.PHONY: setup
setup: install migrate collectstatic
	@echo "Setup complete! Run 'make createsuperuser' to create an admin user."