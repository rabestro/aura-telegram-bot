"""Manages application configuration and secrets using Pydantic."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Setup logging ---
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Manages application settings and secrets using Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Secrets (will be loaded from the .env file) ---
    telegram_token: str
    gemini_api_key: str

    # --- Security ---
    # A list of authorized Telegram user IDs. Pydantic will automatically
    # convert a comma-separated string from the .env file into a list of ints.
    allowed_telegram_user_ids: list[int] = Field(..., min_length=1)

    # --- Application settings ---
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
                f"'{self.knowledge_base_path}' not found. Bot will lack specific context.",
            )
            return "No specific boiler information is available."


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of the Settings object."""
    return Settings()  # ty: ignore[missing-argument]
