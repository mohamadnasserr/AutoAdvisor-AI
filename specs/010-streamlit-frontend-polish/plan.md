# Plan - Streamlit Frontend Polish

Maintain Streamlit as a compact backup/demo dashboard. Keep API calls in small
client helpers, preserve session IDs in Streamlit session state, display
structured results consistently, and make safety/validation messages easy to
understand during quick demos.

## Approach

1. Keep Streamlit API calls aligned with the FastAPI backend.
2. Avoid adding business logic that belongs in backend services.
3. Keep user-facing copy consistent with the React website:
   curated demo inventory, no live scraping, dealer drafts only.
4. Keep image-assisted price estimation honest: confirmed details are required.
5. Treat React/Vite as the main polished frontend and Streamlit as backup.

## Validation

- Manual Streamlit smoke demo can call the main backend flows.
- React/Vite remains the main frontend verified by `npm run build`.
- Backend behavior remains covered by the Python test suite.
