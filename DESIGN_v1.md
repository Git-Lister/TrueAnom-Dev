1. Overview
Name: True Anomaly
Goal: A leak/archive explorer that matches existing Epstein search engines on search/graph quality, then adds automated anomaly/burst detection and logistics‑centric analysis, with a path to generalise to other leaks.

2. Scope (v1)
Ingest and normalise a contained subset of Epstein files (e.g. selected DOJ/Sifter subset with flight logs and emails).

Provide:

Full‑text and metadata search over that subset.

Entity extraction and co‑occurrence graph.

Document and entity pages with links back to original pages.

Ship one flagship analytic feature:

“Anomaly & burst timelines” for communications/logistics (spikes and gaps over time).

Provide a basic logistics mode for flights/log‑like docs (itineraries, routes).

3. Non‑Goals (v1)
No full Epstein corpus; v1 is subset‑only.

No polished user accounts or recommendation engine; v1 may have simple bookmarks only.

No fully generic leak‑agnostic config system; v1 is Epstein‑tuned but designed to generalise.

No advanced redaction handling or legal workflows beyond respectful use of public docs.

4. High‑Level Architecture
Core components:

Backend API (Python/FastAPI)

Exposes REST/JSON endpoints for search, documents, entities, anomalies, and graph queries.

Talks to Postgres, OpenSearch, vector store, and Neo4j.

Data stores

Postgres: canonical store for documents, entities, relationships, events (schema from previous step).

Object storage (local data/raw/ for dev): raw PDFs/TIFFs and page images.

OpenSearch: full‑text and filterable search index.

pgvector in Postgres for embeddings (RAG support).
​

Neo4j: co‑occurrence and relationship graph.

Ingestion & enrichment

Python worker(s) (ingestion/) for:

File discovery, OCR/layout extraction (via MinerU or similar).

Entity extraction and canonicalisation.

Relationship extraction (emails/logs).

Co‑occurrence matrix and graph updates.
​

Analytics modules

Anomaly/burst detector over time‑series of events and relationships (per entity or pair).

Logistics module for flight/log‑like events (routes, itineraries).

Frontend (later)

Simple React/Next.js app for v1: search, document view, entity view, anomaly/logistics views.

5. Data Model (v1 subset)
Core tables in Postgres:

sources, documents, pages, entities, entity_mentions, relationships, events (as previously defined).

Graph projection in Neo4j:

Nodes: Entity, Document.

Edges: MENTIONED_IN, CO_OCCURS_WITH, RELATES.

6. v1 Feature Checklist
Base capabilities

Ingest N sample documents (e.g. 500–2000) from chosen Epstein subset.

Run OCR/text extraction and populate documents and pages.

Run NER and populate entities and entity_mentions.

Populate relationships for:

Emails: sender/recipient edges.

Flight/log entries (if present): travels_with edges.

Build co‑occurrence weights and sync to Neo4j (CO_OCCURS_WITH).
​

Index documents in OpenSearch with keyword + metadata fields.

Create embeddings and store in pgvector; configure simple RAG Q&A endpoint.

Analytic capabilities (differentiators)

Implement burst detection:

For each entity pair (or entity vs “all”), compute time‑binned counts and z‑score/threshold anomalies; expose via /analytics/bursts.

Implement gap detection:

For selected sources (e.g. flight logs), detect unusually long intervals without events; expose via /analytics/gaps.

Implement basic logistics view:

/logistics/itinerary?entity_id=... returns ordered events (flights/logs) with origin/destination and timestamps.

API & UX

GET /search – keyword + filters (date, entity, type, source).

GET /documents/{id} – metadata, text snippet, pages, entities.

GET /entities/{id} – entity info, mention stats, related entities, docs.

GET /analytics/bursts, /analytics/gaps, /logistics/itinerary.

Minimal web UI for: search, document view, entity view, anomaly/logistics views.

7. Implementation Phases
Phase 0 – Repo & infra

Scaffold repo via project_init.py (see below), commit Docker compose, .env template.

Phase 1 – Ingestion & schema

Implement DB schema migrations.

Implement ingestion for one Epstein subset; verify a handful of docs end‑to‑end.

Phase 2 – Search & RAG

OpenSearch indexing + pgvector; simple RAG endpoint.

Phase 3 – Analytics (True Anomaly bits)

Burst and gap detection jobs + APIs.

Basic logistics itinerary view.

Phase 4 – Frontend

Minimal UI to exercise APIs and demonstrate value.