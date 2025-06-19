# Makefile for affiliate automation project

.PHONY: help install dev-install clean test lint format pre-commit check run

help:
	@echo "Available commands:"
	@echo "  make install       Install production dependencies"
	@echo "  make dev-install   Install all dependencies including dev"
	@echo "  make clean         Clean up cache files"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linting"
	@echo "  make format        Format code"
	@echo "  make pre-commit    Run pre-commit hooks"
	@echo "  make check         Run all checks (lint, test, pre-commit)"
	@echo "  make run           Run the application"

install:
	poetry install --no-dev

dev-install:
	poetry install
	pre-commit install

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf build/ dist/

test:
	poetry run pytest -v

test-cov:
	poetry run pytest --cov=src --cov-report=html --cov-report=term

lint:
	poetry run flake8 src/ tests/
	poetry run bandit -r src/ -ll

format:
	poetry run isort src/ tests/
	poetry run black src/ tests/

pre-commit:
	poetry run pre-commit run --all-files

check: format lint test

run:
	poetry run python main.py

# Development shortcuts
search:
	poetry run python main.py search -q "$(q)"

compare:
	poetry run python main.py compare -q "$(q)"

deals:
	poetry run python main.py deals

# Docker commands (if needed in future)
docker-build:
	docker build -t affiliate-automation .

docker-run:
	docker run -it --rm affiliate-automation
