"""The main entry point for the Aura Telegram Bot."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from aura_telegram_bot.core.engine import AuraEngine

# --- Setup logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def load_knowledge_base() -> str:
    """Loads the boiler manual text from a file.

    Returns:
        The content of the knowledge base file as a string.
    """
    try:
        # Assumes the file is in the project root (and container WORKDIR)
        knowledge_base_path = Path("knowledge_base.txt")
        return knowledge_base_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error("knowledge_base.txt not found. The bot will lack specific context.")
        return "No specific boiler information is available."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hello, {user_name}! I am the Aura expert for our Viessmann boiler. "
        "Ask me a question about it.",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user's questions by sending them to the AuraEngine."""
    if not update.message or not update.message.text:
        return

    user_question = update.message.text
    logger.info(f"Received question from user '{update.effective_user.first_name}': {user_question}")

    # Show "typing..." status in Telegram for better UX
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # The engine is stored in the bot's context, so we can access it here.
    engine: AuraEngine = context.bot_data["engine"]
    answer = await engine.get_response(user_question)
    await update.message.reply_text(answer)


def main() -> None:
    """Starts the Telegram bot and waits for messages."""
    load_dotenv()

    # --- Configuration and Validation ---
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if telegram_token is None:
        msg = "TELEGRAM_TOKEN environment variable not set. Please create a .env file."
        raise ValueError(msg)
    if gemini_api_key is None:
        msg = "GEMINI_API_KEY environment variable not set. Please create a .env file."
        raise ValueError(msg)

    # --- Initialize Telegram Bot ---
    logger.info("Starting bot...")
    application = Application.builder().token(telegram_token).build()

    # --- Initialize Engine and add it to the bot's context ---
    knowledge_base = load_knowledge_base()
    engine = AuraEngine(gemini_api_key=gemini_api_key, knowledge_base=knowledge_base)
    application.bot_data["engine"] = engine

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
