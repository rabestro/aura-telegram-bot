"""The main entry point for the Aura Telegram Bot."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

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
        # Assumes the file is in the project root, adjust path if needed
        knowledge_base_path = Path(__file__).parent.parent.parent / "boiler_manual.txt"
        with open(knowledge_base_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("boiler_manual.txt not found. The bot will lack specific context.")
        return "No specific boiler information is available."


async def get_gemini_answer(question: str, knowledge_base: str) -> str:
    """Sends a structured prompt to the Gemini API and returns the answer.

    Args:
        question: The user's question.
        knowledge_base: The contextual information for the model.

    Returns:
        The generated answer from the Gemini API.
    """
    # This is the core of our "expert" system: Prompt Engineering.
    prompt = f"""
    You are a helpful and polite expert assistant for the Viessmann Vitodens 111-F gas boiler.
    Your task is to answer user questions based ONLY on the technical information provided below.
    If the answer cannot be found in the provided text, you must clearly state that you do not
    have that information.
    Do not invent any information. Answer in the same language as the user's question.

    --- Knowledge Base Start ---
    {knowledge_base}
    --- Knowledge Base End ---

    User Question: "{question}"
    """

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        logger.error(f"An error occurred with the Gemini API: {e}")
        return ("Sorry, I encountered an error while processing your request. Please try again "
                "later.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
            f"Hello, {user_name}! I am the Aura expert for our Viessmann boiler. "
            "Ask me a question about it.",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user's questions by sending them to the Gemini model."""
    user_question = update.message.text
    logger.info(
        f"Received question from user '{update.effective_user.first_name}': {user_question}")

    # Show "typing..." status in Telegram for better UX
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # The knowledge_base is loaded once and stored in the bot's context
    knowledge_base = context.bot_data["knowledge_base"]
    answer = await get_gemini_answer(user_question, knowledge_base)
    await update.message.reply_text(answer)


def main() -> None:
    """Starts the Telegram bot and waits for messages."""
    load_dotenv()

    # --- Configuration and Validation ---
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not telegram_token:
        msg = "TELEGRAM_TOKEN environment variable not set. Please create a .env file."
        raise ValueError(msg)
    if not gemini_api_key:
        msg = "GEMINI_API_KEY environment variable not set. Please create a .env file."
        raise ValueError(msg)

    # --- Initialize Gemini ---
    genai.configure(api_key=gemini_api_key)

    # --- Initialize Telegram Bot ---
    logger.info("Starting bot...")
    application = Application.builder().token(telegram_token).build()

    # --- Load data and add it to the bot's context ---
    # This makes the data available in all handler callbacks
    application.bot_data["knowledge_base"] = load_knowledge_base()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
