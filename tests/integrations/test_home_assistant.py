"""Unit tests for the HomeAssistantClient."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx
from httpx import Response

from aura_telegram_bot.integrations.home_assistant import (
    ApiError,
    ConnectionError,
    HomeAssistantClient,
)

# Constants for testing
TEST_URL = "http://fake-home-assistant.local:8123"
TEST_TOKEN = "fake-long-lived-token"  # noqa: S105
TEST_ENTITY_ID = "light.living_room_lamp"

pytestmark = pytest.mark.asyncio


@pytest.fixture
def client() -> HomeAssistantClient:
    """Provides a HomeAssistantClient instance for testing."""
    return HomeAssistantClient(base_url=TEST_URL, token=TEST_TOKEN)


@respx.mock
async def test_get_entity_state_success(client: HomeAssistantClient) -> None:
    """Verify a successful API call to get an entity's state."""
    # Arrange
    # Mock the expected API response from Home Assistant
    expected_state: dict[str, Any] = {
        "entity_id": TEST_ENTITY_ID,
        "state": "on",
        "attributes": {"friendly_name": "Living Room Lamp"},
    }
    request = respx.get(f"{TEST_URL}/api/states/{TEST_ENTITY_ID}").mock(
        return_value=Response(200, json=expected_state),
    )

    # Act
    actual_state = await client.get_entity_state(TEST_ENTITY_ID)

    # Assert
    assert request.called
    assert actual_state == expected_state
    # Verify that the correct headers were sent
    sent_headers = request.calls.last.request.headers
    assert sent_headers["authorization"] == f"Bearer {TEST_TOKEN}"
    assert sent_headers["content-type"] == "application/json"


@respx.mock
async def test_get_entity_state_api_error(client: HomeAssistantClient) -> None:
    """Verify that ApiError is raised for non-200 responses."""
    # Arrange
    # Mock a 404 Not Found response
    request = respx.get(f"{TEST_URL}/api/states/{TEST_ENTITY_ID}").mock(
        return_value=Response(404),
    )

    # Act & Assert
    with pytest.raises(ApiError, match="Home Assistant API returned status 404"):
        await client.get_entity_state(TEST_ENTITY_ID)

    assert request.called


@respx.mock
async def test_get_entity_state_connection_error(client: HomeAssistantClient) -> None:
    """Verify that ConnectionError is raised on network issues."""
    # Arrange
    # Mock a network-level error, like a timeout or DNS failure
    request = respx.get(f"{TEST_URL}/api/states/{TEST_ENTITY_ID}").mock(
        side_effect=httpx.ConnectError("Connection failed"),
    )

    # Act & Assert
    with pytest.raises(ConnectionError, match="Cannot connect to Home Assistant"):
        await client.get_entity_state(TEST_ENTITY_ID)

    assert request.called
