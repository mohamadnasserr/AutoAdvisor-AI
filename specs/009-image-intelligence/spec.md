> Renumbered from Spec 007 after inserting Spec 007 Safety Guardrails.

# 009 - Image Intelligence

## Goal

Safely analyze uploaded vehicle images for quality, vehicle presence, color,
body type, and optional low-confidence make/model suggestions.

## Planned Scope

- Run NSFW/safety checks before storage or further analysis.
- Check resolution, blur, brightness, framing, and vehicle presence.
- Return confidence and require confirmation for uncertain attributes.
- Exact make/model recognition is a stretch feature.
- MinIO is optional future object storage, not required for the local MVP.

The preserved image-assisted used-car price estimation track is documented
under `image-assisted-price-estimation/` within this spec.
