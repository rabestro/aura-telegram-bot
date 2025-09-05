from __future__ import annotations

import logging
import textwrap

import google.generativeai as genai

logger = logging.getLogger(__name__)


class AuraEngine:
    """The core engine of the Aura bot.

    This class encapsulates the main business logic, decoupling it from any
    specific interface like Telegram or a command-line interface.
    """

    def __init__(self, gemini_api_key: str, knowledge_base: str) -> None:
        """Initializes the AuraEngine.

        Args:
            gemini_api_key: The API key for the Google Gemini service.
            knowledge_base: The text content of the knowledge base file.
        """
        logger.info("Initializing AuraEngine...")
        self._knowledge_base = knowledge_base

        # Configure the generative AI model
        genai.configure(api_key=gemini_api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("AuraEngine initialized successfully.")

    async def _get_gemini_answer(self, question: str) -> str:
        """Sends a structured prompt to the Gemini API and returns the answer.

        This is a private method responsible for the direct interaction with the AI model.

        Args:
            question: The user's question.

        Returns:
            The generated answer from the Gemini API.
        """
        prompt = textwrap.dedent(f"""
            You are a helpful and polite expert assistant for the Viessmann Vitodens 111-F gas
            boiler. Your task is to answer user questions based ONLY on the technical
            information provided below. If the answer cannot be found in the provided text,
            you must clearly state that you do not have that information.
            Do not invent any information. Answer in the same language as the user's question.

            --- Knowledge Base Start ---
            {self._knowledge_base}
            --- Knowledge Base End ---

            User Question: "{question}"
            """).strip()

        try:
            response = await self._model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"An error occurred with the Gemini API: {e}")
            return (
                "Sorry, I encountered an error while processing your request. "
                "Please try again later."
            )

    async def get_response(self, user_input: str) -> str:
        """
        Processes the user's input and returns a response.

        This is the main public entry point for the engine.

        Args:
            user_input: The text message from the user.

        Returns:
            A string containing the bot's response.
        """
        logger.info(f"Engine received input: '{user_input}'")
        return await self._get_gemini_answer(user_input)
