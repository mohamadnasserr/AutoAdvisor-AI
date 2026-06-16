# 014 - React/Vite Frontend

## Goal

Provide the main polished AutoAdvisor AI website using React and Vite, while
keeping Streamlit available as a backup/demo dashboard.

## Current State

- `web-frontend` contains the main React/Vite frontend.
- The frontend calls the existing FastAPI backend at
  `VITE_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.
- The visual style is premium automotive/AI: dark theme, cyan accents, subtle
  orange highlights, and AutoAdvisor logo integration.
- Main product navigation uses the PRNDS gearbox concept:
  - P = Park -> curated inventory
  - R = Rate -> used-car fair-price estimation
  - N = Neutral -> car comparison
  - D = Drive -> AI chatbot
  - S = Save -> Save Interest / dealer inquiry draft
- The PRNDS selector has a gearbox-inspired vertical UI, active gear glow, and
  smooth active-state animation.

## Product Capabilities

- Chatbot-first Drive section using `POST /chat`.
- Recommended car cards with representative `image_url` visuals when present.
- Inventory explorer with optional filters and curated demo inventory wording.
- Add to Compare from AI recommendation cards, inventory cards, and similar-car
  results.
- Neutral comparison workflow with selected inventory cars and confirmed
  uploaded profiles.
- Used-car fair-price form calling `/price/used-car`.
- Image-assisted evaluation flow calling `/image/analyze`.
- Confirmed-detail fair-price estimation from the image flow.
- Similar-car matching from confirmed image details via `/image/similar-cars`.
- Save Interest forms from car cards and from the `S - Save` section.
- Dealer inquiry draft result display with no-auto-send wording.
- Backend status indicator and friendly loading/error states.

## Product Rules

- Use "curated demo inventory" in user-facing copy.
- Do not claim inventory is live scraped.
- Do not claim representative images are exact listing photos.
- Do not expose OpenAI API keys or require OpenAI calls from the frontend.
- Do not estimate price from image alone.
- Dealer inquiry/save interest does not send email, WhatsApp, SMS, or dealer
  contact automatically.

## Acceptance Criteria

- `npm run build` passes.
- All major sections work against a running FastAPI backend.
- Backend base URL is configurable with `VITE_API_BASE_URL`.
- Streamlit remains available and is not deleted.
