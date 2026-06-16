# Tasks - Recommendation Chat

## Completed

- [x] Add `POST /chat`.
- [x] Add rule-based intent routing.
- [x] Add ML intent classifier integration with rule-based fallback.
- [x] Add deterministic recommendation-intent override before RAG/general
  advice.
- [x] Add greeting handling for hello/hi/hey style messages.
- [x] Add rule-based preference extraction.
- [x] Add inventory candidate filtering.
- [x] Add rule-based recommendation fit scoring.
- [x] Return structured preferences and recommended cars.
- [x] Distinguish new and used cars in scoring and answer text.
- [x] Ensure clear used-car requests do not ask whether the user wants new or
  used.
- [x] Return natural no-match messages for inventory shopping requests.
- [x] Add optional OpenAI response polishing layer.
- [x] Keep `LLM_PROVIDER=none` fallback with no external calls required.
- [x] Ensure OpenAI is response polishing only, not a source of listings.
- [x] Require dealer workflow to store drafts only and not send automatically.
- [x] Define comparison request and response schemas.
- [x] Implement comparison service for 2 to 5 cars.
- [x] Add `POST /compare/cars` endpoint.
- [x] Add chat handling for comparison intent.
- [x] Add tests for comparing 2 cars.
- [x] Add tests for comparing 3 to 5 cars.
- [x] Add test for rejecting more than 5 cars.
- [x] Add test for fewer than 2 cars.
- [x] Add comparison output with strengths, risks, best use case, and final
  verdict.

## Missing or Weak

- [ ] Add broader recommendation evaluation scenarios and rubric.
- [ ] Improve brand/model alias coverage for more regional phrasing.
- [ ] Add more examples for no-match and near-match explanations.

## Verification

- `python -m pytest tests\test_recommendation_chat.py` -> passed.
- Inventory, recommendation chat, and comparison tests passed together using:
  `python -m pytest tests\test_inventory_api.py tests\test_recommendation_chat.py tests\test_comparison_api.py`.
- `python -m pytest tests` -> latest full suite passes.
- `cd web-frontend && npm run build` -> passes.
- Manual React Drive and Neutral demo verified where appropriate.
