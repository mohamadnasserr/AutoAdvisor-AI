# Plan - Recommendation Chat

## Current Request Flow

`POST /chat` -> text guardrails -> greeting/shopping overrides -> ML intent
classifier with rule fallback -> preference extraction -> workflow service
selection -> draft answer -> optional LLM response polishing -> memory storage
and `ChatResponse`.

## Implementation Approach

1. Keep guardrails before intent classification.
2. Keep deterministic shopping and greeting handling before RAG/general advice.
3. Harden preference extraction for budgets, listing type, brand aliases, model
   names, regions, and common buyer language.
4. Refine candidate filtering and scoring so new/used behavior is intentional.
5. Make all formatting null-safe and avoid raw JSON in user-facing answers.
6. Keep comparison request and response schemas for 2 to 5 cars.
7. Keep rule-based comparison service using structured inventory.
8. Keep `/compare/cars` and route chat comparison intent to the comparison
   workflow when possible.
9. Keep price-check and dealer-contact intents connected to their dedicated
   backend services.
10. Keep optional OpenAI response polishing as a final answer rewrite only. It
    must not invent cars, prices, dealerships, or live availability.

## Validation Scenarios

- Reliable used city car under a budget.
- "Reliable used car under $10,000 in Beirut" routes to `car_recommendation`.
- New zero-mileage car with warranty.
- New or used family SUV.
- Luxury preference with low-maintenance concern.
- No-match request.
- Greeting such as "hello".
- Missing mileage or warranty data.
- Compare 2 cars.
- Compare 3 to 5 cars.
- Reject a comparison of more than 5 cars.
- Price-check with enough details and with missing fields.
- Dealer-contact draft request.

## Non-Goals for This Spec

- Real dealer message sending.
- Live marketplace scraping.
- Using OpenAI as the source of listings or prices.
