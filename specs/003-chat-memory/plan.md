# Plan - Temporary Chat Memory

## Proposed Design

Create a small memory service around Redis list operations:

- Key: `chat:{session_id}`
- Value: JSON-serialized recent messages
- Trim: retain the configured latest messages
- Expiry: refresh the configured TTL after writes
- Failure policy: log minimally and return an empty history/no-op write

## Integration Plan

1. Add Redis to Docker Compose alongside PostgreSQL.
2. Add Redis client dependency and typed settings.
3. Extend `ChatRequest` with a session identifier or define a request-header
   contract.
4. Create a chat-memory service with read, append, trim, and expiry behavior.
5. Pass recent context into extraction/recommendation without coupling business
   logic directly to Redis.
6. Add failure-path and session-isolation tests.

## Privacy and Reliability

- Keep memory temporary and small.
- Avoid contact details and other unnecessary personal data.
- Do not use PostgreSQL or MinIO as the primary chat memory store.
- Redis outages must degrade to stateless chat.

## Deferred

No application or Docker Compose implementation is part of this spec-writing
step.
