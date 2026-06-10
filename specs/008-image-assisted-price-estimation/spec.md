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
