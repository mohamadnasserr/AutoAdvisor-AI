# Tasks - Temporary Chat Memory

- [x] Decide on Redis for temporary session memory.
- [x] Define 30-minute default TTL.
- [x] Define 12-message default maximum.
- [x] Add Redis memory variables to `.env.example`.
- [ ] Add Redis service to Docker Compose.
- [ ] Add Redis dependency and settings fields.
- [ ] Define the chat session identifier contract.
- [ ] Implement memory read/append/trim/expiry service.
- [ ] Integrate recent context into `/chat`.
- [ ] Add graceful Redis failure handling.
- [ ] Add privacy, isolation, trimming, TTL, and fallback tests.
