import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.app.models.db_models import Document,DocumentChunk

from sentence_transformers import SentenceTransformer
from sqlalchemy import text

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "before",
    "between",
    "buy",
    "buying",
    "car",
    "cars",
    "do",
    "for",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "new",
    "of",
    "or",
    "should",
    "the",
    "to",
    "used",
    "what",
    "when",
    "with",
}

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedding_model: SentenceTransformer | None = None


@dataclass
class RagSource:
    title: str
    source_url: str
    category: str
    chunk_index: int
    text: str
    score: int


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {token for token in tokens if token not in STOPWORDS and len(token) > 2}

def get_embedding_model() -> SentenceTransformer:
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return _embedding_model


def retrieve_semantic_rag_sources(db: Session, query: str, limit: int = 3) -> list[RagSource]:
    model = get_embedding_model()
    query_embedding = model.encode([query], normalize_embeddings=True)[0]
    query_vector = "[" + ",".join(str(float(value)) for value in query_embedding.tolist()) + "]"

    rows = db.execute(
        text(
            """
            SELECT
                dc.chunk_index,
                dc.text,
                dc.category,
                dc.source_url,
                d.title,
                1 - (dc.embedding <=> CAST(:query_embedding AS vector)) AS similarity
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit;
            """
        ),
        {
            "query_embedding": query_vector,
            "limit": limit,
        },
    ).fetchall()

    sources: list[RagSource] = []

    for row in rows:
        sources.append(
            RagSource(
                title=row.title,
                source_url=row.source_url,
                category=row.category,
                chunk_index=row.chunk_index,
                text=row.text,
                score=round(float(row.similarity) * 100),
            )
        )

    if sources:
        return sources

    return retrieve_rag_sources(db, query, limit)

def retrieve_rag_sources(db: Session, query: str, limit: int = 3) -> list[RagSource]:
    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    chunks = db.query(DocumentChunk).all()
    documents = db.query(Document).all()
    document_titles = {document.id: document.title for document in documents}

    scored_sources: list[RagSource] = []

    for chunk in chunks:
        chunk_tokens = tokenize(chunk.text)
        score = len(query_tokens.intersection(chunk_tokens))

        if score <= 0:
            continue

        document_title = document_titles.get(chunk.document_id, "Unknown Source")

        scored_sources.append(
            RagSource(
                title=document_title,
                source_url=chunk.source_url,
                category=chunk.category,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                score=score,
            )
        )

    scored_sources.sort(key=lambda source: source.score, reverse=True)

    return scored_sources[:limit]


def build_rag_answer(question: str, sources: list[RagSource]) -> str:
    if not sources:
        return (
            "I do not have enough sourced knowledge for this question yet. "
            "For used-car buying, always inspect the car with a trusted mechanic, verify documents, "
            "check accident history, and compare similar market listings before paying."
        )

    bullet_points = []

    combined_text = " ".join(source.text for source in sources).lower()

    if any(word in combined_text for word in ["inspection", "mechanic", "test drive", "engine"]):
        bullet_points.append(
            "Inspect the car in daylight, test drive it, and have a trusted mechanic check the engine, chassis, electronics, tires, brakes, and diagnostic codes."
        )

    if any(word in combined_text for word in ["documents", "registration", "ownership", "customs", "legal"]):
        bullet_points.append(
            "Verify ownership papers, registration, insurance/customs status where relevant, chassis/VIN details, and whether there are unpaid fines or legal issues."
        )

    if any(word in combined_text for word in ["accident", "paint", "panel", "rust", "flood"]):
        bullet_points.append(
            "Look for accident or flood signs such as uneven paint, panel gaps, rust, suspicious repairs, damp smells, or unclear vehicle history."
        )

    if any(word in combined_text for word in ["new car", "warranty", "depreciation"]):
        bullet_points.append(
            "New cars usually give warranty and lower short-term risk, while used cars may offer better value because depreciation has already happened."
        )

    if any(word in combined_text for word in ["negotiation", "price", "mileage", "service history"]):
        bullet_points.append(
            "Negotiate based on mileage, year, condition, service history, tire condition, accident history, and comparable alternatives."
        )

    if not bullet_points:
        bullet_points.append(
            "Use the retrieved notes as a checklist: compare risk, condition, documents, ownership cost, and realistic alternatives before deciding."
        )

    source_lines = [
        f"- {source.title} ({source.source_url}, chunk {source.chunk_index})"
        for source in sources
    ]

    return (
        "Based on the AutoAdvisor knowledge base:\n"
        + "\n".join(f"- {point}" for point in bullet_points)
        + "\n\nSources:\n"
        + "\n".join(source_lines)
    )