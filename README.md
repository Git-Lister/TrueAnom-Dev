# TrueAnom – AI‑Empowered Epstein Database

TrueAnom is an AI‑ready backend for exploring the DOJ Epstein files as a **dynamic network of people, assets, and places**.  
It ingests document subsets into Postgres and OpenSearch, then runs **burst detection** over events and relationships to surface anomalous patterns in time.

This repo is a v1 prototype of that idea, focused on:

- A small Epstein subset (local DOJ volume) as a dev testbed.
- A clean, extensible schema for documents, entities, relationships, and events.
- A minimal analytics loop: ingest → search → events → burst detection, exposed via a FastAPI backend.

For detailed setup instructions, see [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).  
For design notes, assumptions, and lessons learned, see [docs/PROJECT_NOTES.md](docs/PROJECT_NOTES.md).

---

## Architecture overview

**Services**

- FastAPI backend (local):
  - `backend.app.main:app`
  - Endpoints under `/api`:
    - Documents, snippets, search
    - Events
    - Analytics (burst detection)

- Postgres 16 (Docker, `localhost:55432`)
  - Canonical store for sources, documents, pages, entities, relationships, events.

- OpenSearch 2.11 (Docker, `localhost:9200`)
  - Full‑text index (`epstein_docs_v1`) over searchable documents.

- Neo4j 5 (Docker, `localhost:7474/7687`)
  - Reserved for graph analytics; schema is aligned but ingestion not yet using Neo4j.

**High‑level data flow**

1. **Ingestion** – `backend.app.ingestion.epstein_subset`
   - Walks `data/raw/epstein_subset/...` (subset of DOJ Data Set 1).
   - Creates `Source` + `Document` rows.
   - Extracts text from PDFs (PyMuPDF) when possible.
   - Marks `is_searchable=True` where text exists.

2. **Search indexing** – `backend.app.ingestion.index_opensearch`
   - Indexes searchable documents into OpenSearch (`epstein_docs_v1`).
   - Supports simple keyword search over `title` and `text`.

3. **Events & analytics**
   - `events` table stores time‑stamped events with a flexible `meta_json` payload.
   - Synthetic “A‑B” email events seeded by `backend.app.analytics.event_test_data`.
   - Burst detection in `backend.app.analytics.anomaly`:
     - Buckets events in time, computes mean/std, flags high‑activity buckets.
   - Exposed via `GET /api/analytics/bursts`.

4. **Bates groundwork** – `backend.app.ingestion.flight_logs_v1`
   - Parses `VOL00001.DAT` (Bates index) to understand load‑file structure.
   - Attempts initial `Bates → Page` mapping (currently a stub; see limitations below).

---

## Schema (short summary)

Core tables (in `backend.app/db/schema.py`):

- `sources` – data source/custodian metadata.
- `documents` – logical documents with paths, text, and ingestion times.
- `pages` – per‑page representation (image path, optional text, optional Bates ID).
- `entities` – people, assets, locations, etc.
- `entity_mentions` – links entities to documents/pages and spans in text.
- `relationships` – explicit ties between entities, grounded in a document/time.
- `events` – time‑stamped events (emails, flights, meetings, etc.), with `meta_json`.

At v1:

- `sources`, `documents`, and `events` are actively used.  
- `pages`, `entities`, `entity_mentions`, `relationships` are structurally defined and reserved for v1.1+ when real entity/relationship extraction is wired in.

---

## API surface (v1)

Mounted under `/` and `/api`:

- `GET /health` – basic health check.
- `GET /api/documents` – list documents (id, source_id, external_id, title, raw_path, ingest_time).
- `GET /api/documents/{id}` – get a document.
- `GET /api/documents/{id}/snippet` – first N characters of document text (where available).
- `GET /api/events` – list events (currently synthetic A‑B email events).
- `GET /api/search` – keyword search over OpenSearch.
- `GET /api/analytics/bursts` – burst detection over `events` filtered by pair.

Contract and implementation details are in [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) and the corresponding modules under `backend/app`.

---

## Status vs original design

Aligned with the v1 design:

- ✅ Base stack: Postgres + FastAPI + OpenSearch, with a clean schema.
- ✅ Ingestion for a local DOJ subset, including basic PDF text extraction.
- ✅ Search index over ingested text.
- ✅ Event schema and synthetic burst detection, exposed via API.

Intentionally deferred for v1.1:

- 🔜 Real flight/log ingestion (using structured manifests / logs rather than Bates indexes).
- 🔜 Entity and relationship extraction from text + logs into `entities`, `entity_mentions`, `relationships`.
- 🔜 Neo4j integration for graph‑level analytics.

Limitations and future work are discussed in [docs/PROJECT_NOTES.md](docs/PROJECT_NOTES.md).
