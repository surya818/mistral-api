"""
Shared pytest fixtures for Mistral API E2E tests.
"""

import json
import logging
import os
import sys
from collections.abc import AsyncGenerator, Callable, Generator
from pathlib import Path
from typing import Any

import httpx
import pytest
from dotenv import load_dotenv


# Add generated client to path
sys.path.insert(0, str(Path(__file__).parent / ".." / "src" / "generated_client"))

from mistral_ai_api_client import AuthenticatedClient


# Load environment variables from .env file
load_dotenv()

# Configure logging for API calls
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mistral_api")


def _log_request(request: httpx.Request) -> None:
    """Log outgoing HTTP request."""
    logger.info(">>> %s %s", request.method, request.url)
    if request.content:
        try:
            body = json.loads(request.content)
            logger.info(">>> Body: %s", json.dumps(body, indent=2))
        except json.JSONDecodeError:
            pass


def _log_response(response: httpx.Response) -> None:
    """Log incoming HTTP response."""
    logger.info("<<< %s %s", response.status_code, response.reason_phrase)
    try:
        response.read()
        logger.info("<<< Body: %s", json.dumps(response.json(), indent=2))
    except (json.JSONDecodeError, httpx.ResponseNotRead):
        pass


async def _async_log_request(request: httpx.Request) -> None:
    """Async hook to log outgoing HTTP request."""
    _log_request(request)


async def _async_log_response(response: httpx.Response) -> None:
    """Async hook to log incoming HTTP response."""
    logger.info("<<< %s %s", response.status_code, response.reason_phrase)
    try:
        await response.aread()
        logger.info("<<< Body: %s", json.dumps(response.json(), indent=2))
    except (json.JSONDecodeError, httpx.ResponseNotRead):
        pass


# =============================================================================
# CONFIGURATION
# =============================================================================


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for Mistral API."""
    return os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai")


@pytest.fixture(scope="session")
def api_key() -> str:
    """API key for Mistral API authentication."""
    key = os.getenv("MISTRAL_API_KEY")
    if not key:
        pytest.skip("MISTRAL_API_KEY environment variable not set")
    return key


@pytest.fixture(scope="session")
def auth_headers(api_key: str) -> dict[str, str]:
    """Authentication headers for API requests."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


# =============================================================================
# HTTP CLIENTS
# =============================================================================


@pytest.fixture(scope="session")
def sync_client(base_url: str, auth_headers: dict[str, str]) -> Generator[httpx.Client, None, None]:
    """Synchronous HTTP client for API requests with logging."""
    with httpx.Client(
        base_url=base_url,
        headers=auth_headers,
        timeout=httpx.Timeout(60.0),
        event_hooks={
            "request": [_log_request],
            "response": [_log_response],
        },
    ) as client:
        yield client


@pytest.fixture
async def async_client(
    base_url: str, auth_headers: dict[str, str]
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Asynchronous HTTP client for API requests with logging."""
    async with httpx.AsyncClient(
        base_url=base_url,
        headers=auth_headers,
        timeout=httpx.Timeout(60.0),
        event_hooks={
            "request": [_async_log_request],
            "response": [_async_log_response],
        },
    ) as client:
        yield client


# =============================================================================
# GENERATED API CLIENT
# =============================================================================


@pytest.fixture
async def api_client(base_url: str, api_key: str) -> AsyncGenerator[AuthenticatedClient, None]:
    """Generated API client with type-safe methods and logging.

    Note: Function-scoped (not session) because async clients are bound to event loops,
    and each test function gets a new event loop by default in pytest-asyncio.
    """
    client = AuthenticatedClient(
        base_url=base_url,
        token=api_key,
        timeout=httpx.Timeout(60.0),
        httpx_args={
            "event_hooks": {
                "request": [_async_log_request],
                "response": [_async_log_response],
            }
        },
    )
    async with client:
        yield client


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def sample_chat_messages() -> list[dict[str, str]]:
    """Sample chat messages for testing."""
    return [
        {"role": "user", "content": "Say 'hello' and nothing else."},
    ]


@pytest.fixture
def sample_chat_request(sample_chat_messages: list[dict[str, str]]) -> dict[str, Any]:
    """Sample chat completion request body."""
    return {
        "model": "mistral-small-latest",
        "messages": sample_chat_messages,
        "temperature": 0.0,
        "max_tokens": 20,
    }


@pytest.fixture
def sample_embedding_request() -> dict[str, Any]:
    """Sample embedding request body."""
    return {
        "model": "mistral-embed",
        "input": ["Hello, world!"],
    }


# =============================================================================
# UTILITY FIXTURES
# =============================================================================


@pytest.fixture
def assert_valid_response() -> Callable[[httpx.Response, int, list[str] | None], dict[str, Any]]:
    """Factory fixture for validating API responses."""

    def _assert_valid_response(
        response: httpx.Response,
        expected_status: int = 200,
        expected_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        assert response.status_code == expected_status
        data: dict[str, Any] = response.json()
        if expected_keys:
            for key in expected_keys:
                assert key in data, f"Expected key '{key}' not found in response"
        return data

    return _assert_valid_response
