> Renumbered from Spec 008 and preserved as a supporting track within Spec 009
> after inserting Spec 007 Safety Guardrails.

# 009 Supporting Track - Image-Assisted Used-Car Price Estimation

## Goal

Use uploaded vehicle images for safety, quality, and context, then require the
user to confirm structured used-car attributes before running the fair-price
estimator. This is not image-only price prediction.

## Current Flow

Upload image -> upload guardrails -> NSFW/safety check -> quality and vehicle
visibility checks -> color/body-type context -> user confirms structured fields
-> used-car price estimator predicts a fair-price range.

Confirmed image-derived profiles may also be matched against the curated
inventory for similar cars and added to comparison as user-confirmed profiles.

## Rules

- Uploaded images must not be compared as raw images only.
- AutoAdvisor must not estimate price from image alone.
- The user must confirm make, model, year, mileage, fuel, transmission, and
  other required estimator fields before price estimation.
- New-car images must not be routed into the used-car estimator without
  explicitly confirmed used-car details.
- Uploaded profiles shown in comparison are not inventory listings.
- Similar-car matching uses confirmed details, not exact image recognition.
