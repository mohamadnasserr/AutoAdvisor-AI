# Plan - Safety Guardrails

## Implementation Order

1. Define guardrail settings and typed outcomes.
2. Implement text validation before intent classification in `/chat`.
3. Add prompt-injection, secret-request, unsafe-request, and off-topic handling.
4. Add realistic used-car input validation around price estimation.
5. Enforce RAG grounding and insufficient-knowledge responses.
6. Implement reusable upload validation before image storage or analysis.
7. Add image safety, quality, and vehicle-visibility gates as image
   intelligence is implemented.
8. Add focused tests, then run the complete suite.

## Text Guardrail Design

- Keep deterministic checks lightweight and explainable.
- Normalize input before checking empty content, length, and suspicious
  patterns.
- Return a safe response without passing blocked content to intent
  classification, chat memory, RAG, or other services.
- Log only minimal guardrail metadata; do not log secrets or full sensitive
  prompts.
- Make thresholds configurable rather than hard-coding them in route logic.

## Price and RAG Design

- Put used-car range validation in reusable schemas/service boundaries.
- Keep model output explicitly advisory and retain the existing disclaimer.
- Require RAG answer construction to attach retrieved sources.
- Return an insufficient-knowledge response when retrieval has no useful
  evidence.
- Treat instructions inside retrieved documents as untrusted content.

## Upload Guardrail Design

- Validate declared extension, MIME type, byte size, and decoded image content.
- Decode in memory or quarantine until safety checks pass.
- Verify resolution before running heavier image models.
- Run NSFW/safety checks before permanent storage.
- Run blur, brightness, and vehicle-visibility checks before attribute
  extraction.
- Return structured validation results and user-safe explanations.

## Test Plan

- Empty, whitespace-only, and too-long chat messages.
- Prompt-injection and secret/system-prompt requests.
- Normal car-buying messages that must remain allowed.
- Unrealistic and valid used-car estimator inputs.
- Grounded RAG answer and insufficient-knowledge fallback.
- Unsupported extension/MIME, oversized, corrupted, and low-resolution image.
- Safety-before-storage behavior and clear refusal messages.
- Full regression suite.
