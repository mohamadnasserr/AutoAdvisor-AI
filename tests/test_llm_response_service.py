from types import SimpleNamespace

from backend.app.config import settings
from backend.app.services import llm_response_service


def test_rewrite_returns_draft_without_openai_configuration(monkeypatch):
    class UnexpectedOpenAI:
        def __init__(self, **kwargs):
            raise AssertionError("OpenAI client must not be created without configuration")

    monkeypatch.setattr(settings, "llm_provider", "none")
    monkeypatch.setattr(settings, "openai_api_key", None)
    monkeypatch.setattr(llm_response_service, "OpenAI", UnexpectedOpenAI)

    draft = "Here are the strongest matches from the demo inventory."
    result = llm_response_service.rewrite_chat_answer_with_llm(
        user_message="Find me a reliable used car",
        intent="car_recommendation",
        draft_answer=draft,
        extracted_preferences={"listing_type": "used"},
        recommended_cars=[],
    )

    assert result == draft


def test_rewrite_uses_configured_openai_model_without_real_call(monkeypatch):
    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text="A friendly rewritten answer.")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured["client"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(settings, "openai_model", "gpt-5.5")
    monkeypatch.setattr(llm_response_service, "OpenAI", FakeOpenAI)

    result = llm_response_service.rewrite_chat_answer_with_llm(
        user_message="Find me a reliable used car",
        intent="car_recommendation",
        draft_answer="Draft answer.",
        extracted_preferences={"listing_type": "used"},
        recommended_cars=[],
    )

    assert result == "A friendly rewritten answer."
    assert captured["model"] == "gpt-5.5"
    assert captured["client"]["api_key"] == "test-key"


def test_rewrite_falls_back_to_draft_on_openai_error(monkeypatch):
    class FailingOpenAI:
        def __init__(self, **kwargs):
            raise RuntimeError("API unavailable")

    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(llm_response_service, "OpenAI", FailingOpenAI)

    result = llm_response_service.rewrite_chat_answer_with_llm(
        user_message="Hello",
        intent="greeting",
        draft_answer="Fallback greeting.",
        extracted_preferences={},
        recommended_cars=[],
    )

    assert result == "Fallback greeting."
