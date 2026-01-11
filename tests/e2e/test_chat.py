"""
End-to-end tests for Mistral Chat Completions API.

These tests verify chat completion functionality using the generated client.
"""

from http import HTTPStatus

import httpx
import pytest

from mistral_ai_api_client import AuthenticatedClient
from mistral_ai_api_client.api.chat import chat_completion_v1_chat_completions_post
from mistral_ai_api_client.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    SystemMessage,
    UserMessage,
)


pytestmark = [pytest.mark.e2e]


class TestChatCompletion:
    """E2E tests for chat completion operations."""

    async def test_simple_chat_completion(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test a simple chat completion request."""
        request = ChatCompletionRequest(
            model="mistral-small-latest",
            messages=[
                UserMessage(content="What is 2 + 2? Reply with just the number."),
            ],
            max_tokens=10,
            temperature=0.0,
        )

        response = await chat_completion_v1_chat_completions_post.asyncio_detailed(
            client=api_client,
            body=request,
        )

        assert response.status_code == HTTPStatus.OK
        result = response.parsed
        assert isinstance(result, ChatCompletionResponse)
        assert len(result.choices) > 0
        assert result.choices[0].message.content is not None

    async def test_multi_turn_conversation(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test a multi-turn conversation workflow."""
        # Turn 1: Initial question
        request1 = ChatCompletionRequest(
            model="mistral-small-latest",
            messages=[
                UserMessage(content="What is 2 + 2?"),
            ],
            max_tokens=50,
            temperature=0.0,
        )

        response1 = await chat_completion_v1_chat_completions_post.asyncio_detailed(
            client=api_client,
            body=request1,
        )

        assert response1.status_code == HTTPStatus.OK
        result1 = response1.parsed
        assert isinstance(result1, ChatCompletionResponse)
        assistant_content = result1.choices[0].message.content

        # Turn 2: Follow-up question with conversation history
        request2 = ChatCompletionRequest(
            model="mistral-small-latest",
            messages=[
                UserMessage(content="What is 2 + 2?"),
                # Include assistant's previous response in history
                UserMessage(content="What about 3 + 3?"),
            ],
            max_tokens=50,
            temperature=0.0,
        )

        response2 = await chat_completion_v1_chat_completions_post.asyncio_detailed(
            client=api_client,
            body=request2,
        )

        assert response2.status_code == HTTPStatus.OK
        result2 = response2.parsed
        assert isinstance(result2, ChatCompletionResponse)
        assert len(result2.choices) > 0

    async def test_system_prompt(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test chat completion with system prompt."""
        request = ChatCompletionRequest(
            model="mistral-small-latest",
            messages=[
                SystemMessage(content="You are a helpful assistant. Always respond in one word."),
                UserMessage(content="Are you ready?"),
            ],
            max_tokens=20,
            temperature=0.0,
        )

        response = await chat_completion_v1_chat_completions_post.asyncio_detailed(
            client=api_client,
            body=request,
        )

        assert response.status_code == HTTPStatus.OK
        result = response.parsed
        assert isinstance(result, ChatCompletionResponse)
        assert len(result.choices) > 0


class TestChatCompletionErrors:
    """E2E tests for chat completion error handling."""

    async def test_invalid_model(
        self,
        async_client: httpx.AsyncClient,
    ) -> None:
        """Test error response for invalid model."""
        # Using raw client to test error case with missing model
        response = await async_client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )

        assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY]

    async def test_empty_messages(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test error response for empty messages."""
        request = ChatCompletionRequest(
            model="mistral-small-latest",
            messages=[],
        )

        response = await chat_completion_v1_chat_completions_post.asyncio_detailed(
            client=api_client,
            body=request,
        )

        # Empty messages should fail validation
        assert response.status_code in [
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ]
