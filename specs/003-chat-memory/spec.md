# 003 - Temporary Chat Memory

## Goal

Add small, temporary, session-based chat memory so follow-up messages can use
recent context without storing unnecessary personal data.

## Scope

- Use Redis as the chat memory store.
- Use keys shaped like `chat:{session_id}`.
- Set TTL to 30 minutes (`1800` seconds).
- Retain only the latest 8-12 messages; default to 12.
- Store only message role, text, and minimal timestamp/context metadata.
- Do not store unnecessary personal data.
- If Redis is unavailable, chat must continue statelessly.
- MinIO may be considered later for uploaded image objects; it is not the chat
  memory store.

## API Expectations

- Add a session identifier to the chat request or an equivalent header.
- Read recent messages before intent/extraction/recommendation processing.
- Append the current user message and assistant response after processing.
- Refresh TTL when a session is successfully updated.
- Never expose Redis failures as a failed recommendation request.

## Configuration

- `REDIS_URL=redis://localhost:6379/0`
- `CHAT_MEMORY_TTL_SECONDS=1800`
- `CHAT_MEMORY_MAX_MESSAGES=12`

These variables are documented in `.env.example`; implementation is deferred.

## Acceptance Criteria

- Follow-up messages can use recent context for the same session.
- Different sessions remain isolated.
- Redis keys expire after approximately 30 minutes of inactivity.
- Stored histories never exceed the configured maximum.
- Chat continues without memory when Redis is unavailable.
- Tests cover expiry configuration, trimming, isolation, and graceful failure.
