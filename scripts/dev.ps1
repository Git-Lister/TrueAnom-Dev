param(
    [string]$Task = "all"
)

$ErrorActionPreference = "Stop"

function Ensure-Infra {
    Write-Host "Starting infra (Postgres + OpenSearch + Neo4j)..." -ForegroundColor Cyan
    docker compose -f .\infra\docker-compose.yml up -d postgres opensearch neo4j
}

function Init-Db {
    Write-Host "Creating tables..." -ForegroundColor Cyan
    .\.venv\Scripts\python.exe -m backend.app.db.create_tables
}

function Ingest-Epstein {
    Write-Host "Ingesting Epstein subset..." -ForegroundColor Cyan
    .\.venv\Scripts\python.exe -m backend.app.ingestion.epstein_subset
}

function Index-Search {
    Write-Host "Indexing into OpenSearch..." -ForegroundColor Cyan
    .\.venv\Scripts\python.exe -m backend.app.ingestion.index_opensearch
}

function Run-Api {
    Write-Host "Starting API (Uvicorn)..." -ForegroundColor Cyan
    .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
}

switch ($Task) {
    "infra"   { Ensure-Infra }
    "db"      { Ensure-Infra; Init-Db }
    "ingest"  { Ensure-Infra; Ingest-Epstein }
    "index"   { Ensure-Infra; Index-Search }
    "api"     { Ensure-Infra; Run-Api }
    "all"     {
        Ensure-Infra
        Init-Db
        Ingest-Epstein
        Index-Search
        Run-Api
    }
    default   {
        Write-Host "Unknown task '$Task'. Use one of: infra, db, ingest, index, api, all." -ForegroundColor Red
        exit 1
    }
}
