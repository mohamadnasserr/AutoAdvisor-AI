> Renumbered from Spec 007 after inserting Spec 007 Safety Guardrails.

# Tasks - Image Intelligence

## Completed

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
- [x] Add confirmed vehicle details flow in React.
- [x] Connect image-assisted flow to used-car fair-price estimation from
  confirmed details.
- [x] Add similar-car request and response schemas.
- [x] Add similar-car matching service using confirmed details.
- [x] Add `/image/similar-cars` endpoint.
- [x] Add similar-car endpoint tests.
- [x] Add React similar-car matching from confirmed image details.
- [x] Add uploaded/confirmed profile support in comparison UI.
- [x] Verify full test suite passes.

## Future Work

- [ ] Add exact make/model recognition when a reliable model is available.
- [ ] Add stronger vehicle detection and confidence calibration.
- [ ] Add persistence rules for accepted image uploads if production storage is
  introduced.

## Important Notes

- The current image intelligence is honest MVP computer vision.
- It does not claim exact make/model recognition yet.
- Uploaded car images are validated for safety and quality before further
  vehicle analysis.
- AutoAdvisor does not estimate price from image alone.
- Fair-price estimation uses confirmed structured details.
- Similar-car matching uses confirmed structured details and curated inventory.

## Verification

- `python -m pytest tests\test_image_analysis_api.py` -> passed.
- `python -m pytest tests\test_upload_guardrails.py` -> passed.
- `python -m pytest tests\test_image_quality.py` -> passed.
- `python -m pytest tests\test_image_safety.py` -> passed.
- Similar-car endpoint tests -> passed.
- `python -m pytest tests` -> latest full suite passes.
- `cd web-frontend && npm run build` -> passes.
- Manual React demo verified image upload, confirmed details, fair-price
  estimation, similar cars, and adding uploaded profiles to compare.
