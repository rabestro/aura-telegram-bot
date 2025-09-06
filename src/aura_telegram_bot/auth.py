"""Authorization logic for the Telegram bot."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

from aura_telegram_bot.config import get_settings

logger = logging.getLogger(__name__)


# The corrected version uses Python 3.12+ syntax for generics (PEP 695).
# We declare the TypeVar `R` directly in the function signature.
def restricted[R](
    func: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[R]],
) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[R | None]]:
    """Restrict access to handlers to authorized users."""

    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> R | None:
        """The inner wrapper function that performs the authorization check."""
        settings = get_settings()
        if not update.effective_user:
            logger.warning("Decorator received an update with no effective_user.")
            return None

        user_id = update.effective_user.id
        user_name = update.effective_user.first_name

        if user_id not in settings.allowed_telegram_user_ids:
            logger.warning(
                "Unauthorized access attempt by user_id: %s (Name: %s).",
                user_id,
                user_name,
            )
            return None  # Silently ignore the request

        logger.info("Authorized access for user_id: %s (Name: %s).", user_id, user_name)
        # The wrapped function's signature is known, so we call it directly.
        return await func(update, context)

    return wrapped
