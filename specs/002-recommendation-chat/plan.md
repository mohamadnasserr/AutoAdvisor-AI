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
6. Add optional RAG context only after the non-RAG workflow is stable.

## Validation Scenarios

- Reliable used city car under a budget.
- New zero-mileage car with warranty.
- New or used family SUV.
- Luxury preference with low-maintenance concern.
- No-match request.
- Missing mileage or warranty data.

## Non-Goals for This Spec

- Persistent chat memory.
- Trained ML intent classifier.
- Fair-price regression.
- Automatic dealer contact.
- Live marketplace scraping.
