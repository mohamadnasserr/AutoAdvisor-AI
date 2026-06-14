import pytest

from backend.app.config import settings


@pytest.fixture(autouse=True)
def disable_external_llm_calls(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "none")
    monkeypatch.setattr(settings, "openai_api_key", None)
