# THE MENTALIST
### Criminal Intelligence & Network Analysis System

> B.Tech AI/ML Semester Integrated Project  
> AI-Driven Criminal Network Intelligence Through Multimodal Knowledge Graphs

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- Or: Python 3.11+, Node 18+, PostgreSQL 15, Neo4j 5

### One-command start (Docker)

```bash
cd PBL_proto
docker-compose up -d
```

Wait ~15 seconds for Neo4j to initialise, then open:

| Service | URL |
|---|---|
| **THE MENTALIST app** | http://localhost:3000 |
| Backend API docs | http://localhost:8000/api/docs |
| Neo4j browser | http://localhost:7474 |

No login required — the app auto-authenticates with the demo investigator account.

### Load demo data (first time only)

```bash
# 1. Generate synthetic case files
python3 data/synthetic/generate_cases.py

# 2. Load 4 synthetic investigation cases
python3 scripts/load_synthetic_data.py

# 3. Seed 4 historical reference cases (JFK, Watergate, Unabomber, Golden State Killer)
python3 scripts/seed_historical_cases.py

# 4. Write knowledge graphs directly to Neo4j (works without an LLM API key)
pip install neo4j requests   # if not already installed
python3 scripts/seed_graphs_direct.py
```

---

## Manual Start (without Docker)

Run each in a separate terminal.

### Terminal 1 — Databases

```bash
cd PBL_proto
docker-compose up -d postgres neo4j
```

### Terminal 2 — Backend

```bash
cd PBL_proto/backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env         # then edit .env with your passwords
uvicorn app.main:app --reload --port 8000
```

### Terminal 3 — Frontend

```bash
cd PBL_proto/frontend
npm install
npm run dev
```

App available at **http://localhost:3000**

### Stop everything

```bash
docker-compose down        # stop containers, keep data
docker-compose down -v     # stop containers AND delete all data
```

---

## Environment Configuration

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_PASSWORD` | `crimenet_dev_2026` | PostgreSQL password |
| `NEO4J_PASSWORD` | `crimenet_neo4j_2026` | Neo4j password |
| `SECRET_KEY` | `dev_secret_key_…` | JWT signing key — **change in production** |
| `LLM_PROVIDER` | `mock` | `openai` / `anthropic` / `mock` |
| `OPENAI_API_KEY` | _(empty)_ | Required for real text extraction |
| `ANTHROPIC_API_KEY` | _(empty)_ | Alternative LLM provider |

> **Never commit `.env` to source control.**

### Enable real AI extraction

Set in `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

Then reprocess any failed documents via the Evidence Files tab or:
```bash
# Reprocess all failed docs via the API
python3 - <<'EOF'
import requests
BASE = "http://localhost:8000/api"
token = requests.post(f"{BASE}/auth/login",
    json={"email":"demo@crimenet.local","password":"crimenet2026"}).json()["access_token"]
h = {"Authorization": f"Bearer {token}"}
for c in requests.get(f"{BASE}/cases", headers=h).json()["cases"]:
    for d in requests.get(f"{BASE}/cases/{c['id']}/documents", headers=h).json():
        if d["processing_status"] == "FAILED":
            requests.post(f"{BASE}/cases/{c['id']}/reprocess/{d['id']}", headers=h)
            print(f"Reprocessing: {d['original_filename']}")
EOF
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         THE MENTALIST  (React + TypeScript)          │
│  Dashboard │ Case Library │ Investigation Board       │
│  Timeline  │ Evidence     │ Intelligence AI           │
└─────────────────────┬───────────────────────────────┘
                      │ REST API (JSON)
┌─────────────────────▼───────────────────────────────┐
│            FastAPI Backend  (Python 3.11)            │
│                                                       │
│  /auth      JWT authentication + bcrypt hashing      │
│  /cases     Case management + audit logging          │
│  /documents Upload + async processing pipeline      │
│  /graph     Neo4j query layer (all parameterised)    │
│  /investigate  AI assistant (safe Cypher templates)  │
└──────┬──────────────────────────────┬───────────────┘
       │                              │
┌──────▼──────┐                ┌──────▼──────────────┐
│ PostgreSQL  │                │       Neo4j          │
│             │                │                      │
│ users       │                │  (:Person)           │
│ cases       │                │  (:Organization)     │
│ case_members│                │  (:Location)         │
│ documents   │                │  (:Phone)            │
│ audit_logs  │                │  (:BankAccount)      │
│ proc_jobs   │                │  (:Transaction)      │
└─────────────┘                │  (:Event)            │
                                │  (:Vehicle)          │
                                │  (:Document)         │
                                │  relationships with  │
                                │  confidence +        │
                                │  evidence provenance │
                                └──────────────────────┘
```

