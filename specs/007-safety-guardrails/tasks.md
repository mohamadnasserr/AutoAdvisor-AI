# Tasks - Safety Guardrails

## Text Guardrails

- [x] Add text guardrail service.
- [x] Define configurable chat message length limit.
- [x] Implement empty and whitespace-only message rejection.
- [x] Implement too-long message rejection.
- [x] Add `/chat` guardrail check before intent classification.
- [x] Add prompt-injection detection before intent classification.
- [x] Block requests for secrets, API keys, system prompts, hidden
  instructions, and internal configuration.
- [x] Block system-prompt, hidden-instruction, `.env`, API-key, and secret
  requests.
- [x] Block unsupported risky guarantee requests.
- [x] Ensure normal car-buying questions remain allowed.
- [x] Prevent blocked text from reaching intent classification and downstream
  AI services.
- [x] Return safe refusal responses for blocked chat messages.
- [x] Preserve chat memory logging for blocked messages.
- [x] Allow normal car-buying messages to continue through the regular chat
  flow.

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

- [x] Add focused text guardrail tests.
- [x] Add chat tests proving prompt-injection is blocked before intent
  classification.
- [x] Add chat tests proving normal car-buying requests still pass.
- [ ] Add price-estimator boundary tests.
- [ ] Add RAG grounding/fallback tests.
- [ ] Add upload validation tests.
- [ ] Verify image safety checks happen before permanent storage.
- [x] Run the full test suite successfully.

### Test Results

- `python -m pytest tests\test_guardrails.py` -> 6 passed.
- `python -m pytest tests\test_recommendation_chat.py tests\test_guardrails.py`
  -> 15 passed.
- `python -m pytest tests` -> 43 passed.
