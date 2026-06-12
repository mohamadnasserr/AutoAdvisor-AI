from pathlib import Path

from backend.app.db.database import SessionLocal
from backend.app.models.db_models import Document, DocumentChunk


DOCS_DIR = Path("data/rag_docs")
DEFAULT_CATEGORY = "car_buying_guide"


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 120) -> list[str]:
    clean_text = " ".join(text.split())

    if len(clean_text) <= chunk_size:
        return [clean_text]

    chunks = []
    start = 0

    while start < len(clean_text):
        end = start + chunk_size
        chunk = clean_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(clean_text):
            break

        start = end - overlap

    return chunks


def ingest_rag_docs() -> None:
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"RAG docs directory not found: {DOCS_DIR}")

    markdown_files = sorted(DOCS_DIR.glob("*.md"))

    if not markdown_files:
        raise FileNotFoundError(f"No markdown files found in: {DOCS_DIR}")

    db = SessionLocal()

    try:
        inserted_docs = 0
        inserted_chunks = 0

        for file_path in markdown_files:
            source_url = f"local://rag_docs/{file_path.name}"
            title = file_path.stem.replace("_", " ").title()
            raw_text = file_path.read_text(encoding="utf-8")

            existing_doc = (
                db.query(Document)
                .filter(Document.url == source_url)
                .first()
            )

            if existing_doc:
                db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == existing_doc.id
                ).delete()

                existing_doc.title = title
                existing_doc.category = DEFAULT_CATEGORY
                existing_doc.raw_text = raw_text
                document = existing_doc
            else:
                document = Document(
                    title=title,
                    url=source_url,
                    category=DEFAULT_CATEGORY,
                    raw_text=raw_text,
                )
                db.add(document)
                db.flush()
                inserted_docs += 1

            chunks = chunk_text(raw_text)

            for index, chunk in enumerate(chunks):
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        text=chunk,
                        category=DEFAULT_CATEGORY,
                        source_url=source_url,
                    )
                )
                inserted_chunks += 1

        db.commit()

        print("RAG documents ingested successfully.")
        print(f"Markdown files found: {len(markdown_files)}")
        print(f"New documents inserted: {inserted_docs}")
        print(f"Chunks inserted/replaced: {inserted_chunks}")

    finally:
        db.close()


if __name__ == "__main__":
    ingest_rag_docs()