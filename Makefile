# Variables
PYTHON = poetry run python
POETRY = poetry

# Help: Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  install          Install dependencies"
	@echo "  format           Run code formatters (black, isort)"
	@echo "  lint             Run linters (flake8)"
	@echo "  test             Run tests with pytest"
	@echo "  check            Run format check and linting"
	@echo "  clean            Clean up cache files and artifacts"

# Install dependencies
.PHONY: install
install:
	$(POETRY) install

# Run code formatters
.PHONY: format
format:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .

# Run linters
.PHONY: lint
lint:
	$(PYTHON) -m flake8 .

# Run tests
.PHONY: test
test:
	$(PYTHON) -m pytest

# Check formatting and linting
.PHONY: check
check:
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check .
	$(PYTHON) -m flake8 .

# Clean up cache and artifacts
.PHONY: clean
clean:
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
