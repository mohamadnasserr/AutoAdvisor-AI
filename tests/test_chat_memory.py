import uuid

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.chat_memory_service import ChatMemoryService


client = TestClient(app)


def test_chat_response_returns_session_id():
    session_id = f"test-{uuid.uuid4()}"

    response = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": "I want a used city car under $10,000",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == session_id


def test_chat_memory_stores_user_and_assistant_messages():
    session_id = f"test-{uuid.uuid4()}"
    memory = ChatMemoryService()

    memory.clear_session(session_id)

    response = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": "I want a used city car under $10,000",
        },
    )

    assert response.status_code == 200

    messages = memory.get_messages(session_id)

    if memory.available:
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert "used city car" in messages[0]["content"].lower()

    memory.clear_session(session_id)


def test_chat_memory_respects_max_messages_limit():
    session_id = f"test-{uuid.uuid4()}"
    memory = ChatMemoryService()

    memory.clear_session(session_id)

    for index in range(memory.max_messages + 5):
        memory.add_message(
            session_id=session_id,
            role="user",
            content=f"message {index}",
        )

    messages = memory.get_messages(session_id)

    if memory.available:
        assert len(messages) == memory.max_messages
        assert messages[-1]["content"] == f"message {memory.max_messages + 4}"

    memory.clear_session(session_id)