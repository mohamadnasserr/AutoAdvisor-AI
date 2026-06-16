> Renumbered from Spec 007 after inserting Spec 007 Safety Guardrails.

# Plan - Image Intelligence

## Implementation Approach

1. Run upload validation before storage or analysis.
2. Run NSFW safety before permanent storage or further image processing.
3. Run OpenCV-based quality checks for blur and brightness.
4. Run lightweight edge-density based vehicle visibility MVP checks.
5. Return structured image analysis fields for frontend/demo use.
6. Ask the user to confirm vehicle details before using the image flow for
   price estimation or comparison.
7. Route confirmed details to the existing used-car price estimator.
8. Route confirmed details to a similar-car service backed by the curated
   inventory.
9. Allow the React frontend to add confirmed uploaded profiles to the comparison
   workflow as non-inventory profiles.
10. Keep exact make/model recognition and stronger vehicle detectors as future
    upgrades.

## Validation

- API tests cover valid image analysis and guardrail failures.
- Upload guardrail tests cover file type, MIME, size, corrupted images, and
  resolution.
- Image safety tests cover model-based behavior and fallback behavior.
- Image quality tests cover detailed, dark, bright, blurry, and blank/low-detail
  images.
- Similar-car endpoint tests cover valid requests and no-upload behavior.
- Manual React demo verifies upload, confirmed details, fair-price estimation,
  similar cars, and adding an uploaded profile to compare.
