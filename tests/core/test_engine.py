from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from aura_telegram_bot.core.engine import AuraEngine

# Mark all tests in this file as asyncio, since our engine is async
pytestmark = pytest.mark.asyncio


@patch("aura_telegram_bot.core.engine.genai.GenerativeModel", autospec=True)
async def test_get_response_uses_gemini_api(mock_generative_model: AsyncMock) -> None:
    """Verify that the engine formats the prompt and calls the Gemini API correctly."""
    # Arrange: Set up the test conditions
    # 1. Configure the mock to simulate the Gemini API's response object.
    mock_response_object = AsyncMock()
    mock_response_object.text = "Mocked Gemini Response"

    # 2. Make the mock 'generate_content_async' method return our fake response object.
    #    The `return_value` of the model instance is what we configure.
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content_async.return_value = mock_response_object

    # 3. Create an instance of our engine with test data.
    engine = AuraEngine(
        gemini_api_key="fake-api-key", knowledge_base="Test knowledge base."
    )
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