---

## Document Processing Pipeline

```
UPLOAD (PDF / TXT / DOCX / CSV / JSON)
    │
    ▼
FILE PARSER
    │ TXT/PDF/DOCX → raw text
    │ CSV/JSON     → detect schema (CDR? Transactions? Generic?)
    ▼
EXTRACTION
    │ CDR schema        → deterministic: Phone nodes + CALLED edges
    │ Transaction schema→ deterministic: BankAccount + Transaction nodes
    │ Text / Generic    → LLM extraction (requires API key)
    ▼
ENTITY RESOLUTION
    │ Normalise names + phone numbers
    │ Deduplicate within batch and against existing Neo4j nodes
    ▼
NEO4J WRITE
    │ MERGE nodes (no duplicates)
    │ MERGE relationships with confidence + evidence_text
    ▼
PROCESSING JOB STATUS: PROCESSED ✓
```

---

## Demo Cases

### Synthetic Investigation Cases
| Case Number | Title | Priority | Documents |
|---|---|---|---|
| CASE-2026-CBB2F6DB | Organized Financial Fraud Network | HIGH | Narrative + transactions.csv |
| CASE-2026-DB3481A5 | Vehicle Theft Ring — Delhi NCR | MEDIUM | Narrative |
| CASE-2026-9B75C9F3 | Kidnapping for Ransom — Bangalore | CRITICAL | Narrative |
| CASE-2026-73C07678 | CryptoMax Investment Fraud | HIGH | Narrative + cdr.csv |

> All names, phone numbers, and account numbers in synthetic cases are entirely fictional.

### Historical Reference Cases
Sourced from public records — Warren Commission (1964), Senate Watergate Committee (1974), FBI UNABOM case files, California DOJ press releases (2018).

| Case | Nodes | Edges | Status | Source |
|---|---|---|---|---|
| Assassination of President John F. Kennedy | 13 | 6 | Closed | Warren Commission Report (1964) |
| Watergate: Presidential Obstruction of Justice | 15 | 8 | Closed | Senate Watergate Committee Report (1974) |
| UNABOM: Kaczynski Mail-Bomb Campaign | 10 | 5 | Closed | FBI UNABOM files; U.S. v. Kaczynski (1998) |
| Golden State Killer — East Area Rapist | 13 | 7 | Closed | California DOJ press releases (2018, 2020) |

> These cases are tagged `HISTORICAL_REFERENCE` and are for educational/demonstration purposes only. All facts are sourced from public records. Nothing is fabricated.

---

## Project Structure

