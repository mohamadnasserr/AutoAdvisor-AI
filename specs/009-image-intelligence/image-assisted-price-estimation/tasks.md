> Renumbered from Spec 008 and preserved as a supporting track within Spec 009
> after inserting Spec 007 Safety Guardrails.

# Tasks - Image-Assisted Used-Car Price Estimation

## Completed

- [x] Define confirmed structured input flow in the frontend.
- [x] Connect safe image analysis to a confirmation step.
- [x] Route confirmed used-car fields to the price estimator.
- [x] Return price range, confidence label, limitations, and disclaimer.
- [x] Keep raw model confidence in technical details only where shown.
- [x] Add similar-car matching from confirmed details.
- [x] Add uploaded/confirmed car profile support for comparison.
- [x] Clearly state that AutoAdvisor does not estimate price from image alone.

## Future Work

- [ ] Add end-to-end browser tests for the full image-assisted flow.
- [ ] Add stronger make/model suggestions when a reliable model is available.

## Verification

- `python -m pytest tests` -> latest full suite passes.
- `cd web-frontend && npm run build` -> passes.
- Manual React demo verified image-assisted fair-price estimation and
  similar-car matching.
