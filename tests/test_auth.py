"""Unit tests for the authorization decorator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aura_telegram_bot.auth import restricted

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@patch("aura_telegram_bot.auth.get_settings")
async def test_restricted_allows_authorized_user(
    mock_get_settings: MagicMock,
) -> None:
    """Verify that the decorator allows a user with an ID in the whitelist."""
    # Arrange
    mock_get_settings.return_value.allowed_telegram_user_ids = [12345]

    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Jegors"
    context = MagicMock()

    original_handler = AsyncMock(return_value="Success")
    decorated_handler = restricted(original_handler)

    # Act
    result = await decorated_handler(update, context)

    # Assert
    assert result == "Success"
    original_handler.assert_awaited_once_with(update, context)


@patch("aura_telegram_bot.auth.get_settings")
async def test_restricted_blocks_unauthorized_user(
    mock_get_settings: MagicMock,
) -> None:
    """Verify that the decorator blocks a user with an ID not in the whitelist."""
    # Arrange
    mock_get_settings.return_value.allowed_telegram_user_ids = [12345]

    update = MagicMock()
    update.effective_user.id = 99999  # Unauthorized ID
    update.effective_user.first_name = "Stranger"
    context = MagicMock()

    original_handler = AsyncMock()
    decorated_handler = restricted(original_handler)

    # Act
    result = await decorated_handler(update, context)

    # Assert
    assert result is None
    original_handler.assert_not_awaited()


@patch("aura_telegram_bot.auth.get_settings")
async def test_restricted_ignores_update_without_effective_user(
    mock_get_settings: MagicMock,
) -> None:
    """Verify that the decorator handles updates without an effective_user."""
    # Arrange: This simulates a system-level update, like a channel post.
    mock_get_settings.return_value.allowed_telegram_user_ids = [12345]

    update = MagicMock()
    update.effective_user = None  # No user associated with the update
    context = MagicMock()

    original_handler = AsyncMock()
    decorated_handler = restricted(original_handler)

    # Act
    result = await decorated_handler(update, context)

    # Assert
    assert result is None
    original_handler.assert_not_awaited()
