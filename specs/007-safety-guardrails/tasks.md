# Tasks - Safety Guardrails

**Status: MVP completed**

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

- [x] Add upload guardrail service.
- [x] Validate allowed image extensions: `jpg`, `jpeg`, `png`, and `webp`.
- [x] Validate allowed image MIME types: `image/jpeg`, `image/png`, and
  `image/webp`.
- [x] Reject empty uploads.
- [x] Reject oversized uploads above 5 MB.
- [x] Reject corrupted or unreadable image files.
- [x] Enforce minimum image resolution of 640x480.
- [x] Add image safety service.
- [x] Add NSFW safety gate MVP.
- [x] Reject suspicious NSFW/explicit filenames.
- [x] Reject empty image files in the safety gate.
- [x] Return safe image status, NSFW score, reason, and safe response.
- [x] Add image quality service.
- [x] Add blur detection using OpenCV Laplacian variance.
- [x] Add brightness scoring.
- [x] Add edge-density based vehicle visibility MVP check.
- [x] Flag blurry images.
- [x] Flag images that are too dark.
- [x] Flag images that are too bright.
- [x] Flag blank/low-detail images where a vehicle is not clearly visible.
- [x] Return image quality status, vehicle visibility status, edge density, and
  warnings.
- [x] Return safe user-facing rejection messages.

## Verification

- [x] Add focused text guardrail tests.
- [x] Add chat tests proving prompt-injection is blocked before intent
  classification.
- [x] Add chat tests proving normal car-buying requests still pass.
- [ ] Add price-estimator boundary tests.
- [ ] Add RAG grounding/fallback tests.
- [x] Add upload guardrail unit tests.
- [x] Add image quality tests.
- [x] Add tests for detailed image, dark image, bright image, blurry image, and
  blank/low-detail image.
- [x] Add image safety tests.
- [ ] Verify image safety checks happen before permanent storage.
- [x] Run the full test suite successfully.

## Important Note

- The current NSFW checker is an MVP safety-gate interface using filename
  heuristics.
- A future upgrade can replace or extend it with a pretrained NSFW image
  classifier.

### Test Results

- `python -m pytest tests\test_guardrails.py` -> 6 passed.
- `python -m pytest tests\test_recommendation_chat.py tests\test_guardrails.py`
  -> 15 passed.
- `python -m pytest tests\test_upload_guardrails.py` -> passed.
- `python -m pytest tests\test_image_quality.py` -> passed.
- `python -m pytest tests\test_image_safety.py` -> passed.
- `python -m pytest tests` -> passed.
