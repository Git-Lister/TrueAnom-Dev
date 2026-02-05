import os
from pathlib import Path
from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal, engine
from backend.app.db.schema import Base, Source, Document

EPSTEIN_SUBSET_DIR = Path("data/raw/epstein_subset")


def get_or_create_source(db: Session) -> Source:
    name = "Epstein – Local Subset"
    src = db.query(Source).filter_by(name=name).first()
    if src:
        return src
    src = Source(
        name=name,
        kind="local_subset",
        url=None,
        notes="Local test subset of Epstein files for True Anomaly v1.",
    )
    db.add(src)
    db.commit()
    db.refresh(src)
    return src


def ingest_epstein_subset():
    if not EPSTEIN_SUBSET_DIR.exists():
        raise RuntimeError(f"Directory not found: {EPSTEIN_SUBSET_DIR}")

    db = SessionLocal()
    try:
        source = get_or_create_source(db)

        for root, _, files in os.walk(EPSTEIN_SUBSET_DIR):
            for fname in files:
                if not fname.lower().endswith((".pdf", ".tif", ".tiff", ".jpg", ".jpeg", ".png")):
                    continue

                full_path = Path(root) / fname
                # Check if we already have a Document with this path
                existing = (
                    db.query(Document)
                    .filter_by(raw_path=str(full_path))
                    .first()
                )
                if existing:
                    continue

                doc = Document(
                    source_id=source.id,
                    external_id=fname,
                    doc_type="generic_pdf",
                    title=fname,
                    description=None,
                    ingest_time=datetime.utcnow(),
                    text=None,  # to be filled by OCR/parse later
                    raw_path=str(full_path),
                    ocr_confidence=None,
                    is_searchable=False,  # becomes True after OCR
                    meta_json=None,
                )
                db.add(doc)

        db.commit()
    finally:
        db.close()


def main():
    # Ensure tables exist (safe if already created)
    Base.metadata.create_all(bind=engine)
    ingest_epstein_subset()
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
