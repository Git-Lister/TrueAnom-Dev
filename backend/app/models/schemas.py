from datetime import datetime
from pydantic import BaseModel

class DocumentOut(BaseModel):
    id: int
    source_id: int
    external_id: str | None = None
    doc_type: str | None = None
    title: str | None = None
    raw_path: str | None = None
    ingest_time: datetime | None = None

    class Config:
        from_attributes = True  # orm_mode in Pydantic v1
