import json
from typing import Literal

import redis

from backend.app.config import settings


MessageRole = Literal["user", "assistant"]


class ChatMemoryService:
    def __init__(self) -> None:
        self.redis_url = settings.redis_url
        self.ttl_seconds = settings.chat_memory_ttl_seconds
        self.max_messages = settings.chat_memory_max_messages

        try:
            self.client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            self.client.ping()
            self.available = True
        except redis.RedisError:
            self.client = None
            self.available = False

    def _key(self, session_id: str) -> str:
        return f"chat:{session_id}"

    def get_messages(self, session_id: str) -> list[dict]:
        if not self.available or self.client is None:
            return []

        try:
            raw_messages = self.client.lrange(self._key(session_id), 0, -1)
            return [json.loads(message) for message in raw_messages]
        except (redis.RedisError, json.JSONDecodeError):
            return []

    def add_message(self, session_id: str, role: MessageRole, content: str) -> None:
        if not self.available or self.client is None:
            return

        message = {
            "role": role,
            "content": content,
        }

        try:
            key = self._key(session_id)

            self.client.rpush(key, json.dumps(message))
            self.client.ltrim(key, -self.max_messages, -1)
            self.client.expire(key, self.ttl_seconds)

        except redis.RedisError:
            return

    def clear_session(self, session_id: str) -> None:
        if not self.available or self.client is None:
            return

        try:
            self.client.delete(self._key(session_id))
        except redis.RedisError:
            return