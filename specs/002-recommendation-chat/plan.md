# Plan - Recommendation Chat

## Existing Request Flow

`POST /chat` -> rule-based intent -> preference extraction -> inventory query ->
fit scoring -> text answer + Pydantic car responses.

## Implementation Approach

1. Add a compact scenario test set before changing recommendation behavior.
2. Harden preference extraction for budgets, listing type, brand aliases, and
   common buyer language.
3. Refine candidate filtering and scoring so new/used behavior is intentional.
4. Improve response formatting with consistent recommendation reasons and
   explicit tradeoffs.
5. Make all formatting null-safe.
6. Add comparison request and response Pydantic schemas for 2 to 5 cars.
7. Add a rule-based comparison service using structured PostgreSQL inventory.
8. Add `POST /compare` and route `/chat` comparison intent to the comparison
   workflow.
9. Allow a later frontend to compare selected recommended inventory cars.
10. Add optional RAG context only after the non-RAG recommendation and
    comparison workflows are stable.

## Validation Scenarios

- Reliable used city car under a budget.
- New zero-mileage car with warranty.
- New or used family SUV.
- Luxury preference with low-maintenance concern.
- No-match request.
- Missing mileage or warranty data.
- Compare 2 cars.
- Compare 3 to 5 cars.
- Reject a comparison of more than 5 cars.
- Request another car or broader filters when fewer than 2 cars are available.

## Non-Goals for This Spec

- Persistent chat memory.
- Trained ML intent classifier.
- Fair-price regression.
- Automatic dealer contact.
- Live marketplace scraping.
