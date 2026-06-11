# 008 - Image-Assisted Used-Car Price Estimation

## Goal

Use image-derived suggestions to help collect structured used-car attributes
before running the used-car price estimator. This is not image-only prediction.

## Planned Scope

Flow: upload image -> NSFW/safety check -> quality check -> vehicle detection ->
color/body-type/make-model suggestion -> user confirms structured fields ->
used-car price estimator predicts a price range.

New-car images must not be routed into a used-car price prediction without
explicitly confirmed used-car details.

## Future Image-Derived Comparison

- Uploaded images must not be compared as raw images only.
- The image pipeline should extract or suggest vehicle attributes.
- The user must confirm make, model, year, mileage, and condition before
  comparison or price estimation.
- After confirmation, image-derived car profiles may be compared with each
  other or with PostgreSQL inventory cars.
- This future workflow is not required before the basic inventory comparison
  capability works.
