# echo_bot.py
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# Get the token from an environment variable for security
# We will pass this variable when running the Docker container
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables")

# --- Bot Handlers ---

# This function handles the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = update.effective_user.first_name
    await update.message.reply_text(f'Привет, {user_name}! Я эхо-бот. Просто отправь мне сообщение, и я его повторю.')

# This function handles any text message
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user's message."""
    await update.message.reply_text(update.message.text)

# --- Main function to run the bot ---
def main() -> None:
    """Start the telegram bot and wait for messages."""
    print("Starting bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot and poll for updates
    application.run_polling()
    print("Bot stopped.")


if __name__ == '__main__':
    main()