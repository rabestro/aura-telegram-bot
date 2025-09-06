"""A command-line interface (CLI) for interacting with the AuraEngine."""

from __future__ import annotations

import asyncio
import logging

from aura_telegram_bot.config import settings
from aura_telegram_bot.core.engine import AuraEngine

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Runs the main CLI loop."""
    # Settings are loaded and validated upon import.
    # We can directly use the `settings` object.
    print("Initializing AuraEngine for CLI...")
    knowledge_base = settings.load_knowledge_base()
    engine = AuraEngine(gemini_api_key=settings.gemini_api_key, knowledge_base=knowledge_base)
    print("Engine ready. Type 'exit' or 'quit' to end the session.")
    print("-" * 20)

    while True:
        try:
            user_input = await asyncio.to_thread(input, "You: ")
            if user_input.strip().lower() in ("exit", "quit"):
                print("Aura: Goodbye!")
                break

            response = await engine.get_response(user_input)
            print(f"Aura: {response}")

        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D gracefully
            print("\nAura: Goodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
