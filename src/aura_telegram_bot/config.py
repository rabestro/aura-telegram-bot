"""Manages application configuration and secrets using Pydantic."""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Setup logging ---
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Manages application settings and secrets using Pydantic."""

    # This tells Pydantic to load settings from a .env file.
    # The `env_file` path is relative to where the script is run.
    # In Docker, we use `aura-bot.env`, locally you can use a `.env`.
    # Pydantic will handle this automatically.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Secrets (will be loaded from the .env file) ---
    # Pydantic automatically finds environment variables matching these field names
    # (case-insensitive) and validates them.
    telegram_token: str
    gemini_api_key: str

    # --- Application settings ---
    # We can define default values for non-secret settings.
    knowledge_base_path: Path = Path("knowledge_base.txt")

    def load_knowledge_base(self) -> str:
        """Loads the knowledge base content from the configured path.

        Returns:
            The content of the knowledge base file as a string.
        """
        logger.info(f"Loading knowledge base from: {self.knowledge_base_path}")
        try:
            return self.knowledge_base_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.error(
                f"'{self.knowledge_base_path}' not found. Bot will lack specific context."
            )
            return "No specific boiler information is available."


# Create a single, importable instance of the settings.
# When this line is executed, Pydantic immediately loads and validates
# the environment variables. If a required variable is missing, the app
# will fail fast with a clear error message.
settings = Settings()
