import os
from pathlib import Path
from datetime import datetime

import fitz  # PyMuPDF
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


def extract_text_if_pdf(path: Path) -> str | None:
    """
    For now, only try to extract text from PDFs with embedded text.
    TIFF/JPEG/etc. will be handled later via OCR.
    """
    if path.suffix.lower() != ".pdf":
        return None
    try:
        doc = fitz.open(path)
        parts: list[str] = []
        for page in doc:
            parts.append(page.get_text())
        text = "\n".join(parts).strip()
        return text or None
    except Exception:
        # Swallow errors for now; later we can log these
        return None


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

                existing = (
                    db.query(Document)
                    .filter_by(raw_path=str(full_path))
                    .first()
                )
                if existing:
                    continue

                text = extract_text_if_pdf(full_path)

                doc = Document(
                    source_id=source.id,
                    external_id=fname,
                    doc_type="generic_pdf",
                    title=fname,
                    description=None,
                    ingest_time=datetime.utcnow(),  # TODO: switch to timezone-aware
                    text=text,
                    raw_path=str(full_path),
                    ocr_confidence=None,
                    is_searchable=bool(text),
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
