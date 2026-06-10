# AutoAdvisor AI Project Reference

This folder contains the source-of-truth planning documents for AutoAdvisor AI:

- [Regional Project Brief](./AutoAdvisor_AI_Regional_Project_Brief.pdf)
- [Full Project Roadmap](./AutoAdvisor_AI_Full_Roadmap.pdf)

## Project Direction

AutoAdvisor AI is a solo, two-week AI engineering project for an intelligent
used-car buying assistant. The demo is Lebanon-first, uses USD as its primary
currency, and should remain compatible with future MENA/GCC expansion.

The assistant should turn natural-language needs into structured preferences,
search available inventory, rank and explain recommendations, compare cars,
estimate fair prices, summarize review insights, analyze uploaded vehicle
images, and prepare dealer inquiry drafts after explicit user confirmation.

## Required Boundaries

- Do not use unauthorized scraping of restricted marketplaces.
- Use public datasets, official APIs, approved listing APIs, curated content,
  seeded inventory, and permitted pages only.
- Clearly label seeded or demo inventory and do not promise live availability.
- Do not provide financing approval, insurance, legal, or financial advice.
- Do not automatically contact dealers or store a lead without confirmation.
- Run the NSFW safety gate before storing or further processing uploads.
- Treat uncertain image predictions as suggestions requiring confirmation.
- Warn buyers to have used cars inspected by a mechanic before purchase.

## Recommended Stack

- Frontend: Streamlit
- Backend: FastAPI
- Relational storage: SQLite
- Vector storage: ChromaDB
- Classical ML: scikit-learn
- Image processing: OpenCV and Pillow
- DL/CV: pretrained models from Hugging Face, Ultralytics, or an approved API
- LLM: hosted API for schema extraction and grounded response generation

## MVP Priority

1. Core inventory search and recommendation using public or seeded data.
2. Intent classification and structured preference extraction.
3. Used-car fair-price estimation.
4. RAG over curated car guides and review summaries.
5. Seeded dealer matching and inquiry draft generation.
6. NSFW and image quality checks.
7. Vehicle presence, body type, and color extraction.

Exact make/model recognition from images and approved live inventory APIs are
stretch features.

## Target Workflows

- Recommendation: classify intent, extract preferences, search inventory, score
  candidates, retrieve supporting context, and return 3-5 explained choices.
- Comparison: compare two or more models using structured data and grounded
  ownership guidance.
- Image analysis: safety gate, quality checks, vehicle detection, attribute
  suggestions, and confidence-based confirmation.
- Dealer inquiry: match a selected vehicle to seeded or approved inventory,
  draft an inquiry, request confirmation, then optionally store a demo lead.

## Evaluation Targets

- Intent classification: at least 80% accuracy.
- Preference extraction: at least 95% valid JSON and 80% key-field accuracy.
- RAG retrieval: hit@3 at least 70% and hit@5 at least 80%.
- End-to-end recommendation: at least 8 of 10 scenarios pass manual review.
- Price model: report baseline and selected-model MAE/RMSE.
- Image pipeline: block unsafe samples and report quality/attribute failures.

## Planned Deliverables

- Working FastAPI backend and Streamlit frontend.
- SQLite database and ChromaDB vector store.
- Intent, price, and review model artifacts.
- Recommendation, comparison, image analysis, and dealer inquiry workflows.
- Evaluation scripts and documented metrics.
- `README.md`, `DESIGN.md`, `DATA.md`, `EVALS.md`, and `RUNBOOK.md`.

When implementation choices conflict, prioritize the explicit safety and scope
constraints in the Regional Project Brief, then follow the MVP ordering in the
Full Project Roadmap.
