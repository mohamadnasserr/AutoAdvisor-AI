# Tasks - RAG Knowledge Base

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
- [x] Add pgvector extension setup script.
- [x] Add `embedding vector(384)` column to `document_chunks`.
- [x] Add sentence-transformers embedding script.
- [x] Generate embeddings using
  `sentence-transformers/all-MiniLM-L6-v2`.
- [x] Store embeddings in PostgreSQL pgvector.
- [x] Add semantic RAG retrieval using vector similarity.
- [x] Keep lexical retrieval as fallback.
- [x] Connect `/chat` `general_advice` to semantic RAG retrieval.
- [x] Verify all tests pass.
- [ ] Create hit@3/hit@5 evaluation set.
- [ ] Integrate optional RAG context into car recommendations.

## Important Notes

- Spec 006 is embedding-based RAG using sentence-transformers and PostgreSQL
  pgvector, with lexical retrieval as fallback.
- RAG answers include source references using local document URLs.

## Verification

- `python -m scripts.ingest_rag_docs` -> 3 markdown files found, 7 chunks
  inserted/replaced.
- `python -m pytest tests\test_rag_service.py` -> 2 passed.
- `python -m pytest tests\test_recommendation_chat.py tests\test_rag_service.py`
  -> 11 passed.
- `python -m pytest tests` -> 37 passed.
- `python -m scripts.upgrade_rag_pgvector` -> pgvector extension and embedding
  column confirmed.
- `python -m scripts.embed_rag_chunks` -> 7 chunks embedded, dimension 384.
- `python -m pytest tests\test_rag_service.py tests\test_recommendation_chat.py`
  -> 11 passed.
- `python -m pytest tests` -> passed.
