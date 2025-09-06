"""Unit tests for the AuraEngine class."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, patch

import pytest

from aura_telegram_bot.core.engine import AuraEngine

# Mark all tests in this file as asyncio, since our engine is async
pytestmark = pytest.mark.asyncio


@patch("aura_telegram_bot.core.engine.genai.GenerativeModel", autospec=True)
async def test_get_response_uses_gemini_api_successfully(
    mock_generative_model: AsyncMock,
) -> None:
    """Verify that the engine formats the prompt and calls the Gemini API correctly."""
    # Arrange: Set up the test conditions
    # 1. Configure the mock to simulate the Gemini API's response object.
    mock_response_object = AsyncMock()
    mock_response_object.text = "Mocked Gemini Response"

    # 2. Make the mock 'generate_content_async' method return our fake response object.
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content_async.return_value = mock_response_object

    # 3. Create an instance of our engine with test data.
    engine = AuraEngine(gemini_api_key="fake-api-key", knowledge_base="Test knowledge base.")
    user_question = "What is the test question?"

    # Act: Call the method we are testing
    actual_response = await engine.get_response(user_question)

    # Assert: Check that the results are what we expect
    # 1. Check that the method returned the text from our mock response.
    assert actual_response == "Mocked Gemini Response"

    # 2. Verify that the Gemini API was called exactly once.
    mock_model_instance.generate_content_async.assert_called_once()

    # 3. (Optional but good practice) Check that the prompt sent to the API was correct.
    call_args, _ = mock_model_instance.generate_content_async.call_args
    sent_prompt = call_args[0]
    assert "Test knowledge base." in sent_prompt
    assert "What is the test question?" in sent_prompt
    assert "You are a helpful and polite expert assistant" in sent_prompt


@patch("aura_telegram_bot.core.engine.genai.GenerativeModel", autospec=True)
async def test_get_response_handles_api_exception_gracefully(
    mock_generative_model: AsyncMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Verify the engine returns a user-friendly message when the Gemini API fails."""
    # Arrange
    # 1. Configure the mock to raise a generic exception to simulate an API error.
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content_async.side_effect = Exception("Simulated API error")

    # 2. Set up the logger to capture log messages.
    caplog.set_level(logging.ERROR)

    # 3. Create an instance of the engine.
    engine = AuraEngine(gemini_api_key="fake-api-key", knowledge_base="Test base.")
    user_question = "A question that will cause an error."

    # Act
    response = await engine.get_response(user_question)

    # Assert
    # 1. Check that the response is the expected user-friendly error message.
    assert "Sorry, I encountered an error" in response

    # 2. Verify that the error was logged, which is crucial for debugging.
    assert "An error occurred with the Gemini API: Simulated API error" in caplog.text


@patch("aura_telegram_bot.core.engine.genai.GenerativeModel", autospec=True)
async def test_get_response_handles_malformed_api_response(
    mock_generative_model: AsyncMock,
) -> None:
    """Verify the engine handles API responses that are missing the 'text' attribute."""
    # Arrange
    # 1. Configure the mock to return an object where `text` is None.
    mock_response_object = AsyncMock()
    mock_response_object.text = None
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content_async.return_value = mock_response_object

    # 2. Create an instance of the engine.
    engine = AuraEngine(gemini_api_key="fake-api-key", knowledge_base="Test base.")
    user_question = "Some question."

    # Act
    response = await engine.get_response(user_question)

    # Assert
    # 1. Check that the response is the expected fallback message.
    assert "Sorry, I couldn't generate a response" in response
