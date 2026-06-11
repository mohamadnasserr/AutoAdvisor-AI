# 002 - Recommendation Chat

## Goal

Provide a practical chat endpoint that interprets a buyer request, searches the
seeded new/used inventory, ranks suitable cars, and explains the tradeoffs.

## Audited Current State

- `POST /chat` is implemented and returned HTTP 200 during the audit.
- `intent_service.py` provides rule-based intent routing.
- `preference_service.py` extracts budget, region, listing type, use case, body
  type, fuel, transmission, brand, luxury preference, and priorities.
- `recommendation_service.py` filters candidates, applies rule-based scores, and
  formats a text answer.
- Comparison, dealer contact, and image analysis currently return placeholders.
- There are no first-party automated tests.

## Functional Requirements

- Accept a natural-language message.
- Return classified intent, extracted preferences, answer text, and structured
  recommended cars.
- Recommend up to 3-5 inventory matches with understandable reasons.
- Respect an explicit `new`, `used`, or `both` preference.
- When listing type is unspecified, explain meaningful new-versus-used tradeoffs
  instead of blindly favoring one category.
- Treat new cars as warranty/zero-mileage alternatives and reference pricing.
- Keep used cars as the target for future fair-price ML predictions.
- Clearly label demo inventory and avoid unsupported availability claims.
- Add source-backed RAG later; do not fabricate sources now.

## Car Comparison

- The chatbot must support comparing 2 to 5 cars.
- Cars may come from:
  - Retrieved or recommended cars from the current chat result.
  - An explicit request such as "compare Corolla, Civic, and Elantra".
  - Selected inventory car IDs from a future frontend workflow.
- The first MVP comparison must use structured inventory cars from PostgreSQL.
- Each comparison must include:
  - Make, model, and year.
  - Listing type: new or used.
  - Price and mileage.
  - Body type, fuel, and transmission.
  - Condition.
  - Warranty years when applicable to a new car.
  - Strengths, risks, best use case, and a final recommendation/verdict.
- If a user requests more than 5 cars, ask them to narrow the comparison.
- If fewer than 2 cars are available, ask for another car or suggest broader
  inventory filters.
- Comparison should be rule-based first. Source-backed RAG explanations may be
  added later.

## Response Quality

Each recommendation should make relevant tradeoffs clear, such as budget fit,
mileage, warranty, body type, fuel, reliability, and maintenance risk. The
response must tolerate null mileage/warranty values and should avoid empty
`Reason:` text.

## Acceptance Criteria

- Recommendation requests return valid `ChatResponse` payloads.
- Explicit new/used requests only return the requested listing type.
- Mixed recommendations explain why a new or used option fits.
- No-match responses suggest useful constraint changes.
- Null fields do not crash answer formatting.
- Comparison responses support 2 to 5 cars and include strengths, risks, best
  use cases, and a final verdict.
- Invalid comparison sizes receive actionable guidance.
- Tests cover intent routing, extraction, ranking, and `/chat`.
