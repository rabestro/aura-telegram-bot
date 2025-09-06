"""Unit tests for the authorization decorator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aura_telegram_bot.auth import restricted

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_update() -> MagicMock:
    """Fixture to create a mock Update object."""
    update = MagicMock()
    update.effective_user.id = 12345  # Authorized user ID
    update.effective_user.first_name = "Jegors"
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Fixture to create a mock Context object."""
    return MagicMock()


@patch("aura_telegram_bot.auth.get_settings")
async def test_restricted_allows_authorized_user(
    mock_get_settings: MagicMock,
    mock_update: MagicMock,
    mock_context: MagicMock,
) -> None:
    """Verify that the decorator allows a user with an ID in the whitelist."""
    # Arrange
    mock_get_settings.return_value.allowed_telegram_user_ids = [12345, 67890]
    original_handler = AsyncMock()
    decorated_handler = restricted(original_handler)

    # Act
    await decorated_handler(mock_update, mock_context)

    # Assert
    original_handler.assert_called_once_with(mock_update, mock_context)


@patch("aura_telegram_bot.auth.get_settings")
async def test_restricted_blocks_unauthorized_user(
    mock_get_settings: MagicMock,
    mock_update: MagicMock,
    mock_context: MagicMock,
) -> None:
    """Verify that the decorator blocks a user with an ID not in the whitelist."""
    # Arrange
    mock_get_settings.return_value.allowed_telegram_user_ids = [99999, 88888]
    original_handler = AsyncMock()
    decorated_handler = restricted(original_handler)

    # Act
    await decorated_handler(mock_update, mock_context)

    # Assert
    original_handler.assert_not_called()
