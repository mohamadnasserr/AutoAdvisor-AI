from backend.app.db.database import SessionLocal
from backend.app.services.rag_service import build_rag_answer, retrieve_rag_sources


def test_rag_retrieves_used_car_inspection_sources():
    db = SessionLocal()

    try:
        sources = retrieve_rag_sources(
            db,
            "What should I check before buying a used car?",
            limit=3,
        )

        assert len(sources) > 0
        assert any("Inspection" in source.title or "Lebanon" in source.title for source in sources)
        assert all(source.score > 0 for source in sources)

    finally:
        db.close()


def test_rag_answer_includes_sources():
    db = SessionLocal()

    try:
        sources = retrieve_rag_sources(
            db,
            "How do I inspect a used car before payment?",
            limit=3,
        )

        answer = build_rag_answer(
            "How do I inspect a used car before payment?",
            sources,
        )

        assert "Based on the AutoAdvisor knowledge base" in answer
        assert "Sources:" in answer
        assert "local://rag_docs/" in answer

    finally:
        db.close()