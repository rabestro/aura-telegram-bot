"""The main entry point for the Aura Telegram Bot."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued.

    Args:
        update: An object that represents an incoming update.
        context: The context object for the callback.
    """
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hello, {user_name}! I am the Aura Echo Bot. "
        "Send me a message, and I will repeat it back to you.",
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echoes the user's message.

    Args:
        update: An object that represents an incoming update.
        context: The context object for the callback.
    """
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Starts the Telegram bot and waits for messages."""
    # Load environment variables from a .env file
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        msg = "TELEGRAM_TOKEN environment variable not set. Please create a .env file."
        raise ValueError(msg)

    print("Starting bot...")
    application = Application.builder().token(telegram_token).build()

    # Register handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot and poll for updates
    application.run_polling()
    print("Bot stopped.")


if __name__ == "__main__":
    main()
