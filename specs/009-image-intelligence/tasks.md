> Renumbered from Spec 007 after inserting Spec 007 Safety Guardrails.

# Tasks - Image Intelligence

- [x] Define upload validation and safety policy.
- [x] Add `/image/analyze` endpoint.
- [x] Connect upload validation guardrails.
- [x] Connect NSFW/model-based image safety check.
- [x] Connect image quality analysis.
- [x] Connect vehicle visibility MVP.
- [x] Return structured image analysis response.
- [x] Add dominant color estimation.
- [x] Add lightweight body-type shape estimation.
- [x] Add metadata analysis status.
- [x] Add focused image analysis API tests.
- [x] Verify full test suite passes.
- [ ] Add exact make/model recognition when a reliable model is available.
- [ ] Add confidence handling, persistence rules, and evaluation.

## Important Notes

- The current image intelligence is honest MVP computer vision.
- It does not claim exact make/model recognition yet.
- Uploaded car images are validated for safety and quality before further
  vehicle analysis.
- The endpoint returns structured fields for frontend and demo use.

## Verification

- `python -m pytest tests\test_image_analysis_api.py` -> 4 passed.
- `python -m pytest tests` -> 64 passed.
