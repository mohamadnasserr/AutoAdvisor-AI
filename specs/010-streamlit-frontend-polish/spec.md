# 010 - Streamlit Frontend Polish

## Goal

Keep Streamlit as a backup/demo dashboard for the stable backend capabilities
without duplicating backend business logic.

## Current State

- The primary polished frontend has moved to the React/Vite website in
  `web-frontend`.
- The Streamlit app remains available as a lightweight backup dashboard and
  internal demo surface.
- Streamlit can exercise backend APIs for inventory search, chat, comparison,
  used-car price checks, image analysis, similar cars, and dealer inquiry
  drafts.

## Planned Scope

- Keep Streamlit useful for quick backend demos and debugging.
- Preserve backend base URL configuration.
- Keep chatbot-style interaction where practical.
- Show inventory/search results and recommendation cards.
- Keep used-car price-check form and disclaimer.
- Keep image analysis and confirmed-detail fair-price flow where practical.
- Keep dealer inquiry draft wording clear: no real message is sent
  automatically.

## Non-Goals

- Streamlit is not the main production-style website.
- Do not duplicate all React/Vite product polish here.
- Do not add separate business logic in Streamlit.
