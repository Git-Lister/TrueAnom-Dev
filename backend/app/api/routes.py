from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.deps import get_db
from backend.app.db.schema import Document, Event
from backend.app.models.schemas import DocumentOut
from backend.app.analytics.anomaly import compute_bursts_for_pair


router = APIRouter()

@router.get("/documents/debug")
def list_docs_debug(db: Session = Depends(get_db)):
    docs = db.query(Document).limit(3).all()
    return [{"id": d.id, "raw_path": d.raw_path} for d in docs]

@router.get("/search")
def search(q: str = "", limit: int = 20):
    # TODO: hook OpenSearch later
    return {"results": []}


@router.get("/documents", response_model=List[DocumentOut])
def list_documents(limit: int = 50, db: Session = Depends(get_db)):
    docs = db.query(Document).limit(limit).all()
    return docs


@router.get("/documents/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).get(doc_id)
    if not doc:
        # in v1 we can just return 404 later; for now return empty-ish
        return DocumentOut(
            id=doc_id,
            source_id=0,
            external_id=None,
            doc_type=None,
            title=None,
            raw_path=None,
            ingest_time=None,
        )
    return doc

@router.get("/analytics/bursts")
def get_bursts(pair: str, bucket_days: int = 7, z_threshold: float = 1.5):
    bursts = compute_bursts_for_pair(pair=pair, bucket_days=bucket_days, z_threshold=z_threshold)
    return {"pair": pair, "bursts": bursts}

@router.get("/events")
def list_events(limit: int = 20, db: Session = Depends(get_db)):
    evs = db.query(Event).order_by(Event.event_time).limit(limit).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "event_time": e.event_time,
            "description": e.description,
            "meta_json": e.meta_json,
        }
        for e in evs
    ]
