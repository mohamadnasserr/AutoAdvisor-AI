> Renumbered from Spec 007 after inserting Spec 007 Safety Guardrails.

# 009 - Image Intelligence

## Goal

Provide image-assisted vehicle evaluation that validates uploaded images,
summarizes safety/quality/context, and helps the user continue with confirmed
structured details.

## Current State

- `/image/analyze` accepts vehicle image uploads.
- Upload guardrails validate file type, MIME type, size, readability, and
  minimum resolution before analysis.
- Model-based NSFW safety check runs before further image analysis.
- Image quality analysis returns blur, brightness, warnings, quality status,
  edge density, and vehicle visibility status.
- Metadata analysis returns dominant color, lightweight body-type estimate, and
  analysis status.
- The endpoint is honest MVP computer vision and does not claim exact
  make/model recognition.
- The React image-assisted evaluation flow asks the user to confirm vehicle
  details after upload.
- Confirmed details can be used for fair-price estimation through
  `/price/used-car`.
- Confirmed details can be used for similar-car matching through
  `/image/similar-cars`.
- An uploaded/confirmed profile can be added to comparison as a custom profile;
  it is not treated as an inventory listing.

## Requirements

- Uploaded images must not be used as raw-image-only comparisons.
- The app must not estimate price from image alone.
- The image is used for safety, quality, visibility, and context.
- User must confirm make/model/year/mileage/condition-style structured fields
  before price estimation or profile comparison.
- Similar-car matching uses confirmed details against the curated inventory.
- Uploaded profiles shown in comparison must be labeled as user-confirmed image
  profiles, not inventory cars.
- Exact make/model recognition remains a future upgrade.
- MinIO or object storage is optional future infrastructure, not required for
  the local MVP.

## Acceptance Criteria

- Valid image upload returns structured analysis fields.
- Unsupported, oversized, corrupted, unsafe, or low-resolution images are
  rejected by guardrails/safety checks.
- Accepted images show user-facing safety, quality, visibility, color, body-type
  estimate, and warnings.
- Fair-price estimation from the image flow requires confirmed structured
  details.
- Similar-car matching works from confirmed details and does not require an
  image upload.
- Uploaded profile comparison is clearly labeled as non-inventory data.
