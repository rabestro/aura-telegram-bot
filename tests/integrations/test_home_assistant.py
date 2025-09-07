"""Unit tests for the HomeAssistantClient."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx
from httpx import Response

from aura_telegram_bot.integrations.home_assistant import (
    ApiError,
    HAConnectionError,
    HomeAssistantClient,
)

# Constants for testing
TEST_URL = "http://fake-home-assistant.local:8123"
TEST_TOKEN = "fake-long-lived-token"  # noqa: S105
TEST_ENTITY_ID = "light.living_room_lamp"

pytestmark = pytest.mark.asyncio


@pytest.fixture
def client_instance() -> HomeAssistantClient:
    """Provides a HomeAssistantClient instance for testing."""
    return HomeAssistantClient(base_url=TEST_URL, token=TEST_TOKEN)


@respx.mock
async def test_get_entity_state_success(client_instance: HomeAssistantClient) -> None:
    """Verify a successful API call to get an entity's state."""
    # Arrange
    expected_state: dict[str, Any] = {
        "entity_id": TEST_ENTITY_ID,
        "state": "on",
        "attributes": {"friendly_name": "Living Room Lamp"},
    }
    request = respx.get(f"{TEST_URL}/api/states/{TEST_ENTITY_ID}").mock(
        return_value=Response(200, json=expected_state),
    )

    # Act
    async with client_instance as client:
        actual_state = await client.get_entity_state(TEST_ENTITY_ID)

    # Assert
    assert request.called
    assert actual_state == expected_state
    sent_headers = request.calls.last.request.headers
    assert sent_headers["authorization"] == f"Bearer {TEST_TOKEN}"
    assert sent_headers["accept"] == "application/json"


@respx.mock
async def test_get_entity_state_api_error(client_instance: HomeAssistantClient) -> None:
    """Verify that ApiError is raised for non-200 responses."""
    # Arrange
    request = respx.get(f"{TEST_URL}/api/states/{TEST_ENTITY_ID}").mock(
        return_value=Response(404),
    )

    # Act & Assert
    with pytest.raises(ApiError, match="Home Assistant API returned status 404"):
        async with client_instance as client:
            await client.get_entity_state(TEST_ENTITY_ID)

    assert request.called


@respx.mock
async def test_get_entity_state_connection_error(
    client_instance: HomeAssistantClient,
) -> None:
    """Verify that HAConnectionError is raised on network issues."""
    # Arrange
    request = respx.get(f"{TEST_URL}/api/states/{TEST_ENTITY_ID}").mock(
        side_effect=httpx.ConnectError("Connection failed"),
    )

    # Act & Assert
    with pytest.raises(HAConnectionError, match="Cannot connect to Home Assistant"):
        async with client_instance as client:
            await client.get_entity_state(TEST_ENTITY_ID)

    assert request.called


async def test_client_used_without_context_manager(
    client_instance: HomeAssistantClient,
) -> None:
    """Verify that calling a method outside 'async with' raises a TypeError."""
    # Act & Assert
    with pytest.raises(
        TypeError,
        match="HomeAssistantClient must be used with 'async with'.",
    ):
        await client_instance.get_entity_state(TEST_ENTITY_ID)


async def test_reuses_client_session(
    monkeypatch: pytest.MonkeyPatch,
    client_instance: HomeAssistantClient,
) -> None:
    """Verify that the httpx.AsyncClient is created only once per context."""
    # Arrange
    created_count = 0

    # Spy on the httpx.AsyncClient constructor
    original_init = httpx.AsyncClient.__init__

    def spy_init(self: httpx.AsyncClient, *args: Any, **kwargs: Any) -> None:
        nonlocal created_count
        created_count += 1
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", spy_init)

    # Act
    with respx.mock:
        respx.get(f"{TEST_URL}/api/states/{TEST_ENTITY_ID}").mock(
            return_value=Response(200, json={}),  # Fix: Provide a valid JSON body
        )
        async with client_instance as client:
            await client.get_entity_state(TEST_ENTITY_ID)
            await client.get_entity_state(TEST_ENTITY_ID)

    # Assert
    assert created_count == 1, "AsyncClient should only be created once."
