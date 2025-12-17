.PHONY: help install install-dev test lint format clean run ingest

help:
	@echo "GhostVault Development Commands"
	@echo ""
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linters (flake8, black, isort)"
	@echo "  make format        - Format code (black, isort)"
	@echo "  make clean         - Clean build artifacts and caches"
	@echo "  make run           - Run the Chainlit app"
	@echo "  make ingest        - Run the ingestion service"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	black --check .
	isort --check-only .

format:
	black .
	isort .

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build

run:
	chainlit run app.py

ingest:
	python ingest.py

