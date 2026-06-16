# Plan - React/Vite Frontend

## Implementation Approach

1. Create a Vite + React app in `web-frontend`.
2. Keep API calls in a small helper module using `VITE_API_BASE_URL`.
3. Copy the AutoAdvisor logo into React assets.
4. Build a premium dark automotive/AI visual style with plain CSS.
5. Use PRNDS as the main product navigation model:
   Park, Rate, Neutral, Drive, Save.
6. Keep Drive as the chatbot-first experience.
7. Render inventory/recommendation/similar-car cards with representative
   images when available and text-only fallback when missing.
8. Maintain global compare selection across recommendation, inventory, and
   image-assisted similar-car cards.
9. Support uploaded/confirmed profiles in comparison without treating them as
   inventory listings.
10. Add Save Interest forms on car cards and in the Save section.
11. Keep Streamlit as a backup/demo dashboard.

## Validation

- `cd web-frontend && npm run build`.
- Manual React demo with a running backend:
  Drive chat, Park inventory, Neutral compare, Rate price check, image-assisted
  evaluation, similar cars, and Save Interest.
- Python backend tests remain the source of truth for API behavior.
