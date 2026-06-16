> Renumbered from Spec 010 after inserting Spec 007 Safety Guardrails.

# Plan - Evaluation + Final Docs

## Implementation Approach

1. Keep automated tests as the primary regression check for backend workflows.
2. Keep React/Vite build as the primary frontend verification check.
3. Create a final demo script that starts with the PRNDS website experience:
   Drive, Park, Neutral, Rate, image-assisted evaluation, and Save.
4. Explain AI concepts in plain language:
   intent classification, preference extraction, recommendation scoring, RAG,
   ML price estimation, image safety/quality, and optional LLM rewriting.
5. Clearly separate curated demo inventory from live marketplace data.
6. Clearly state dealer inquiries are drafts only and no contact is sent
   automatically.
7. Document limitations and future improvements without overstating the MVP.

## Validation

- `python -m pytest tests` for backend behavior.
- `cd web-frontend && npm run build` for the main frontend.
- Manual React demo against a running FastAPI backend.
- Optional Streamlit backup smoke demo.
