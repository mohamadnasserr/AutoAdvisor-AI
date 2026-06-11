# Tasks - Temporary Chat Memory

- [x] Decide on Redis for temporary session memory.
- [x] Define 30-minute default TTL.
- [x] Use TTL of `CHAT_MEMORY_TTL_SECONDS=1800`.
- [x] Limit memory to `CHAT_MEMORY_MAX_MESSAGES=30`.
- [x] Add Redis memory variables to `.env.example`.
- [x] Add Redis service to Docker Compose.
- [x] Add Redis memory settings to config.
- [x] Define the chat session identifier contract.
- [x] Implement chat memory service.
- [x] Store user and assistant messages from `/chat`.
- [x] Return `session_id` in chat response.
- [x] Add tests for `session_id` response.
- [x] Add tests for storing user and assistant messages.
- [x] Add tests for max message trimming.
- [ ] Integrate recent context into `/chat`.
- [ ] Add graceful Redis failure handling.
- [ ] Add privacy, isolation, TTL, and fallback tests.

## Verification

- `python -m pytest tests\test_inventory_api.py tests\test_recommendation_chat.py tests\test_comparison_api.py tests\test_chat_memory.py` -> 22 passed.
