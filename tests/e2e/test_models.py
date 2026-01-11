"""
End-to-end tests for Mistral Models API.

These tests verify model listing, retrieval, and access control
using the generated type-safe API client.
"""

from http import HTTPStatus

import pytest
from mistral_ai_api_client import AuthenticatedClient
from mistral_ai_api_client.api.models import (
    delete_model_v1_models_model_id_delete,
    list_models_v1_models_get,
    retrieve_model_v1_models_model_id_get,
)
from mistral_ai_api_client.models import BaseModelCard, ModelList


pytestmark = [pytest.mark.e2e]


class TestModelRetrieval:
    """E2E tests for model retrieval operations."""

    async def test_get_model_devstral_small_latest(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test retrieving the devstral-small-latest model."""
        response = await retrieve_model_v1_models_model_id_get.asyncio_detailed(
            model_id="devstral-small-latest",
            client=api_client,
        )

        assert response.status_code == HTTPStatus.OK
        model = response.parsed
        assert isinstance(model, BaseModelCard)
        assert model.id == "devstral-small-latest"
        assert model.object_ == "model"
        assert model.created is not None
        assert model.owned_by is not None

    async def test_list_models(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test listing all available models."""
        response = await list_models_v1_models_get.asyncio_detailed(
            client=api_client,
        )

        assert response.status_code == HTTPStatus.OK
        model_list = response.parsed
        assert isinstance(model_list, ModelList)
        assert model_list.object_ == "list"
        assert len(model_list.data) > 0

        # Verify each model has required fields (type-safe access)
        for model in model_list.data:
            assert model.id is not None
            assert model.object_ == "model"

    async def test_get_invalid_model_id(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test fetching a non-existent model returns 404."""
        response = await retrieve_model_v1_models_model_id_get.asyncio_detailed(
            model_id="devstral-xxl",
            client=api_client,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestModelAccessControl:
    """E2E tests for model access control and permissions."""

    async def test_cannot_delete_system_model(
        self,
        api_client: AuthenticatedClient,
    ) -> None:
        """Test that system models like devstral-latest cannot be deleted."""
        response = await delete_model_v1_models_model_id_delete.asyncio_detailed(
            model_id="devstral-latest",
            client=api_client,
        )

        # System models should not be deletable
        # Expected: 403 Forbidden, 405 Method Not Allowed, or 400 Bad Request
        assert response.status_code in [
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.METHOD_NOT_ALLOWED,
        ]
