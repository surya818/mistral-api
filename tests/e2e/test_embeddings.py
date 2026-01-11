"""
End-to-end tests for Mistral Embeddings API.

These tests verify embedding generation functionality using the generated client.
"""

from http import HTTPStatus

import pytest

from mistral_ai_api_client import AuthenticatedClient
from mistral_ai_api_client.api.embeddings import embeddings_v1_embeddings_post
from mistral_ai_api_client.models import EmbeddingRequest, EmbeddingResponse


pytestmark = [pytest.mark.e2e]


class TestEmbeddings:
    """E2E tests for embedding operations."""

    async def test_single_text_embedding(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test embedding generation for a single text."""
        request = EmbeddingRequest(
            model="mistral-embed",
            input_="Hello, world!",
        )

        response = await embeddings_v1_embeddings_post.asyncio_detailed(
            client=api_client,
            body=request,
        )

        assert response.status_code == HTTPStatus.OK
        result = response.parsed
        assert isinstance(result, EmbeddingResponse)
        assert len(result.data) == 1
        assert len(result.data[0].embedding) > 0

    async def test_batch_embeddings(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test embedding generation for multiple texts."""
        texts = [
            "The weather is shit today.",
            "But I live in Sweden",
            "Right!!!",
        ]

        request = EmbeddingRequest(
            model="mistral-embed",
            input_=texts,
        )

        response = await embeddings_v1_embeddings_post.asyncio_detailed(
            client=api_client,
            body=request,
        )

        assert response.status_code == HTTPStatus.OK
        result = response.parsed
        assert isinstance(result, EmbeddingResponse)
        assert len(result.data) == 3

        # All embeddings should have same dimensions
        dimensions = [len(item.embedding) for item in result.data]
        assert len(set(dimensions)) == 1

    async def test_semantic_similarity(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test that similar texts have higher embedding similarity."""
        texts = [
            "Apple and brocolli has highest fibre content",
            "Siri is the AI assistant in all apple phones",
            "Tim Cook is investing a lot in Apple's AI development",
        ]

        request = EmbeddingRequest(
            model="mistral-embed",
            input_=texts,
        )

        response = await embeddings_v1_embeddings_post.asyncio_detailed(
            client=api_client,
            body=request,
        )

        assert response.status_code == HTTPStatus.OK
        result = response.parsed
        assert isinstance(result, EmbeddingResponse)

        embeddings = [item.embedding for item in result.data]

        def dot_product(a: list[float], b: list[float]) -> float:
            return sum(x * y for x, y in zip(a, b, strict=True))

        # Weather-related texts (0, 1) should be more similar to each other
        # than to the programming text (2)
        company_and_fruit_similarity = dot_product(embeddings[0], embeddings[1])
        company_similarity = dot_product(embeddings[1], embeddings[2])
        print(f"Company similarity{company_similarity} - Company and fruit Similarity{company_and_fruit_similarity}")
        assert company_similarity > company_and_fruit_similarity
