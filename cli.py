"""A command-line interface (CLI) for interacting with the AuraEngine."""

from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv

from aura_telegram_bot.core.engine import AuraEngine
from aura_telegram_bot.main import load_knowledge_base

# --- Setup logging ---
# We can keep it minimal for the CLI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Runs the main CLI loop."""
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        msg = "GEMINI_API_KEY environment variable not set. Please create a .env file."
        raise ValueError(msg)

    # --- Initialize Engine ---
    print("Initializing AuraEngine for CLI...")
    knowledge_base = load_knowledge_base()
    engine = AuraEngine(gemini_api_key=gemini_api_key, knowledge_base=knowledge_base)
    print("Engine ready. Type 'exit' or 'quit' to end the session.")
    print("-" * 20)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Aura: Goodbye!")
                break

            response = await engine.get_response(user_input)
            print(f"Aura: {response}")

        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D gracefully
            print("\nAura: Goodbye!")
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ValueError as e:
        logger.error(e)
