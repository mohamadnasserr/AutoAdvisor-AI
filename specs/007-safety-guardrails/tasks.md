# Tasks - Safety Guardrails

## Text Guardrails

- [ ] Define configurable chat message length limit.
- [ ] Implement empty and whitespace-only message rejection.
- [ ] Implement too-long message rejection.
- [ ] Add prompt-injection detection before intent classification.
- [ ] Block requests for secrets, API keys, system prompts, hidden
  instructions, and internal configuration.
- [ ] Add safe handling for unsafe and off-topic requests.
- [ ] Ensure normal car-buying questions remain allowed.
- [ ] Prevent blocked text from reaching intent classification and downstream
  AI services.
- [ ] Add clear, safe refusal messages.

## Price and RAG Boundaries

- [ ] Validate realistic used-car estimator input ranges.
- [ ] Reject new-car requests from the used-car price estimator.
- [ ] Preserve the non-guarantee used-car price disclaimer.
- [ ] Require RAG answers to use retrieved sources when possible.
- [ ] Add an insufficient-knowledge RAG response.
- [ ] Prevent RAG content from overriding safety rules.
- [ ] Prevent unsupported live-availability claims.

## Upload Guardrails

- [ ] Define allowed extensions: `jpg`, `jpeg`, `png`, and `webp`.
- [ ] Define allowed MIME types: `image/jpeg`, `image/png`, and `image/webp`.
- [ ] Define and enforce maximum upload size.
- [ ] Reject corrupted or undecodable images.
- [ ] Enforce minimum image resolution.
- [ ] Run NSFW/safety checks before permanent storage.
- [ ] Add blur and brightness quality checks.
- [ ] Add vehicle visibility check.
- [ ] Return clear rejection/correction messages.

## Verification

- [ ] Add text guardrail tests.
- [ ] Add price-estimator boundary tests.
- [ ] Add RAG grounding/fallback tests.
- [ ] Add upload validation tests.
- [ ] Verify image safety checks happen before permanent storage.
- [ ] Run the full test suite successfully.
