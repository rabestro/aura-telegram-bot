"""The main entry point for the Aura Telegram Bot."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from aura_telegram_bot.config import get_settings
from aura_telegram_bot.core.engine import AuraEngine

# --- Setup logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = (
        update.effective_user.first_name
        if update.effective_user and update.effective_user.first_name
        else "there"
    )
    if update.message is not None:
        await update.message.reply_text(
            f"Hello, {user_name}! I am the Aura expert for our Viessmann boiler. "
            "Ask me a "
            "question about it.",
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user's questions by sending them to the AuraEngine."""
    if not update.message or not update.message.text:
        return

    user_question = update.message.text
    user_first_name = (
        update.effective_user.first_name
        if update.effective_user and update.effective_user.first_name
        else "unknown"
    )
    logger.info(f"Received question from user '{user_first_name}': {user_question}")

    # Show "typing..." status in Telegram for better UX
    if update.effective_chat is not None:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # The engine is stored in the bot's context, so we can access it here.
    engine: AuraEngine = context.bot_data["engine"]
    answer = await engine.get_response(user_question)
    if update.message is not None:
        await update.message.reply_text(answer)


def main() -> None:
    """Starts the Telegram bot and waits for messages."""
    # Settings are now loaded and validated automatically when `settings` is imported.
    # No more manual checks are needed here.
    logger.info("Starting bot...")

    # --- Initialize Telegram Bot using validated settings ---
    settings = get_settings()
    application = Application.builder().token(settings.telegram_token).build()

    # --- Initialize Engine and add it to the bot's context ---
    knowledge_base = settings.load_knowledge_base()
    engine = AuraEngine(gemini_api_key=settings.gemini_api_key, knowledge_base=knowledge_base)
    application.bot_data["engine"] = engine

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
