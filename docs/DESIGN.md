# Design

## Architecture

AutoAdvisor AI uses a Streamlit frontend, FastAPI backend, SQLite relational
database, ChromaDB vector store, and local model artifacts.

## Core Workflows

1. Convert natural-language requests into structured car preferences.
2. Search and rank seeded or approved inventory.
3. Ground recommendations and comparisons in curated RAG documents.
4. Estimate fair prices and summarize review insights.
5. Safely analyze vehicle images.
6. Draft dealer inquiries after explicit user confirmation.

## Design Constraints

- Keep the demo Lebanon-first and MENA-ready.
- Never depend on unauthorized marketplace scraping.
- Clearly identify seeded inventory and uncertain model predictions.
- Run image safety checks before storage or further processing.