```
PBL_proto/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Settings from .env
│   │   ├── api/
│   │   │   ├── auth.py                # Register, login, me, logout
│   │   │   ├── cases.py               # Case CRUD + audit
│   │   │   ├── documents.py           # Upload, process, job status
│   │   │   ├── graph.py               # Neo4j query endpoints
│   │   │   └── investigation.py       # AI assistant
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   ├── schemas/                   # Pydantic response schemas
│   │   ├── services/
│   │   │   ├── auth/                  # JWT + bcrypt
│   │   │   ├── extraction/            # LLM + deterministic extractors
│   │   │   ├── entity_resolution/     # Deduplication
│   │   │   ├── graph/                 # All Neo4j operations
│   │   │   └── ingestion/             # File parser + pipeline orchestrator
│   │   ├── ai/
│   │   │   ├── provider.py            # OpenAI / Anthropic / Mock abstraction
│   │   │   ├── extraction.py          # System prompts
│   │   │   └── reasoning.py           # AI assistant query templates
│   │   └── db/
│   │       ├── postgres.py            # SQLAlchemy async engine
│   │       └── neo4j.py               # Neo4j driver + constraints
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── App.tsx                    # Router + LoadingScreen
│       ├── layouts/AppLayout.tsx      # Sidebar + navigation
│       ├── pages/
│       │   ├── DashboardPage.tsx      # Intelligence dashboard
│       │   ├── CasesPage.tsx          # Case library table
│       │   └── CaseWorkspacePage.tsx  # 6-tab investigation workspace
│       ├── components/
│       │   ├── LoadingScreen.tsx      # Red John boot animation
│       │   └── case/
│       │       ├── CaseOverviewTab.tsx
│       │       ├── CaseGraphTab.tsx   # Investigation board
│       │       ├── CaseEntitiesTab.tsx
│       │       ├── CaseTimelineTab.tsx
│       │       ├── CaseDocumentsTab.tsx
│       │       └── CaseAssistantTab.tsx
│       ├── services/api.ts            # All API calls + auto-auth
│       └── types/index.ts             # TypeScript domain types
│
├── data/
│   └── synthetic/
│       ├── generate_cases.py          # Generate synthetic case files
│       └── cases/                     # Generated case files (txt + csv)
│
├── scripts/
│   ├── load_synthetic_data.py         # Load synthetic cases via API
│   ├── seed_historical_cases.py       # Seed historical cases (idempotent)
│   └── seed_graphs_direct.py          # Write graphs to Neo4j directly
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Current user |
| GET | `/api/cases` | List cases |
| POST | `/api/cases` | Create case |
| GET | `/api/cases/{id}` | Get case |
| PUT | `/api/cases/{id}` | Update case |
| GET | `/api/cases/{id}/audit` | Audit log |
| POST | `/api/cases/{id}/documents` | Upload document |
| GET | `/api/cases/{id}/documents` | List documents |
| GET | `/api/cases/{id}/jobs/{job_id}` | Processing job status |
| POST | `/api/cases/{id}/reprocess/{doc_id}` | Retry failed doc |
| GET | `/api/cases/{id}/graph` | Full knowledge graph |
| GET | `/api/cases/{id}/graph/node/{node_id}` | Node detail + connections |
| GET | `/api/cases/{id}/graph/path` | Shortest path between two nodes |
| GET | `/api/cases/{id}/graph/search` | Entity search |
| GET | `/api/cases/{id}/graph/analytics/centrality` | Degree centrality |
| GET | `/api/cases/{id}/entities` | Entities (filterable by type) |
| GET | `/api/cases/{id}/timeline` | Extracted events |
| POST | `/api/cases/{id}/investigate` | AI assistant query |

Full interactive docs: **http://localhost:8000/api/docs**

---

## Design System

The visual identity is inspired by classic 2000s crime investigation aesthetics.

| Token | Value | Use |
|---|---|---|
| `espresso` | `#211A17` | Body background |
| `mahogany` | `#2C1F1A` | Card surface |
| `walnut` | `#352720` | Sidebar, overlays |
| `burgundy` | `#7A2D35` | Primary accent, active state |
| `cream` | `#E9DFC9` | Primary text |
| `parchment` | `#D7C7A8` | Secondary text |
| `sepia` | `#AA9070` | Muted/tertiary text |
| `brass` | `#AA9164` | Icons, mono data |

Fonts: **Playfair Display** (headings) · **EB Garamond** (body italic) · **IBM Plex Mono** (data/IDs)

---

## Known Limitations

- **Text extraction requires an LLM API key.** Without `OPENAI_API_KEY`, text documents process but extract no entities. Structured CSVs (CDR, transactions) always work deterministically.
- **Neo4j GDS plugin** is listed in docker-compose but betweenness/community detection algorithms are not currently called. Degree centrality uses basic Cypher.
- **Single-user demo mode.** Auth works but the UI runs as a single auto-authenticated demo account. Multi-user flows (invite member, access control UI) are implemented in the backend but not exposed in the frontend.
- **No file preview.** Uploaded documents cannot be read back through the UI — only processed.
- **Planned nav items** (Persons of Interest, Knowledge Graphs, Evidence Repository, Reports, Data Sources) show as "soon" in the sidebar. The underlying API exists for most of these; they need dedicated pages.

---

## Recommended Next Steps

1. **Enable OpenAI** — set `OPENAI_API_KEY` and reprocess the narrative text files to populate full entity graphs from all cases
2. **Add Wikidata connector** — enrich historical entities with structured data via SPARQL
3. **Build Persons of Interest page** — dedicated cross-case person browser
4. **Add manual relationship editor** — investigators should be able to add/edit relationships with notes
5. **Export to PDF** — case summary + graph screenshot export for reports
6. **Add spaCy NER** — optional fallback extraction without an LLM (once spaCy wheels for Python 3.14 are available)

---

## Academic Notes

This project is a B.Tech AI/ML Semester Integrated Project demonstrating:
- Knowledge graph construction from unstructured documents
- Entity extraction and resolution pipelines
- Neo4j graph database integration
- LLM-assisted investigation with evidence provenance
- Full-stack TypeScript + Python architecture
- Containerised development environment

All synthetic case data is fictional. Historical reference cases use only publicly available information from official government sources and are clearly labelled as educational demonstrations.
