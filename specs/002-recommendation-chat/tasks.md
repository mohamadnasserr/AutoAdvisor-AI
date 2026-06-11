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

## Missing or Weak

- [ ] Add automated tests for intent, extraction, scoring, and `/chat`.
- [ ] Improve budget extraction and validate realistic buyer phrases.
- [ ] Strengthen response formatting and ensure every recommendation has useful
  reasons/tradeoffs.
- [ ] Improve new-versus-used recommendation logic when no listing type is
  explicitly requested.
- [ ] Make recommendation formatting safe for nullable used-car mileage.
- [ ] Implement real comparison behavior.
- [ ] Define comparison request and response schemas.
- [ ] Implement comparison service for 2 to 5 cars.
- [ ] Add `POST /compare` endpoint.
- [ ] Add chat handling for comparison intent.
- [ ] Add tests for comparing 2 cars.
- [ ] Add tests for comparing 3 to 5 cars.
- [ ] Add test for rejecting more than 5 cars.
- [ ] Add test for fewer than 2 cars.
- [ ] Add comparison output with strengths, risks, best use case, and final
  verdict.
- [ ] Add optional source-backed RAG after the base workflow is stable.
- [ ] Add recommendation evaluation scenarios and rubric.
