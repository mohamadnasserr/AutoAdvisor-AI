# Tasks - Recommendation Chat

## Completed

- [x] Add `POST /chat`.
- [x] Add rule-based intent routing.
- [x] Add rule-based preference extraction.
- [x] Add inventory candidate filtering.
- [x] Add rule-based recommendation fit scoring.
- [x] Return structured preferences and recommended cars.
- [x] Distinguish new and used cars in basic scoring and answer text.
- [x] Require future dealer workflow to store only after confirmation.
- [x] Define comparison request and response schemas.
- [x] Implement comparison service for 2 to 5 cars.
- [x] Add `POST /compare` endpoint.
- [x] Add tests for comparing 2 cars.
- [x] Add tests for comparing 3 to 5 cars.
- [x] Add test for rejecting more than 5 cars.
- [x] Add test for fewer than 2 cars.
- [x] Add comparison output with strengths, risks, best use case, and final
  verdict.

## Missing or Weak

- [ ] Add automated tests for intent, extraction, scoring, and `/chat`.
- [ ] Improve budget extraction and validate realistic buyer phrases.
- [ ] Strengthen response formatting and ensure every recommendation has useful
  reasons/tradeoffs.
- [ ] Improve new-versus-used recommendation logic when no listing type is
  explicitly requested.
- [ ] Make recommendation formatting safe for nullable used-car mileage.
- [ ] Implement real comparison behavior.
- [ ] Add chat handling for comparison intent.
- [ ] Add optional source-backed RAG after the base workflow is stable.
- [ ] Add recommendation evaluation scenarios and rubric.

## Verification

- Inventory, recommendation chat, and comparison tests passed together using:
  `python -m pytest tests\test_inventory_api.py tests\test_recommendation_chat.py tests\test_comparison_api.py`
