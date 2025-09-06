"""The main entry point for the Aura Telegram Bot."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from aura_telegram_bot.auth import restricted
from aura_telegram_bot.config import get_settings
from aura_telegram_bot.core.engine import AuraEngine

# --- Setup logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# Set a higher log level for the httpx library to avoid noisy logs.
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = update.effective_user.first_name if update.effective_user else "there"
    if update.message:
        await update.message.reply_text(
            f"Hello, {user_name}! I am the Aura expert for our Viessmann boiler. "
            "Ask me a question about it.",
        )


@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user's questions by sending them to the AuraEngine."""
    if not update.message or not update.message.text:
        return

    user_question = update.message.text
    user_name = update.effective_user.first_name if update.effective_user else "unknown"
    logger.info(f"Received question from user '{user_name}': {user_question}")

    # Show "typing..." status in Telegram for better UX
    if update.effective_chat:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

    # The engine is stored in the bot's context, so we can access it here.
    engine: AuraEngine = context.bot_data["engine"]
    answer = await engine.get_response(user_question)
    if update.message:
        await update.message.reply_text(answer)


def main() -> None:
    """Starts the Telegram bot and waits for messages."""
    settings = get_settings()

    # --- Initialize Telegram Bot ---
    logger.info("Starting bot...")
    application = Application.builder().token(settings.telegram_token).build()

    # --- Initialize Engine and add it to the bot's context ---
    knowledge_base = settings.load_knowledge_base()
    engine = AuraEngine(
        gemini_api_key=settings.gemini_api_key,
        knowledge_base=knowledge_base,
    )
    application.bot_data["engine"] = engine

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
    )

    # Start the Bot, ignoring any updates that were missed while it was offline.
    logger.info("Bot started and polling for updates...")
    application.run_polling(drop_pending_updates=True)
    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
