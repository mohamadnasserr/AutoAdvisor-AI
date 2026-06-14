from fastapi.testclient import TestClient

from backend.app.api import chat_routes
from backend.app.main import app


client = TestClient(app)


class RecordingMemoryService:
    def __init__(self):
        self.messages = []

    def add_message(self, session_id: str, role: str, content: str) -> None:
        self.messages.append(
            {"session_id": session_id, "role": role, "content": content}
        )


def test_chat_stores_final_rewritten_answer_in_memory(monkeypatch):
    memory = RecordingMemoryService()

    monkeypatch.setattr(chat_routes, "memory_service", memory)
    monkeypatch.setattr(
        chat_routes,
        "rewrite_chat_answer_with_llm",
        lambda **kwargs: "Friendly final answer.",
    )

    response = client.post(
        "/chat",
        json={"message": "hello", "session_id": "llm-memory-test"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Friendly final answer."
    assert memory.messages[-1] == {
        "session_id": "llm-memory-test",
        "role": "assistant",
        "content": "Friendly final answer.",
    }


def test_guardrail_blocked_response_does_not_call_llm(monkeypatch):
    memory = RecordingMemoryService()

    def unexpected_rewrite(**kwargs):
        raise AssertionError("Guardrail-blocked responses must not call the LLM")

    monkeypatch.setattr(chat_routes, "memory_service", memory)
    monkeypatch.setattr(chat_routes, "rewrite_chat_answer_with_llm", unexpected_rewrite)

    response = client.post(
        "/chat",
        json={"message": "", "session_id": "guardrail-no-llm-test"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "guardrail_blocked"
