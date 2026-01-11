# Mistral API Test Automation

A production-ready Python API test automation framework for the [Mistral AI API](https://docs.mistral.ai/), built with industry best practices.

## Features

- **Auto-generated API Client**: Type-safe Python client generated from OpenAPI spec
- **Modern Python Stack**: Python 3.11+, async/await, type hints
- **Industry-standard Tooling**: uv, pytest, ruff, mypy, pre-commit
- **CI/CD Ready**: GitHub Actions workflows for testing and client regeneration
- **E2E Testing**: Real API workflow tests with request/response logging

## Project Structure

```
mistral-api/
├── .github/workflows/      # CI/CD pipelines
│   ├── ci.yml              # Main CI (lint, type-check, e2e tests)
│   ├── e2e-manual.yml      # Manual E2E test trigger
│   └── generate-client.yml # Auto-regenerate API client
├── src/
│   └── generated_client/   # Auto-generated API client (git-ignored)
├── tests/
│   ├── conftest.py         # Shared fixtures & API logging
│   └── e2e/                # End-to-end workflow tests
├── specs/
│   └── openapi.yaml        # Mistral OpenAPI specification
├── scripts/
│   └── generate_client.sh  # Client generation script
├── Makefile                # Common commands
├── pyproject.toml          # Project config & dependencies
└── .pre-commit-config.yaml # Git hooks
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) - Modern Python package manager
- Mistral API key ([get one here](https://console.mistral.ai/))

### Installation

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd mistral-api
   make setup
   ```

   This will:
   - Install all dependencies
   - Generate the API client from the OpenAPI spec

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```
   MISTRAL_API_KEY=your-api-key-here
   MISTRAL_BASE_URL=https://api.mistral.ai
   ```

4. **Run tests**:
   ```bash
   make test-e2e
   ```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Full setup: install deps + generate client |
| `make install` | Install dependencies only |
| `make generate-client` | Regenerate API client from OpenAPI spec |
| `make test` | Run all tests |
| `make test-e2e` | Run E2E tests with API logging |
| `make lint` | Run ruff linter |
| `make format` | Format code with ruff |
| `make typecheck` | Run mypy type checker |
| `make clean` | Remove generated files and caches |

## Running Tests

### Basic Usage

```bash
# Run all E2E tests with logging
make test-e2e

# Run all tests
make test

# Run specific test file
uv run pytest tests/e2e/test_models.py -v

# Run with verbose API logging
uv run pytest tests/e2e -v --log-cli-level=INFO
```

### Advanced Options

```bash
# Run tests in parallel
uv run pytest tests/e2e -n auto

# Run with timeout
uv run pytest tests/e2e --timeout=300

# Run specific test markers
uv run pytest tests/e2e -m "smoke"

# Generate Allure report
uv run pytest tests/e2e --alluredir=allure-results
```

## Generated API Client

The API client is auto-generated from the OpenAPI spec and provides:
- **Type safety**: Full type hints for all requests/responses
- **IDE support**: Autocomplete for methods and fields
- **Auto-sync**: Regenerate when API spec changes

### Usage in Tests

```python
from mistral_ai_api_client import AuthenticatedClient
from mistral_ai_api_client.api.models import (
    list_models_v1_models_get,
    retrieve_model_v1_models_model_id_get,
)
from mistral_ai_api_client.models import BaseModelCard, ModelList

async def test_list_models(api_client: AuthenticatedClient):
    response = await list_models_v1_models_get.asyncio_detailed(
        client=api_client,
    )
    assert response.status_code == HTTPStatus.OK
    model_list = response.parsed
    assert isinstance(model_list, ModelList)
```

### Regenerating the Client

When the Mistral OpenAPI spec is updated:

```bash
# Regenerate client
make generate-client

# Or manually:
./scripts/generate_client.sh
```

To update the spec from upstream:
```bash
curl -sL https://docs.mistral.ai/openapi.yaml -o specs/openapi.yaml
make generate-client
```

## Code Quality

```bash
# Linting
make lint

# Auto-fix lint issues
uv run ruff check --fix .

# Formatting
make format

# Type checking
make typecheck

# Run all checks
make lint && make typecheck
```

### Pre-commit Hooks (Optional)

```bash
uv run pre-commit install
```

This will run linting and formatting on every commit.

## CI/CD Pipeline

### Main CI Workflow (`.github/workflows/ci.yml`)

Triggers on push/PR to `main` and `develop`:

1. **Lint & Format Check** - Ruff linting and formatting
2. **Type Check** - MyPy static analysis
3. **E2E Tests** - Matrix across Python 3.11, 3.12, 3.13
4. **Security Scan** - Bandit security analysis

### Manual E2E Workflow (`.github/workflows/e2e-manual.yml`)

Manually trigger E2E tests with custom configuration:

1. Go to **Actions** → **E2E Tests (Manual)** → **Run workflow**
2. Configure:
   - **Base URL**: API endpoint (default: `https://api.mistral.ai`)
   - **Environment**: `production` or `staging` (for different secrets)
   - **Python version**: 3.11, 3.12, or 3.13
   - **Test markers**: Filter tests (e.g., `e2e`, `smoke`)

**Setup Required:**
1. Go to repo **Settings → Environments**
2. Create environments: `production`, `staging`
3. Add `MISTRAL_API_KEY` secret to each environment

### Client Generation Workflow (`.github/workflows/generate-client.yml`)

- Triggers when `specs/openapi.yaml` changes
- Can be manually triggered with a custom OpenAPI URL
- Creates a PR with regenerated client code

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MISTRAL_API_KEY` | Your Mistral API key | Required |
| `MISTRAL_BASE_URL` | API base URL | `https://api.mistral.ai` |

### GitHub Secrets (for CI)

| Secret | Environment | Description |
|--------|-------------|-------------|
| `MISTRAL_API_KEY` | `production` | Production API key |
| `MISTRAL_API_KEY` | `staging` | Staging API key (optional) |

## Adding New Tests

1. Create a test file in `tests/e2e/`:
   ```python
   # tests/e2e/test_my_feature.py
   import pytest
   from mistral_ai_api_client import AuthenticatedClient

   pytestmark = [pytest.mark.e2e]

   class TestMyFeature:
       async def test_something(self, api_client: AuthenticatedClient):
           # Use the generated client
           pass
   ```

2. Available fixtures (from `conftest.py`):
   - `api_client`: Generated async API client with logging
   - `async_client`: Raw httpx AsyncClient (for custom requests)
   - `sync_client`: Raw httpx Client (for sync tests)

## Sample Test Report
We use allure report to create test reports in html output. Here's a sample from one of the runs in CI
<img width="1726" height="1036" alt="image" src="https://github.com/user-attachments/assets/906dbcdf-8062-4dcc-ba0f-f13b4010b384" />

## Troubleshooting

### "ModuleNotFoundError: No module named 'mistral_ai_api_client'"

The generated client is missing. Run:
```bash
make generate-client
```

### Tests skip with "MISTRAL_API_KEY environment variable not set"

Create a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### "uv: command not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Dependencies

### Runtime
- `httpx` - Modern async HTTP client
- `pydantic` - Data validation
- `python-dotenv` - Environment management

### Development
- `pytest` + plugins - Testing framework
- `ruff` - Linting & formatting
- `mypy` - Type checking
- `pre-commit` - Git hooks
- `openapi-python-client` - Client generation
- `allure-pytest` - Test reporting

## License

MIT
