from fastapi import APIRouter

router = APIRouter()

@router.get("/search")
def search(q: str = "", limit: int = 20):
    # TODO: call OpenSearch + pgvector
    return {"results": []}

@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    # TODO: fetch from Postgres
    return {"id": doc_id}

@router.get("/entities/{entity_id}")
def get_entity(entity_id: str):
    # TODO: fetch from Postgres + Neo4j
    return {"id": entity_id}

@router.get("/analytics/bursts")
def get_bursts(entity_id: str, bucket: str = "week"):
    # TODO: call anomaly module
    return {"entity_id": entity_id, "bucket": bucket, "bursts": []}
