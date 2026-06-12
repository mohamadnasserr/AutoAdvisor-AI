from sqlalchemy import text

from backend.app.db.database import engine


def upgrade_rag_pgvector() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        connection.execute(
            text(
                """
                ALTER TABLE document_chunks
                ADD COLUMN IF NOT EXISTS embedding vector(384);
                """
            )
        )

    print("RAG pgvector upgrade completed successfully.")
    print("Ensured extension: vector")
    print("Ensured column: document_chunks.embedding vector(384)")


if __name__ == "__main__":
    upgrade_rag_pgvector()