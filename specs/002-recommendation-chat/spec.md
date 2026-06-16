# 002 - Recommendation Chat

## Goal

Provide a practical chat endpoint that interprets a buyer request, searches the
curated new/used inventory, ranks suitable cars, compares options, and explains
the tradeoffs.

## Current State

- `POST /chat` is implemented.
- Intent routing combines deterministic guardrails/overrides, an ML intent
  classifier, and rule-based fallback.
- Greeting handling returns a helpful assistant introduction instead of routing
  to RAG.
- Preference extraction supports budget, region, listing type, use case, body
  type, fuel, transmission, brand/model, luxury preference, and priorities.
- Recommendation scoring searches structured inventory and returns
  `recommended_cars`.
- General advice uses RAG with sourced answers.
- Price-check intent can call the used-car estimator when enough details are
  present.
- Dealer-contact intent can create a draft lead only.
- Optional OpenAI response polishing can rewrite backend draft answers when
  configured; with `LLM_PROVIDER=none`, draft answers are returned without any
  external call.

## Functional Requirements

- Accept a natural-language message.
- Return classified intent, extracted preferences, answer text, session ID, and
  structured recommended cars when applicable.
- Recommend up to 3-5 inventory matches with understandable reasons.
- Route clear shopping requests such as "Reliable used car under $10,000 in
  Beirut" to `car_recommendation`, not RAG/general advice.
- Respect an explicit `new`, `used`, or `both` preference.
- If listing type is clearly mentioned as used or new, do not ask for that
  detail again.
- When no exact inventory matches are found, suggest relaxing filters instead
  of returning unrelated RAG advice.
- Clearly label demo inventory and avoid unsupported availability claims.
- Store final assistant answers in memory when chat memory is enabled.
- Guardrail-blocked responses must not be rewritten by the LLM layer.

## Car Comparison

- The chatbot and API must support comparing 2 to 5 cars.
- Cars may come from:
  - Retrieved or recommended cars from the current chat result.
  - Explicit user request such as "compare Corolla, Civic, and Elantra".
  - Selected inventory car IDs from the frontend comparison workflow.
- The MVP comparison uses structured inventory cars.
- Each comparison includes make/model/year, listing type, price, mileage, body
  type, fuel, transmission, condition, warranty years when applicable,
  strengths, risks, best use case, and final recommendation/verdict.
- If a user requests more than 5 cars, ask them to narrow the comparison.
- If fewer than 2 cars are available, ask for another car or suggest broader
  inventory filters.

## Response Quality

Each recommendation should make relevant tradeoffs clear, such as budget fit,
mileage, warranty, body type, fuel, reliability, and maintenance risk. The
response must tolerate null mileage/warranty/image values and should avoid raw
JSON or internal tool names in user-facing answers.

## Acceptance Criteria

- Recommendation requests return valid `ChatResponse` payloads.
- Explicit new/used requests only return the requested listing type.
- Mixed recommendations explain why a new or used option fits.
- No-match responses suggest useful constraint changes.
- Greetings do not trigger RAG.
- Clear shopping requests route to `car_recommendation`.
- Comparison responses support 2 to 5 cars and include strengths, risks, best
  use cases, and a final verdict.
- Invalid comparison sizes receive actionable guidance.
- Tests cover intent routing, extraction, ranking, comparison, and `/chat`.
