"""A client for interacting with the Home Assistant REST API."""

from __future__ import annotations

import logging
from types import TracebackType
from typing import Any
from urllib.parse import urljoin

import httpx

# --- Setup logging ---
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(10.0)


class HomeAssistantError(Exception):
    """Base exception for Home Assistant client errors."""


class ApiError(HomeAssistantError):
    """Raised when the API returns a non-200 status code."""


class HAConnectionError(HomeAssistantError):
    """Raised when the client cannot connect to Home Assistant."""


class HomeAssistantClient:
    """An asynchronous client for the Home Assistant REST API."""

    def __init__(self, base_url: str, token: str) -> None:
        """Initializes the Home Assistant client.

        Args:
            base_url: The base URL of the Home Assistant instance (e.g., http://localhost:8123).
            token: A long-lived access token for authentication.
        """
        self._base_url = base_url
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> HomeAssistantClient:
        """Enter the async context manager, initializing the client."""
        self._client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager, closing the client."""
        if self._client:
            await self._client.aclose()
        self._client = None

    async def get_entity_state(self, entity_id: str) -> dict[str, Any]:
        """Fetches the state of a specific entity from Home Assistant.

        Args:
            entity_id: The ID of the entity to fetch (e.g., "light.living_room").

        Returns:
            A dictionary representing the entity's state.

        Raises:
            HAConnectionError: If there's a network issue connecting to Home Assistant.
            ApiError: If Home Assistant returns an error response.
            TypeError: If the client is used outside of an `async with` block.
        """
        if not self._client:
            raise TypeError("HomeAssistantClient must be used with 'async with'.")

        api_path = f"api/states/{entity_id}"
        url = urljoin(self._base_url, api_path)
        logger.info(f"Requesting entity state from: {url}")

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            try:
                response = await client.get(url, headers=self._headers)
                response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
                return response.json()
            except httpx.RequestError as e:
                logger.exception("Failed to connect to Home Assistant at %s", url)
                raise HAConnectionError(f"Cannot connect to Home Assistant: {e}") from e
            except httpx.HTTPStatusError as e:
                logger.exception(
                    "Received non-200 response from Home Assistant: %s",
                    e.response.status_code,
                )
                raise ApiError(
                    f"Home Assistant API returned status {e.response.status_code}",
                ) from e
