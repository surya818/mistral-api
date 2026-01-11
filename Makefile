.PHONY: help install generate-client test test-e2e lint format typecheck clean setup

# Default target
help:
	@echo "Available targets:"
	@echo "  setup           - Full setup: install deps + generate client"
	@echo "  install         - Install dependencies"
	@echo "  generate-client - Generate API client from OpenAPI spec"
	@echo "  test            - Run all tests"
	@echo "  test-e2e        - Run e2e tests only"
	@echo "  lint            - Run linter (ruff)"
	@echo "  format          - Format code (ruff)"
	@echo "  typecheck       - Run type checker (mypy)"
	@echo "  clean           - Remove generated files and caches"

# Full setup for new clone
setup: install generate-client
	@echo "Setup complete. Run 'make test' to verify."

# Install dependencies
install:
	uv sync --extra dev

# Generate API client from OpenAPI spec
generate-client:
	@./scripts/generate_client.sh

# Run all tests
test: generate-client
	uv run pytest tests/ -v

# Run e2e tests only
test-e2e: generate-client
	uv run pytest tests/e2e -v --log-cli-level=INFO

# Run linter
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format .
	uv run ruff check --fix .

# Run type checker
typecheck:
	uv run mypy src/ tests/ --ignore-missing-imports

# Clean generated files and caches
clean:
	rm -rf src/generated_client/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
