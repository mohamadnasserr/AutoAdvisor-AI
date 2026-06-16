> Renumbered from Spec 008 and preserved as a supporting track within Spec 009
> after inserting Spec 007 Safety Guardrails.

# Plan - Image-Assisted Used-Car Price Estimation

## Implementation Approach

1. Keep upload guardrails and image safety checks before any image analysis.
2. Show assistant-style image feedback instead of raw technical output.
3. Require user confirmation for structured vehicle details.
4. Route confirmed used-car fields to `/price/used-car`.
5. Route confirmed details to `/image/similar-cars` for curated inventory
   matches.
6. Allow confirmed uploaded profiles to be added to comparison as non-inventory
   profiles.
7. Keep the disclaimer visible: price is not estimated from image alone.

## Validation

- API tests cover the underlying image and price endpoints.
- Similar-car endpoint tests cover confirmed-detail matching without requiring
  image upload.
- Manual React demo verifies upload, confirmed details, fair-price estimate,
  similar cars, and uploaded profile comparison.
