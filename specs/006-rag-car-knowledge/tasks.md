# Tasks - RAG Car Knowledge

- [ ] Select permitted sources and document licensing/terms.
- [x] Create curated RAG docs folder.
- [x] Add used-car inspection guide.
- [x] Add new-vs-used car guide.
- [x] Add Lebanon car-buying notes.
- [x] Add RAG ingestion script.
- [x] Ingest Markdown documents into PostgreSQL `documents` and
  `document_chunks` tables.
- [x] Add chunking logic with overlap.
- [x] Add lexical RAG retrieval service.
- [x] Add sourced RAG answer builder.
- [x] Connect `/chat` `general_advice` intent to RAG retrieval.
- [x] Add RAG service tests.
- [x] Add chat test proving general advice uses RAG sources.
- [ ] Create hit@3/hit@5 evaluation set.
- [ ] Integrate optional RAG context into car recommendations.

## Important Notes

- This is a lexical RAG baseline using PostgreSQL document chunks.
- Embeddings and pgvector can be added later as an upgrade.
- RAG answers include source references using local document URLs.

## Verification

- `python -m scripts.ingest_rag_docs` -> 3 markdown files found, 7 chunks
  inserted/replaced.
- `python -m pytest tests\test_rag_service.py` -> 2 passed.
- `python -m pytest tests\test_recommendation_chat.py tests\test_rag_service.py`
  -> 11 passed.
- `python -m pytest tests` -> 37 passed.
