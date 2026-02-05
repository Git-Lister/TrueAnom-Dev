#!/usr/bin/env python3
import os
from pathlib import Path
from textwrap import dedent

PROJECT_NAME = "true_anomaly"

ROOT_DIRS = [
    "backend",
    "backend/app",
    "backend/app/api",
    "backend/app/models",
    "backend/app/services",
    "backend/app/ingestion",
    "backend/app/analytics",
    "backend/app/db",
    "backend/app/config",
    "frontend",
    "frontend/src",
    "infra",
    "infra/db",
    "infra/search",
    "infra/graph",
    "data",
    "data/raw",
    "data/processed",
    "scripts",
]

def write_file(path: Path, content: str, overwrite=False):
    if path.exists() and not overwrite:
        return
    path.write_text(dedent(content).lstrip(), encoding="utf-8")

def main():
    root = Path.cwd()
    print(f"Initialising True Anomaly project in {root}")

    # Create directories
    for d in ROOT_DIRS:
        p = root / d
        p.mkdir(parents=True, exist_ok=True)

    # Top-level files
    write_file(root / "README.md", f"# {PROJECT_NAME}\n\nLeak/archive explorer – v1.\n")
    write_file(root / "DESIGN_v1.md", "# True Anomaly – v1 Design\n\n(See DESIGN_v1.md content).\n")
    write_file(root / ".gitignore", """
    __pycache__/
    *.pyc
    .env
    .DS_Store
    data/raw/
    data/processed/
    """)

    # Backend: basic FastAPI app skeleton
    write_file(root / "backend/app/main.py", """
    from fastapi import FastAPI

    app = FastAPI(title="True Anomaly API", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok"}
    """)

    # Backend: config placeholder
    write_file(root / "backend/app/config/settings.py", """
    from pydantic import BaseSettings

    class Settings(BaseSettings):
        app_name: str = "True Anomaly"
        postgres_dsn: str = "postgresql://true_anomaly:true_anomaly@localhost:5432/true_anomaly"
        opensearch_url: str = "http://localhost:9200"
        neo4j_url: str = "bolt://localhost:7687"
        neo4j_user: str = "neo4j"
        neo4j_password: str = "password"

        class Config:
            env_file = ".env"

    settings = Settings()
    """)

    # Backend: DB schema placeholder
    write_file(root / "backend/app/db/schema.py", """
    # Placeholder for SQLAlchemy models or Alembic migrations
    # Define: sources, documents, pages, entities, entity_mentions, relationships, events.
    """)

    # Backend: ingestion skeleton
    write_file(root / "backend/app/ingestion/epstein_subset.py", """
    # Ingestion pipeline for the initial Epstein subset.
    # Steps:
    # 1) Register source.
    # 2) Walk files in data/raw/epstein_subset.
    # 3) OCR/parse -> documents, pages.
    # 4) NER -> entities, entity_mentions.
    # 5) Relationships (emails/logs).
    # 6) Index into OpenSearch + pgvector.
    """)

    # Backend: analytics skeleton
    write_file(root / "backend/app/analytics/anomaly.py", """
    # Burst and gap detection over event/relationship time series.
    # Expose functions like:
    # - compute_bursts(entity_id, bucket='week')
    # - compute_bursts_pair(entity_a, entity_b, bucket='week')
    # - detect_gaps(source_id, threshold_days=...)
    """)

    # Backend: API routers placeholders
    write_file(root / "backend/app/api/__init__.py", "")
    write_file(root / "backend/app/api/routes.py", """
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
    """)

    # Infra: docker-compose placeholder
    write_file(root / "infra/docker-compose.yml", """
    version: "3.9"
    services:
      postgres:
        image: postgres:16
        environment:
          POSTGRES_DB: true_anomaly
          POSTGRES_USER: true_anomaly
          POSTGRES_PASSWORD: true_anomaly
        ports:
          - "5432:5432"
      opensearch:
        image: opensearchproject/opensearch:2.11.0
        environment:
          discovery.type: single-node
          OPENSEARCH_JAVA_OPTS: "-Xms512m -Xmx512m"
        ports:
          - "9200:9200"
      neo4j:
        image: neo4j:5
        environment:
          NEO4J_AUTH: neo4j/password
        ports:
          - "7474:7474"
          - "7687:7687"
    """)

    # Scripts: run backend
    write_file(root / "scripts/run_backend.sh", """
    #!/usr/bin/env bash
    uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
    """)

    print("Scaffold created. Next steps:")
    print("1) Create and activate a virtualenv.")
    print("2) Install FastAPI, Uvicorn, SQLAlchemy/ORM of choice, and search/graph clients.")
    print("3) Fill in DESIGN_v1.md with the full design document content.")
    print("4) Run: docker compose -f infra/docker-compose.yml up -d")

if __name__ == "__main__":
    main()
