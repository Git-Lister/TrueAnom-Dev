# Getting Started

This guide covers how to run the TrueAnom backend locally for development and experiments.

## 1. Prerequisites

- Docker (Desktop or equivalent).
- Python 3.12.
- A clone of this repo, with a local Epstein sA focused setup + commands doc:

text
# Getting Started

This guide covers how to run the TrueAnom backend locally for development and experiments.

## 1. Prerequisites

- Docker (Desktop or equivalent).
- Python 3.12.
- A clone of this repo, with a local Epstein subset under:

  ```text
  data/raw/epstein_subset/DataSet 1/DataSet 1/VOL00001/...
2. Python environment
From repo root:

powershell
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
3. Start infrastructure (Postgres + OpenSearch + Neo4j)
powershell
cd "C:\path\to\TrueAnom-Dev"

docker compose -f .\infra\docker-compose.yml up -d postgres opensearch neo4j
Check:

powershell
docker ps
You should see:

Postgres: 0.0.0.0:55432->5432/tcp

OpenSearch: 0.0.0.0:9200->9200/tcp

4. Initialise database and ingest subset
From repo root, with the venv active:

powershell
# 1) Create tables
.\.venv\Scripts\python.exe -m backend.app.db.create_tables

# 2) Ingest local Epstein subset
.\.venv\Scripts\python.exe -m backend.app.ingestion.epstein_subset

# 3) Index searchable documents into OpenSearch
.\.venv\Scripts\python.exe -m backend.app.ingestion.index_opensearch

# 4) Seed synthetic events for burst detection demo
.\.venv\Scripts\python.exe -m backend.app.analytics.event_test_data
5. Run the API
powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
Quick checks
From another terminal (or browser):

powershell
curl http://localhost:8000/health
curl "http://localhost:8000/api/documents?limit=5"
curl "http://localhost:8000/api/events?limit=10"
curl "http://localhost:8000/api/analytics/bursts?pair=A-B&bucket_days=7"
curl "http://localhost:8000/api/search?q=Epstein&limit=5"
health should return {"status":"ok"}.

documents should show rows pointing into data/raw/epstein_subset/....

events should show baseline and burst A‑B email events.

analytics/bursts should show at least one burst bucket for A-B.

search may often return an empty result set at this stage, since many docs are image‑only and not yet OCR’d.

6. Optional: dev helper script (Windows)
A thin convenience wrapper lives at scripts/dev.ps1:

powershell
# Start infra only
.\scripts\dev.ps1 -Task infra

# Initialise DB (tables) after infra is up
.\scripts\dev.ps1 -Task db

# Ingest subset and index
.\scripts\dev.ps1 -Task ingest
.\scripts\dev.ps1 -Task index

# Run API
.\scripts\dev.ps1 -Task api

# Or full flow (infra + db + ingest + index + api)
.\scripts\dev.ps1 -Task all
You can always fall back to the explicit Python commands above; the script just ties them together.

7. Notes on data and security
This repo expects a local copy of a small DOJ subset for development; paths and content are not committed.

OpenSearch is run with DISABLE_SECURITY_PLUGIN: true in infra/docker-compose.yml for local convenience.

Do not reuse this configuration as‑is in any exposed environment.

text

***

## 3. docs/PROJECT_NOTES.md (lessons, world model, chat)

This is where you can “pour” our debugging history, patterns, and your mental model. A suggested outline:

```markdown
# Project Notes

This document captures working notes, decisions, and lessons learned while developing the TrueAnom prototype.

## 1. High‑level intent

- Model the Epstein corpus as:
  - Documents → Pages → Entities → Relationships → Events.
- Use events (and their meta) to compute:
  - Bursts of activity (per dyad, per asset, per location).
  - Gaps (expected interactions that go quiet).
- Provide:
  - A stable backend.
  - A thin analytics layer.
  - A surface that can later be driven by LLMs/RAG.

## 2. Key patterns and lessons from early dev

### 2.1. Docker Postgres vs host Postgres

- Problem: repeated `password authentication failed` on `localhost:5432` despite correct Docker env.
- Root cause: corporate Postgres service also listening on `localhost:5432`; app was talking to **host** Postgres, not Docker.
- Fix:
  - Expose Docker Postgres on a different host port: `55432:5432`.
  - Set DSN to: `postgresql://true_anomaly:true_anomaly@localhost:55432/true_anomaly`.
  - Add a debug print in `SessionLocal` to show the active DSN.
- Pattern: if Postgres works **inside container** but fails from host:
  - Assume port collision / wrong target.
  - Change host port and DSN first.

### 2.2. PowerShell quirks

- Execution policy blocks `Activate.ps1` → use `activate.bat` or explicit `python.exe` path instead.
- Quoting:
  - `.\.venv\Scripts\python.exe -m backend.app.db.create_tables` is correct.
  - `" .\.venv\Scripts\python.exe" -m` with quotes in the wrong place leads to “Unexpected token '-m'”.

### 2.3. WatchFiles + reload noise

- Uvicorn’s `--reload` combined with frequent edits leads to:
  - Multiple “Detected changes, reloading…” messages.
  - Occasional KeyboardInterrupt traces.
- This is benign for dev; reload restarts the worker process.

## 3. Design doc → implementation mapping

- v1 goals largely achieved; see README for summary.
- Intentional gaps:
  - Real flight logs ingestion:
    - `VOL00001.DAT` is a Bates index, not a flight manifest.
    - Flight/event ingestion is postponed to v1.1 with a real structured source (CSV or equivalent).
  - Entities/relationships:
    - Schema present but not populated; current events encode pairs in `meta_json`.

## 4. Future directions

- Bring in a **structured flight manifest** (CSV) as first real event source.
- Add OCR for image‑only pages, feeding `Page.text` and `Document.text`.
- Implement basic NER over text.
- Start populating `entities`, `entity_mentions`, `relationships` and explore Neo4j use.

## 5. Chat + spaces

- This project is being co‑developed with AI assistance.
- To keep context portable:
  - Key decisions and patterns from chat are mirrored here.
  - A separate “Space” can track ongoing design discussions and experiments beyond this repo.
ubset under:

  ```text
  data/raw/epstein_subset/DataSet 1/DataSet 1/VOL00001/...
