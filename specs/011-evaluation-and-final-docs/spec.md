> Renumbered from Spec 010 after inserting Spec 007 Safety Guardrails.

# 011 - Evaluation + Final Docs

## Goal

Demonstrate measurable behavior and provide clear final documentation for the
AutoAdvisor AI MVP.

## Current Product Scope To Document

- FastAPI backend.
- PostgreSQL curated demo inventory with about 120 cars and 11 dealerships.
- React/Vite main frontend and Streamlit backup dashboard.
- Chatbot-style AI assistant.
- Optional OpenAI response polishing layer.
- Inventory recommendations from structured inventory.
- RAG for general car-buying advice.
- ML used-car fair-price estimator.
- Image-assisted vehicle evaluation.
- Similar-car matching from confirmed image details.
- Dealer inquiry drafts / Save Interest flow.
- Representative demo car images.
- Compare selection from AI recommendations, inventory cards, and similar-car
  results.
- PRNDS product navigation:
  - P = Park -> Inventory
  - R = Rate -> Price estimation
  - N = Neutral -> Compare cars
  - D = Drive -> AI chatbot
  - S = Save -> Save interest / dealer inquiry draft

## Final Documentation Requirements

- AI concepts explanation.
- Intent routing and chatbot workflow explanation.
- RAG explanation and grounding rules.
- ML model explanation, features, metrics, and limitations.
- Image flow explanation, including safety, quality, confirmed details, similar
  cars, and no image-only price estimation.
- Optional OpenAI response layer explanation.
- Curated demo inventory / no-live-scraping disclaimer.
- Dealer drafts only / no automatic sending disclaimer.
- Final demo script.
- Local runbook for backend, seed data, React/Vite frontend, and Streamlit
  backup.

## Acceptance Criteria

- Full backend test suite passes.
- React/Vite production build passes.
- Manual React demo covers Drive, Park, Neutral, Rate, image evaluation, and
  Save Interest.
- Documentation explains what is real, what is demo data, and what is future
  production work.
