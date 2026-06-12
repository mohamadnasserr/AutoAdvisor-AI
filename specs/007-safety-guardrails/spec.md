# 007 - Safety Guardrails

## Goal

Add practical safety and reliability boundaries around chat, used-car price
estimation, RAG answers, and future image uploads before those inputs reach
downstream AI workflows.

## Text Guardrails

Text guardrails must run before intent classification for every `/chat`
request.

- Reject empty or whitespace-only messages with a clear, safe response.
- Reject messages above a configured maximum length.
- Detect common prompt-injection attempts and requests for secrets, API keys,
  system prompts, hidden instructions, or internal configuration.
- Never reveal or summarize protected system/developer instructions, secrets,
  API keys, environment variables, or internal configuration.
- Handle unsafe or clearly off-topic requests with a concise refusal and guide
  the user back to supported car-buying tasks.
- Continue allowing normal recommendation, comparison, price-check, dealer,
  image, and car-buying advice requests.
- Return consistent guardrail outcomes that can be tested independently of
  intent classification.

## Price-Estimator Boundaries

- Validate realistic used-car input ranges before model inference, including
  year, mileage, asking price, ownership count, engine size, and other required
  model fields.
- The model applies to used cars only; it must not predict new-car prices.
- Price responses must present an estimate/range, not guarantee real market
  value.
- Keep the used-car disclaimer and recommend inspection and local market
  verification.
- Reject impossible or clearly invalid values with actionable validation
  feedback.

## RAG Grounding Rules

- RAG should answer from retrieved sources when possible.
- Answers should include source references for grounded claims.
- When retrieved knowledge is insufficient, say so instead of inventing an
  answer.
- Do not claim live availability unless data comes from seeded or approved
  inventory.
- Retrieved content must not override system safety rules or request secrets.

## Future Upload Guardrails

Upload guardrails must run before image storage or image analysis.

- Allow only `jpg`, `jpeg`, `png`, and `webp` file extensions.
- Validate MIME types against an explicit allowlist:
  `image/jpeg`, `image/png`, and `image/webp`.
- Enforce a configured maximum upload size.
- Reject corrupted or undecodable images.
- Enforce a configured minimum image resolution.
- Run NSFW/safety checks before permanent storage.
- Check blur and brightness quality.
- Check that a vehicle is visible before vehicle-specific analysis.
- Return clear, safe refusal or correction messages for rejected uploads.
- Store only images that pass the required pre-storage safety checks.

## Acceptance Criteria

- `/chat` rejects empty and too-long messages.
- `/chat` blocks prompt-injection and system-secret requests with a safe
  response.
- `/chat` still allows normal car-buying questions.
- The price estimator validates realistic used-car input ranges and preserves
  its disclaimer.
- RAG answers include sources or state when knowledge is insufficient.
- Upload validation rejects unsupported file types, oversized files, corrupted
  images, and low-resolution images.
- Image safety checks happen before permanent storage.
- Tests exist for text guardrails and upload validation.
- The full test suite passes.

## Non-Goals

- Building a perfect general-purpose moderation system.
- Guaranteeing that every adversarial prompt will be detected.
- Implementing the future image-analysis pipeline in this spec-writing step.
