> Renumbered from Spec 010 after inserting Spec 007 Safety Guardrails.

# Tasks - Evaluation + Final Docs

## Completed

- [x] Add first-party automated tests for core API workflows.
- [x] Add inventory/search API tests.
- [x] Add recommendation chat tests.
- [x] Add comparison API tests.
- [x] Add chat memory tests.
- [x] Add intent classifier tests.
- [x] Add price estimator tests.
- [x] Add RAG service tests.
- [x] Add guardrail, upload, image safety, and image quality tests.
- [x] Add image analysis API tests.
- [x] Add dealer lead tests.
- [x] Verify React/Vite build passes.

## Remaining Final Docs

- [ ] Write AI concepts explanation.
- [ ] Write RAG explanation and grounding rules.
- [ ] Write ML model explanation with features, metrics, and limitations.
- [ ] Write image flow explanation.
- [ ] Write optional OpenAI response layer explanation.
- [ ] Add curated demo inventory / no-live-scraping disclaimer.
- [ ] Add dealer drafts only / no automatic sending disclaimer.
- [ ] Write and rehearse the final demo script.
- [ ] Add final local runbook for backend, seed data, React/Vite, and Streamlit.

## Verification

- `python -m pytest tests` -> latest full suite passes.
- `cd web-frontend && npm run build` -> passes.
- Manual React demo verified where appropriate.
