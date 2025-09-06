"""Unit tests for the AuraEngine class."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from _pytest.logging import LogCaptureFixture

from aura_telegram_bot.core.engine import AuraEngine

# Mark all tests in this file as asyncio, since our engine is async
pytestmark = pytest.mark.asyncio


# We patch the entire module to have full control over all its functions
@patch("aura_telegram_bot.core.engine.genai", autospec=True)
async def test_get_response_uses_gemini_api_successfully(mock_genai: MagicMock) -> None:
    """Verify that the engine formats the prompt and calls the Gemini API correctly."""
    # Arrange to Configure the mock for a successful API response
    mock_genai.GenerativeModel.return_value.generate_content_async.return_value = SimpleNamespace(
        text="Mocked Gemini Response",
    )

    # Act
    engine = AuraEngine(gemini_api_key="fake-api-key", knowledge_base="Test knowledge base.")
    user_question = "What is the test question?"
    actual_response = await engine.get_response(user_question)

    # Assert
    # 1. Verify initialization
    mock_genai.configure.assert_called_once_with(api_key="fake-api-key")
    mock_genai.GenerativeModel.assert_called_once_with("gemini-1.5-flash")

    # 2. Verify API call
    mock_genai.GenerativeModel.return_value.generate_content_async.assert_called_once()
    call_args, _ = mock_genai.GenerativeModel.return_value.generate_content_async.call_args
    sent_prompt = call_args[0]
    assert "Test knowledge base." in sent_prompt
    assert "What is the test question?" in sent_prompt
    assert "You are a helpful and polite expert assistant" in sent_prompt

    # 3. Verify final response
    assert actual_response == "Mocked Gemini Response"


@patch("aura_telegram_bot.core.engine.genai", autospec=True)
async def test_get_response_handles_api_exception(
    mock_genai: MagicMock, caplog: LogCaptureFixture
) -> None:
    """Verify that the engine gracefully handles exceptions from the Gemini API."""
    # Arrange to Configure the mock to raise an exception when called
    error_message = "API connection failed"
    mock_genai.GenerativeModel.return_value.generate_content_async.side_effect = Exception(
        error_message
    )

    # Set up logging capture for this specific test
    with caplog.at_level(logging.ERROR, logger="aura_telegram_bot.core.engine"):
        # Act
        engine = AuraEngine(gemini_api_key="fake-api-key", knowledge_base="Test knowledge base.")
        actual_response = await engine.get_response("any question")

        # Assert
        # 1. Check if the user received a graceful error message
        assert "Sorry, I encountered an error" in actual_response

        # 2. Check if the error was logged correctly for developers
        assert len(caplog.records) == 1
        assert "An error occurred with the Gemini API" in caplog.text
        assert error_message in caplog.text


@patch("aura_telegram_bot.core.engine.genai", autospec=True)
async def test_get_response_handles_malformed_api_response(mock_genai: MagicMock) -> None:
    """Verify that the engine handles API responses that lack the 'text' attribute."""
    # Arrange to Simulate a response object without the 'text' attribute
    malformed_response = SimpleNamespace(parts=[])  # No .text attribute
    mock_genai.GenerativeModel.return_value.generate_content_async.return_value = (
        malformed_response
    )

    # Act
    engine = AuraEngine(gemini_api_key="fake-api-key", knowledge_base="Test knowledge base.")
    actual_response = await engine.get_response("any question")

    # Assert
    assert "Sorry, I couldn't generate a response" in actual_response
