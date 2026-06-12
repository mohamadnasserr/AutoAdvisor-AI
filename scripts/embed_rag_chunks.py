from sqlalchemy import text

from backend.app.db.database import engine


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def embed_rag_chunks() -> None:
    print("Starting RAG embedding script...")

    print("Opening database connection...")
    with engine.connect() as connection:
        print("Database connection opened.")

        print("Querying chunks...")
        rows = connection.execute(
            text(
                """
                SELECT id, text
                FROM document_chunks
                ORDER BY id;
                """
            )
        ).fetchall()

    print(f"Chunks found: {len(rows)}")

    if not rows:
        print("No document chunks found. Run `python -m scripts.ingest_rag_docs` first.")
        return

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Embedding model loaded.")

    texts = [row.text for row in rows]

    print("Generating embeddings...")
    embeddings = model.encode(texts, normalize_embeddings=True)
    print("Embeddings generated.")

    print("Saving embeddings to database...")
    with engine.begin() as connection:
        for row, embedding in zip(rows, embeddings, strict=True):
            embedding_values = "[" + ",".join(str(float(value)) for value in embedding.tolist()) + "]"

            connection.execute(
                text(
                    """
                    UPDATE document_chunks
                    SET embedding = CAST(:embedding AS vector)
                    WHERE id = :chunk_id;
                    """
                ),
                {
                    "embedding": embedding_values,
                    "chunk_id": row.id,
                },
            )

    print("RAG chunk embeddings generated successfully.")
    print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
    print(f"Chunks embedded: {len(rows)}")
    print("Embedding dimension: 384")


if __name__ == "__main__":
    embed_rag_chunks()